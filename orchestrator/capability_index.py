"""Capability indexing for dynamic specialist selection in swarm orchestration."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Collection, Dict, List, Optional, Tuple

import yaml

from tools.engine.roster import iter_specialist_records


@dataclass
class SpecialistMetadata:
    """Metadata about a specialist extracted from YAML."""

    slug: str
    file_path: Path
    role: str
    capabilities: List[str]  # Capability names from core_capabilities
    expertise: List[str]  # From core_identity.expertise
    department: str

    def __post_init__(self):
        """Normalize all text fields to lowercase for matching."""
        self.capabilities = [c.lower() for c in self.capabilities]
        self.expertise = [e.lower() for e in self.expertise]


@dataclass
class CapabilityMatch:
    """A scored match between a required capability and a specialist."""

    specialist_slug: str
    score: float
    match_type: str  # 'exact', 'fuzzy', 'expertise', 'department'
    matched_on: Optional[str] = None  # What capability/expertise triggered the match


class CapabilityIndex:
    """Index of all specialists and their capabilities for dynamic matching."""

    def __init__(
        self,
        staff_dir: Path,
        *,
        allowed_tiers: Collection[str] | None = None,
    ):
        """
        Initialize the capability index by parsing all specialist YAMLs.

        Args:
            staff_dir: Path to the staff directory containing specialist YAMLs
            allowed_tiers: Optional roster tiers to index
        """
        self.staff_dir = staff_dir
        self.allowed_tiers = allowed_tiers
        self.specialists: Dict[str, SpecialistMetadata] = {}
        self.capability_map: Dict[str, List[str]] = {}  # capability → [slugs]
        self.expertise_map: Dict[str, List[str]] = {}  # expertise → [slugs]

        self._build_index()

    def _build_index(self) -> None:
        """Parse all YAML files and build the index."""
        if not self.staff_dir.exists():
            raise FileNotFoundError(f"Staff directory not found: {self.staff_dir}")

        for record in iter_specialist_records(self.staff_dir, tiers=self.allowed_tiers):
            try:
                metadata = self._parse_specialist_yaml(record.path, record.department)
                if metadata:
                    self.specialists[metadata.slug] = metadata
                    self._add_to_maps(metadata)
            except Exception as e:
                # Log but don't fail - continue indexing other specialists
                print(f"Warning: Failed to parse {record.path}: {e}")

    def _parse_specialist_yaml(self, yaml_file: Path, department: str) -> Optional[SpecialistMetadata]:
        """
        Parse a single specialist YAML file.

        Args:
            yaml_file: Path to the YAML file
            department: Department name (from directory)

        Returns:
            SpecialistMetadata or None if parsing fails
        """
        with open(yaml_file, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError:
                return None

        if not data:
            return None

        # Extract slug from filename
        slug = yaml_file.stem

        # Extract role from core_identity
        core_identity = data.get('core_identity', {})
        role = core_identity.get('role', 'Unknown')

        # Extract expertise from core_identity
        expertise = core_identity.get('expertise', [])
        if not isinstance(expertise, list):
            expertise = []

        # Extract capability names from core_capabilities
        core_capabilities = data.get('core_capabilities', [])
        capabilities = []

        if isinstance(core_capabilities, list):
            for cap in core_capabilities:
                if isinstance(cap, dict):
                    cap_name = cap.get('name', '')
                    if cap_name:
                        capabilities.append(cap_name)
                elif isinstance(cap, str):
                    # Some YAMLs might have simple string capabilities
                    capabilities.append(cap)

        return SpecialistMetadata(
            slug=slug,
            file_path=yaml_file,
            role=role,
            capabilities=capabilities,
            expertise=expertise,
            department=department,
        )

    def _add_to_maps(self, metadata: SpecialistMetadata) -> None:
        """Add specialist to capability and expertise reverse indexes."""
        # Add to capability map
        for capability in metadata.capabilities:
            if capability not in self.capability_map:
                self.capability_map[capability] = []
            self.capability_map[capability].append(metadata.slug)

        # Add to expertise map
        for exp in metadata.expertise:
            if exp not in self.expertise_map:
                self.expertise_map[exp] = []
            self.expertise_map[exp].append(metadata.slug)

    def match_specialists(
        self,
        required_capabilities: List[str],
        *,
        min_score: float = 0.3,
        max_results: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Match required capabilities to specialists with scoring.

        Args:
            required_capabilities: List of required capability descriptions
            min_score: Minimum score threshold (0.0-1.0)
            max_results: Maximum number of results to return

        Returns:
            List of (specialist_slug, score) tuples, sorted by score descending
        """
        # Normalize required capabilities
        required_capabilities = [c.lower().strip() for c in required_capabilities]

        # Accumulate scores for each specialist
        specialist_scores: Dict[str, float] = {}
        match_details: Dict[str, List[CapabilityMatch]] = {}

        for req_cap in required_capabilities:
            matches = self._match_single_capability(req_cap)

            for match in matches:
                slug = match.specialist_slug
                if slug not in specialist_scores:
                    specialist_scores[slug] = 0.0
                    match_details[slug] = []

                # Accumulate score (max of any match for this specialist)
                specialist_scores[slug] = max(specialist_scores[slug], match.score)
                match_details[slug].append(match)

        # Filter by min_score and sort
        results = [
            (slug, score)
            for slug, score in specialist_scores.items()
            if score >= min_score
        ]
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:max_results]

    def _match_single_capability(self, required_cap: str) -> List[CapabilityMatch]:
        """
        Match a single required capability against all specialists.

        Scoring:
        - 1.0: Exact match in capabilities
        - 0.8: Fuzzy match in capabilities (>0.8 similarity)
        - 0.5: Fuzzy match in capabilities (>0.6 similarity)
        - 0.4: Exact match in expertise
        - 0.3: Fuzzy match in expertise
        - 0.2: Department relevance heuristic

        Args:
            required_cap: A single required capability (normalized to lowercase)

        Returns:
            List of CapabilityMatch objects
        """
        matches: List[CapabilityMatch] = []

        # 1. Exact match in capability map
        if required_cap in self.capability_map:
            for slug in self.capability_map[required_cap]:
                matches.append(CapabilityMatch(
                    specialist_slug=slug,
                    score=1.0,
                    match_type='exact',
                    matched_on=required_cap,
                ))

        # 2. Fuzzy match in capabilities
        for capability, slugs in self.capability_map.items():
            similarity = self._string_similarity(required_cap, capability)

            if similarity > 0.8:
                for slug in slugs:
                    # Avoid duplicates from exact match
                    if not any(m.specialist_slug == slug and m.score >= 0.8 for m in matches):
                        matches.append(CapabilityMatch(
                            specialist_slug=slug,
                            score=0.8,
                            match_type='fuzzy',
                            matched_on=capability,
                        ))
            elif similarity > 0.6:
                for slug in slugs:
                    if not any(m.specialist_slug == slug and m.score >= 0.5 for m in matches):
                        matches.append(CapabilityMatch(
                            specialist_slug=slug,
                            score=0.5,
                            match_type='fuzzy',
                            matched_on=capability,
                        ))

        # 3. Exact match in expertise map
        if required_cap in self.expertise_map:
            for slug in self.expertise_map[required_cap]:
                if not any(m.specialist_slug == slug and m.score >= 0.4 for m in matches):
                    matches.append(CapabilityMatch(
                        specialist_slug=slug,
                        score=0.4,
                        match_type='expertise',
                        matched_on=required_cap,
                    ))

        # 4. Fuzzy match in expertise
        for expertise, slugs in self.expertise_map.items():
            similarity = self._string_similarity(required_cap, expertise)

            if similarity > 0.7:
                for slug in slugs:
                    if not any(m.specialist_slug == slug and m.score >= 0.3 for m in matches):
                        matches.append(CapabilityMatch(
                            specialist_slug=slug,
                            score=0.3,
                            match_type='expertise_fuzzy',
                            matched_on=expertise,
                        ))

        # 5. Department heuristic
        dept_matches = self._match_department_heuristic(required_cap)
        for slug in dept_matches:
            if not any(m.specialist_slug == slug for m in matches):
                matches.append(CapabilityMatch(
                    specialist_slug=slug,
                    score=0.2,
                    match_type='department',
                    matched_on=None,
                ))

        return matches

    def _string_similarity(self, a: str, b: str) -> float:
        """
        Calculate similarity between two strings using SequenceMatcher.

        Args:
            a: First string
            b: Second string

        Returns:
            Similarity score (0.0-1.0)
        """
        # Check for substring matches first (common pattern)
        if a in b or b in a:
            return 0.85

        # Use SequenceMatcher for fuzzy matching
        return SequenceMatcher(None, a, b).ratio()

    def _match_department_heuristic(self, required_cap: str) -> List[str]:
        """
        Match capability to department using heuristics.

        This is a fallback for when no capability/expertise matches.

        Args:
            required_cap: Required capability

        Returns:
            List of specialist slugs from relevant department
        """
        # Department keyword mapping
        dept_keywords = {
            'strategy': ['strategy', 'research', 'analysis', 'market', 'planning', 'data'],
            'producers': ['content', 'writing', 'copy', 'design', 'creative', 'narrative', 'video'],
            'commerce': ['seo', 'marketing', 'sales', 'conversion', 'growth', 'revenue', 'pricing'],
            'tech': ['technical', 'software', 'automation', 'development', 'engineering', 'code'],
            'health-lifestyle': ['health', 'wellness', 'habit', 'meditation', 'stoic', 'fitness'],
            'knowledge': ['legal', 'law', 'tax', 'finance', 'investment', 'accounting'],
        }

        # Find matching department
        for dept, keywords in dept_keywords.items():
            if any(keyword in required_cap for keyword in keywords):
                # Return all specialists from this department
                return [
                    slug for slug, meta in self.specialists.items()
                    if meta.department == dept
                ]

        return []

    def get_specialist_metadata(self, slug: str) -> Optional[SpecialistMetadata]:
        """Get metadata for a specific specialist."""
        return self.specialists.get(slug)

    def list_all_specialists(self) -> List[str]:
        """Get list of all specialist slugs."""
        return list(self.specialists.keys())

    def get_statistics(self) -> Dict[str, int]:
        """Get index statistics for debugging."""
        return {
            'total_specialists': len(self.specialists),
            'total_capabilities': len(self.capability_map),
            'total_expertise_areas': len(self.expertise_map),
            'departments': len(set(m.department for m in self.specialists.values())),
        }

"""Roster tiers for active, experimental, and archived specialists."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Collection, Dict, Literal

import yaml
from pydantic import BaseModel, Field, model_validator


RosterTier = Literal["active", "experimental", "archived"]
DEFAULT_ROSTER_CONFIG_PATH = Path(__file__).parents[2] / "config" / "specialist_roster.yaml"
DEFAULT_ACTIVE_TIERS: tuple[RosterTier, ...] = ("active",)
ALL_ROSTER_TIERS: tuple[RosterTier, ...] = ("active", "experimental", "archived")


class SpecialistRecord(BaseModel):
    """Resolved specialist metadata plus roster tier."""

    slug: str
    department: str
    path: Path
    tier: RosterTier


class RosterConfig(BaseModel):
    """Tier assignments for the specialist roster."""

    version: int = 1
    flagship_workflow: str = "planning-swarm"
    active: list[str] = Field(default_factory=list)
    experimental: list[str] = Field(default_factory=list)
    archived: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_assignments(self) -> "RosterConfig":
        """Ensure each specialist is assigned to exactly one tier."""
        seen: dict[str, str] = {}
        duplicates: list[str] = []

        for tier in ALL_ROSTER_TIERS:
            values = getattr(self, tier)
            normalized = [slug.strip() for slug in values if slug.strip()]
            setattr(self, tier, normalized)

            for slug in normalized:
                if slug in seen:
                    duplicates.append(slug)
                else:
                    seen[slug] = tier

        if duplicates:
            duplicate_list = ", ".join(sorted(set(duplicates)))
            raise ValueError(f"Specialists assigned to multiple tiers: {duplicate_list}")

        return self

    def tier_for_slug(self, slug: str) -> RosterTier:
        """Return the roster tier for a slug, defaulting to experimental."""
        for tier in ALL_ROSTER_TIERS:
            if slug in getattr(self, tier):
                return tier
        return "experimental"


def load_roster_config(config_path: Path | None = None) -> RosterConfig:
    """Load the roster configuration from disk."""
    path = config_path or DEFAULT_ROSTER_CONFIG_PATH
    if not path.exists():
        return RosterConfig()

    with open(path, encoding="utf-8") as f:
        payload = yaml.safe_load(f) or {}

    return RosterConfig(**payload)


def normalize_roster_tiers(tiers: Collection[str] | None) -> tuple[RosterTier, ...]:
    """Normalize and validate roster tiers."""
    if not tiers:
        return DEFAULT_ACTIVE_TIERS

    normalized = tuple(dict.fromkeys(str(tier).strip().lower() for tier in tiers if str(tier).strip()))
    invalid = [tier for tier in normalized if tier not in ALL_ROSTER_TIERS]
    if invalid:
        invalid_list = ", ".join(invalid)
        raise ValueError(f"Unsupported roster tiers: {invalid_list}")

    return normalized  # type: ignore[return-value]


def iter_specialist_records(
    staff_dir: Path,
    *,
    tiers: Collection[str] | None = None,
    config_path: Path | None = None,
) -> list[SpecialistRecord]:
    """Return specialist records filtered by roster tiers."""
    roster = load_roster_config(config_path)
    allowed_tiers = set(normalize_roster_tiers(tiers))

    records: list[SpecialistRecord] = []
    for dept_dir in sorted(staff_dir.iterdir()):
        if not dept_dir.is_dir() or dept_dir.name.startswith("."):
            continue

        for yaml_file in sorted(dept_dir.rglob("*.yaml")):
            slug = yaml_file.stem
            tier = roster.tier_for_slug(slug)
            if tier not in allowed_tiers:
                continue

            records.append(
                SpecialistRecord(
                    slug=slug,
                    department=dept_dir.name,
                    path=yaml_file,
                    tier=tier,
                )
            )

    return records


def list_specialists_by_department(
    staff_dir: Path,
    *,
    tiers: Collection[str] | None = None,
    config_path: Path | None = None,
) -> Dict[str, list[str]]:
    """Group specialist slugs by department for the selected tiers."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for record in iter_specialist_records(staff_dir, tiers=tiers, config_path=config_path):
        grouped[record.department].append(record.slug)

    return {department: sorted(slugs) for department, slugs in sorted(grouped.items())}


def get_specialist_slugs(
    staff_dir: Path,
    *,
    tiers: Collection[str] | None = None,
    config_path: Path | None = None,
) -> list[str]:
    """Return specialist slugs for the selected tiers."""
    return [record.slug for record in iter_specialist_records(staff_dir, tiers=tiers, config_path=config_path)]

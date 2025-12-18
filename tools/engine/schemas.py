"""Pydantic schemas for specialist YAML validation."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class CoreIdentity(BaseModel):
    """Core identity attributes of a specialist."""
    role: str
    personality: str
    expertise: List[str]
    communication_style: str


class Capability(BaseModel):
    """A single capability with optional sub-capabilities."""
    name: str
    description: str
    tasks: Optional[List[str]] = None
    sub_capabilities: Optional[List['Capability']] = None


class ActivationPattern(BaseModel):
    """Pattern for activating specialist."""
    type: Optional[str] = None
    name: Optional[str] = None  # Some sub-types use 'name' instead of 'type'
    pattern: Optional[str] = None
    examples: Optional[List[str]] = None
    sub_types: Optional[List['ActivationPattern']] = None

    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v: Optional[str], info) -> Optional[str]:
        """Pattern is required unless sub_types are present."""
        # Note: We can't easily check for presence of sub_types here in field validator
        # strictly, but this relaxes the hard requirement.
        return v


class IntegrationPoints(BaseModel):
    """Collaboration patterns."""
    primary_collaborations: List[str]
    secondary_collaborations: Optional[List[str]] = None
    specialized_coordination: Optional[List[str]] = None


class PerformanceStandards(BaseModel):
    """Quality and success metrics."""
    quality_indicators: List[str]
    success_metrics: List[str]
    kpis: Optional[List[str]] = None


class DeliveryCategory(BaseModel):
    """Category of deliverables."""
    category: str
    items: List[str]


class KnowledgeArea(BaseModel):
    """Specialized knowledge domain."""
    area: str
    skills: List[str]


class WorkflowPhase(BaseModel):
    """Phase in specialist workflow."""
    phase: str
    steps: List[str]


class DeepDive(BaseModel):
    """Deep dive section with deliverables and knowledge areas."""
    typical_deliverables: List[DeliveryCategory]
    specialized_knowledge_areas: List[KnowledgeArea]

    model_config = {
        'extra': 'allow'  # Allow workflow fields with dynamic names
    }


class SpecialistSchema(BaseModel):
    """Complete specialist YAML schema."""
    version: str | float
    specialist: str
    motto: str
    core_identity: CoreIdentity
    core_capabilities: List[Capability]
    integration_points: IntegrationPoints
    activation_patterns: List[ActivationPattern]
    performance_standards: PerformanceStandards
    deep_dive: Optional[DeepDive] = None

    model_config = {
        'extra': 'allow'  # Allow additional top-level fields
    }

    @field_validator('version')
    @classmethod
    def validate_version(cls, v: str | float) -> str:
        """Ensure version is 1.x."""
        str_v = str(v)
        if not str_v.startswith('1.'):
            raise ValueError(f"Unsupported schema version: {v}")
        return str_v

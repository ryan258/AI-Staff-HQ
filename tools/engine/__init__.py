"""
AI Staff HQ Executable Engine

Converts specialist YAML files into executable LangChain agents.
"""

from .core import SpecialistAgent, load_specialist
from .schemas import SpecialistSchema

__version__ = "0.2.0"

__all__ = [
    "SpecialistAgent",
    "load_specialist",
    "SpecialistSchema",
]

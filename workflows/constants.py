"""Workflow constants and specialist slug definitions.

This module centralizes specialist slugs used across workflows to avoid
magic strings and enable easier refactoring if specialists are renamed.
"""

from pathlib import Path
from typing import Collection, Set

from tools.engine.roster import get_specialist_slugs


# Configuration Constants
CACHE_KEY_SEPARATOR = "::"
DEFAULT_GRAPH_LOG_DIR = Path("logs") / "graphs"



class GraphNodes:
    """Constants for LangGraph node names."""
    PLANNING = "planning"
    CAPABILITY_MATCHING = "capability_matching"
    EXECUTION_PLANNING = "execution_planning"
    WAVE_EXECUTION = "wave_execution"
    SYNTHESIS = "synthesis"


class SpecialistSlugs:
    """Centralized specialist slug constants.

    These slugs must match the YAML filenames in the staff/ directory.
    """
    # Strategy Department
    CHIEF_OF_STAFF = "chief-of-staff"
    MARKET_ANALYST = "market-analyst"
    CREATIVE_STRATEGIST = "creative-strategist"
    ALCHEMIST = "alchemist"
    CARTOGRAPHER_INVISIBLE = "cartographer-invisible"
    ETHICIST = "ethicist"
    SCENARIO_PLANNER = "scenario-planner"
    ETYMOLOGIST_DECAY = "etymologist-decay"

    # Tech Department
    SOFTWARE_ARCHITECT = "software-architect"
    TOOLMAKER = "toolmaker"
    QUALITY_CONTROL_SPECIALIST = "quality-control-specialist"
    INFINITE_LOOPER = "infinite-looper"
    IRONY_DETECTOR = "irony-detector"
    HANDYMAN = "handyman"

    # Knowledge Department
    LIBRARIAN_BABEL = "librarian-babel"
    ANTIQUARIAN = "antiquarian"
    ARCHIVIST_SILENCE = "archivist-silence"
    LOCAL_HISTORIAN = "local-historian"

    # Health & Lifestyle Department
    SHADOW_WORKER = "shadow-worker"
    ACTIVE_IMAGINATION_GUIDE = "active-imagination-guide"
    HUMANIST = "humanist"
    XENOBIOLOGIST = "xenobiologist"

    # Producers Department
    SYMBOLIST = "symbolist"
    MYTHOLOGIST = "mythologist"
    MIRROR_MAKER = "mirror-maker"
    TRANSLATOR_SILENCE = "translator-silence"
    NARRATOR = "narrator"
    DREAM_NAVIGATOR = "dream-navigator"
    FORENSIC_CONSULTANT = "forensic-consultant"
    DIALECT_COACH = "dialect-coach"
    BETA_READER = "beta-reader"
    CREATIVE_WRITER = "creative-writer"


def get_available_specialists(
    staff_dir: Path,
    *,
    tiers: Collection[str] | None = None,
) -> Set[str]:
    """Get set of all available specialist slugs from staff directory.

    Args:
        staff_dir: Path to staff/ directory
        tiers: Optional roster tiers to include

    Returns:
        Set of specialist slugs (YAML filenames without extension)
    """
    return set(get_specialist_slugs(staff_dir, tiers=tiers))

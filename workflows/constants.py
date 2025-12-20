"""Workflow constants and specialist slug definitions.

This module centralizes specialist slugs used across workflows to avoid
magic strings and enable easier refactoring if specialists are renamed.
"""

from pathlib import Path
from typing import Set


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

    # Knowledge Department
    LIBRARIAN_BABEL = "librarian-babel"
    ANTIQUARIAN = "antiquarian"
    ARCHIVIST_SILENCE = "archivist-silence"

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


def get_available_specialists(staff_dir: Path) -> Set[str]:
    """Get set of all available specialist slugs from staff directory.

    Args:
        staff_dir: Path to staff/ directory

    Returns:
        Set of specialist slugs (YAML filenames without extension)
    """
    specialists = set()
    for dept_dir in staff_dir.iterdir():
        if not dept_dir.is_dir() or dept_dir.name.startswith('.'):
            continue
        for yaml_file in dept_dir.rglob("*.yaml"):
            specialists.add(yaml_file.stem)
    return specialists

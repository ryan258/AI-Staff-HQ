#!/usr/bin/env python3
"""Validate specialist YAML files against the runtime Pydantic schema.

This uses the same `SpecialistSchema` the engine loads at activation time, so a
file that passes here is guaranteed to load at runtime (no more split-brain
between a loose 3-key check and the real schema).
"""

import os
import sys
import glob

import yaml
from pydantic import ValidationError

# Allow running both as a module and as a standalone script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.engine.schemas import SpecialistSchema


def validate_specialist(filepath: str) -> bool:
    """Validate a single specialist YAML file against SpecialistSchema."""
    try:
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ {filepath}: Invalid YAML - {e}")
        return False
    except OSError as e:
        print(f"❌ {filepath}: Could not read file - {e}")
        return False

    if not data:
        print(f"❌ {filepath}: Empty file")
        return False

    try:
        SpecialistSchema(**data)
    except ValidationError as e:
        # Summarize the first few field errors for a readable report.
        errors = e.errors()
        summary = "; ".join(
            f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}"
            for err in errors[:5]
        )
        more = f" (+{len(errors) - 5} more)" if len(errors) > 5 else ""
        print(f"❌ {filepath}: Schema validation failed - {summary}{more}")
        return False
    except TypeError as e:
        print(f"❌ {filepath}: Malformed structure - {e}")
        return False

    print(f"✅ {filepath}: Valid")
    return True


def main() -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    staff_dir = os.path.join(base_dir, "staff")

    yaml_files = glob.glob(os.path.join(staff_dir, "**", "*.yaml"), recursive=True)

    print(f"\U0001f50d Validating {len(yaml_files)} specialists in {staff_dir}...\n")

    passed = 0
    failed = 0

    for file in sorted(yaml_files):
        if validate_specialist(file):
            passed += 1
        else:
            failed += 1

    print(f"\n\U0001f4ca Result: {passed} Passed, {failed} Failed")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()

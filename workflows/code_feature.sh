#!/usr/bin/env bash
# Workflows: Code Feature Scaffold (CLI Chaining Example)
#
# This script demonstrates how to use the 'activate' CLI tool to pipe
# context between agents, creating a linear production line.
#
# Process: Tech Lead -> Python Specialist -> QA Specialist

# Ensure strictly one argument
if [ -z "$1" ]; then
    echo "Usage: ./workflows/code_feature.sh \"Feature Description\""
    exit 1
fi

FEATURE="$1"
PROJECT_ROOT="$(dirname "$0")/.."
ACTIVATE="uv run tools/activate.py"

echo "🚀 Starting Feature Scaffold Workflow: '$FEATURE'"
echo "------------------------------------------------"

# 1. Tech Lead Design
echo ""
echo "🔵 Phase 1: Technical Design (Software Architect)"
DESIGN=$($ACTIVATE software-architect -q "Design the architecture for this feature: '$FEATURE'. Provide a high-level component breakdown and key classes.")

echo "$DESIGN"
echo "------------------------------------------------"

# 2. Python Implementation
echo ""
echo "🟡 Phase 2: Implementation (Automation Specialist)"
# Pass the design into the prompt
CODE=$($ACTIVATE automation-specialist -q "Context: $DESIGN. \n\nTask: Write the Python code structure for this feature. Include docstrings but keep methods empty (pass).")

echo "$CODE"
echo "------------------------------------------------"

# 3. QA Test Plan
echo ""
echo "🟢 Phase 3: Test Plan (Quality Control)"
# Pass the code into the prompt
TESTS=$($ACTIVATE quality-control-specialist -q "Context: $CODE. \n\nTask: Write a checklist of unit tests required to verify this code.")

echo "$TESTS"
echo "------------------------------------------------"
echo "✅ Workflow Complete!"

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORIG_DIR="$PWD"
trap 'cd "$ORIG_DIR" 2>/dev/null || true' EXIT INT TERM

cd "$SCRIPT_DIR"

echo "🚀 Starting AI-Staff-HQ..."

verify_existing_environment() {
    if [[ ! -x ".venv/bin/python" ]]; then
        return 1
    fi
    .venv/bin/python -c 'import yaml, langgraph, streamlit' >/dev/null 2>&1
}

# Only run uv sync if virtualenv does not exist or if explicitly requested with --sync
if [[ "${1:-}" == "--sync" ]] || [[ ! -d ".venv" ]]; then
    echo "📦 Checking dependencies..."
    if [[ "${OFFLINE:-0}" == "1" ]] || [[ "${UV_OFFLINE:-0}" == "1" ]]; then
        if ! uv sync --extra ui --offline; then
            echo "❌ Offline dependency synchronization failed; checking the existing environment..." >&2
            if ! verify_existing_environment; then
                echo "❌ Existing .venv is incomplete; cannot launch offline. Run ./run.sh with network access or repair .venv." >&2
                exit 1
            fi
            echo "⚠️  Continuing with the verified existing offline environment." >&2
        fi
    else
        uv sync --extra ui
    fi
fi

if ! verify_existing_environment; then
    echo "❌ Existing .venv is incomplete; refusing to launch. Run ./run.sh --sync to repair dependencies." >&2
    exit 1
fi

if [[ "${OFFLINE:-0}" == "1" ]] || [[ "${UV_OFFLINE:-0}" == "1" ]]; then
    echo "🖥️  Launching Streamlit Dashboard from the verified offline environment..."
    exec .venv/bin/python -m streamlit run ui/app.py
fi

echo "🖥️  Launching Streamlit Dashboard..."
exec uv run streamlit run ui/app.py

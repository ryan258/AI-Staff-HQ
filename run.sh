#!/bin/bash
set -e

echo "🚀 Starting AI-Staff-HQ..."

echo "📦 Checking dependencies..."
uv sync --extra ui

echo "🖥️  Launching Streamlit Dashboard..."
uv run streamlit run ui/app.py

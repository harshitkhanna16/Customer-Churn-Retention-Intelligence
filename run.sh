#!/bin/bash
# ==============================================================================
# Customer Churn & Retention Intelligence — Application Launcher
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment .venv not found. Please run 'make setup' first."
    exit 1
fi

echo "🚀 Launching Customer Churn & Retention Intelligence Streamlit Portal..."
echo "📍 Local URL: http://localhost:8501"
.venv/bin/streamlit run app.py

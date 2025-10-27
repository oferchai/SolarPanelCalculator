#!/bin/bash
# Solar Panel Analysis Dashboard Launcher

echo "🚀 Starting Solar Panel Analysis Dashboard..."
echo ""

cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"

poetry run streamlit run app.py


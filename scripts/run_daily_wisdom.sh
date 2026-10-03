#!/usr/bin/env bash
# ==============================================================================
# MASTER BOOTSTRAPPER FOR CONTINUOUS HIGH-DENSITY TECHNICAL WISDOM GENERATION
# Powered by Google Gemini Pro Engine
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Initializing Systemic Paradigm Loop via Gemini Dispatch Engine..."

# Dynamically resolve active Python interpreter (Linux, macOS, and Windows compatible)
if command -v python3 &>/dev/null && python3 -c "import sys" &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null && python -c "import sys" &>/dev/null; then
    PYTHON_CMD="python"
elif command -v py &>/dev/null && py -c "import sys" &>/dev/null; then
    PYTHON_CMD="py"
else
    echo "ERROR: Valid Python runtime is required to execute the Gemini dispatch generator." >&2
    exit 1
fi

"${PYTHON_CMD}" "${SCRIPT_DIR}/generate_dispatch.py"

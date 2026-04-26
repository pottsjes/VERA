#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "Setting up V.E.R.A. in $PROJECT_DIR"

# Create venv if missing
[ -d venv ] || python3 -m venv venv --prompt vera

# Activate and install
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Register Jupyter kernel if not already present
if ! jupyter kernelspec list 2>/dev/null | grep -q "vera-env"; then
    pip install ipykernel
    python -m ipykernel install --user --name=vera-env --display-name "Python(VERA)"
fi

echo "Done. Activate with: source venv/bin/activate"

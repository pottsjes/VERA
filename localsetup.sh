#!/bin/bash

# Define the project directory
PROJECT_DIR="$(dirname "$(realpath "$0")")"
echo "Setting up V.E.R.A. in $PROJECT_DIR"

# Detect system architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Create a virtual environment if it doesn't exist
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_DIR/venv" --prompt "vera"
fi

# Activate the virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies (skips if already installed)
echo "Installing dependencies..."
pip install -r "$PROJECT_DIR/requirements.txt"

# Fix psutil installation based on architecture
if [ "$ARCH" = "arm64" ]; then
    echo "Installing psutil for Apple Silicon (ARM64)..."
    pip uninstall -y psutil
    pip install --no-binary :all: psutil
elif [ "$ARCH" = "x86_64" ]; then
    echo "Installing psutil for Intel Mac..."
    pip install psutil
else
    echo "Unknown architecture: $ARCH. Skipping psutil optimization."
fi

# Install Jupyter kernel (optional)
if ! jupyter kernelspec list | grep -q "vera-env"; then
    echo "Setting up Jupyter kernel..."
    pip install ipykernel
    python -m ipykernel install --user --name=vera-env --display-name "Python(VERA)"
fi

echo "============================================================================================="
echo "Setup complete! To activate the environment, run:"
echo "source venv/bin/activate"
echo "============================================================================================="

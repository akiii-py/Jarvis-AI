#!/bin/bash
# Auto-activate virtual environment when entering this directory

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$DIR/venv/bin/activate"

echo "✅ Virtual environment activated"
echo "You can now run: python main.py"

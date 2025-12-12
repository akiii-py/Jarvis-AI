#!/bin/bash

# JARVIS Launcher Script
# Automatically clears Python cache before starting

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Clearing Python cache...${NC}"
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo -e "${GREEN}✓ Cache cleared${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory
cd "$SCRIPT_DIR"

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null && ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Starting Ollama..."
    
    # Try to start Ollama app first
    if [ -d "/Applications/Ollama.app" ]; then
        open -a Ollama
        sleep 3
    else
        # Fallback to ollama serve
        ollama serve > /dev/null 2>&1 &
        sleep 3
    fi
fi

# Verify Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Error: Could not start Ollama. Please start it manually."
    exit 1
fi

# Check if required models are installed
REQUIRED_MODELS=("qwen2.5-coder:latest" "deepseek-r1:latest" "mistral:7b")

for model in "${REQUIRED_MODELS[@]}"; do
    if ! ollama list | grep -q "$model"; then
        echo "Model $model not found. Pulling..."
        ollama pull "$model"
    fi
done

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run JARVIS with all arguments passed to this script
python main.py "$@"

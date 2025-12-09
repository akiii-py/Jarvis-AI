#!/bin/bash

# JARVIS AI Launcher Script
# Run JARVIS from anywhere without directory issues

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# JARVIS project directory
JARVIS_DIR="$SCRIPT_DIR"

# Virtual environment path
VENV_PATH="$JARVIS_DIR/venv/bin/python"

# Main script path
MAIN_SCRIPT="$JARVIS_DIR/main.py"

# Print banner
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}     ${GREEN}JARVIS AI Assistant${NC}              ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}     Initializing systems...           ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if virtual environment exists
if [ ! -f "$VENV_PATH" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo -e "${YELLOW}Expected location: $VENV_PATH${NC}"
    echo -e "${YELLOW}Please run: python3 -m venv venv${NC}"
    exit 1
fi

# Check if main.py exists
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo -e "${RED}Error: main.py not found!${NC}"
    echo -e "${YELLOW}Expected location: $MAIN_SCRIPT${NC}"
    exit 1
fi

# Change to JARVIS directory
cd "$JARVIS_DIR" || exit 1

# Check if Ollama is running
if pgrep -x "ollama" > /dev/null || pgrep -f "ollama serve" > /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama is running"
else
    echo -e "${YELLOW}⚡ Ollama not running. Starting Ollama...${NC}"
    # Try opening the Mac app first
    if open -a Ollama 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Started Ollama.app"
        sleep 2 # Wait for it to initialize
    else
        # Fallback to CLI serve
        if command -v ollama &> /dev/null; then
            ollama serve > /dev/null 2>&1 &
            echo -e "${GREEN}✓${NC} Started Ollama server (background)"
            sleep 2
        else
            echo -e "${RED}Error: Ollama not found! Please install it first.${NC}"
            exit 1
        fi
    fi
fi

# Check for required models
REQUIRED_MODELS=("qwen2.5-coder:latest" "deepseek-r1:latest" "mistral:7b")
echo -e "${BLUE}Checking models...${NC}"

if command -v ollama &> /dev/null; then
    # Get list of installed models
    INSTALLED_MODELS=$(ollama list)
    
    for model in "${REQUIRED_MODELS[@]}"; do
        # Check if model exists in the list (ignoring tag if needed, but here we check full name)
        # We use grep to check if the model name appears in the output
        if echo "$INSTALLED_MODELS" | grep -q "${model%%:*}"; then
             echo -e "${GREEN}✓${NC} Model available: $model"
        else
             echo -e "${YELLOW}⚡ Model missing: $model. Pulling... (this may take a while)${NC}"
             ollama pull "$model"
        fi
    done
fi

echo -e "${GREEN}✓${NC} Virtual environment: ${BLUE}$VENV_PATH${NC}"
echo -e "${GREEN}✓${NC} Working directory: ${BLUE}$JARVIS_DIR${NC}"
echo -e "${GREEN}✓${NC} Starting JARVIS...${NC}"
echo ""

# Run JARVIS
exec "$VENV_PATH" "$MAIN_SCRIPT"

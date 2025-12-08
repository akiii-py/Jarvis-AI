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

echo -e "${GREEN}✓${NC} Virtual environment: ${BLUE}$VENV_PATH${NC}"
echo -e "${GREEN}✓${NC} Working directory: ${BLUE}$JARVIS_DIR${NC}"
echo -e "${GREEN}✓${NC} Starting JARVIS...${NC}"
echo ""

# Run JARVIS
exec "$VENV_PATH" "$MAIN_SCRIPT"

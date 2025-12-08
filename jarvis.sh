#!/bin/bash
# Jarvis AI - Quick Start Script
# Activates venv and runs Jarvis

cd "$(dirname "$0")"
source venv/bin/activate
python main.py "$@"

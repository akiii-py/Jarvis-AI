import sys
from pathlib import Path

# Add src to python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.agent import Jarvis

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Jarvis AI Agent")
    parser.add_argument("--voice", action="store_true", help="Enable voice mode")
    args = parser.parse_args()

    jarvis = Jarvis()
    try:
        jarvis.run(voice_mode=args.voice)
    finally:
        jarvis.cleanup()

if __name__ == "__main__":
    main()

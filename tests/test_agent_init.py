import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.agent import Jarvis

def test_agent_init():
    try:
        agent = Jarvis()
        print("Jarvis initialized successfully.")
        return True
    except Exception as e:
        print(f"Failed to initialize Jarvis: {e}")
        return False

if __name__ == "__main__":
    if test_agent_init():
        sys.exit(0)
    else:
        sys.exit(1)

"""
Test close app functionality
"""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mac_control import MacController


def test_close_app():
    """Test app closing"""
    print("Testing Close App...")
    mac = MacController()
    
    # First open Terminal
    print("  Opening Terminal...")
    success, message = mac.open_app("terminal")
    print(f"    {message}")
    
    # Wait a moment
    time.sleep(2)
    
    # Now close it
    print("  Closing Terminal...")
    success, message = mac.close_app("terminal")
    print(f"    {message}")
    assert success, "Failed to close Terminal"
    
    print("✅ Close app tests passed\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Close App Test")
    print("=" * 50 + "\n")
    
    test_close_app()
    
    print("=" * 50)
    print("Test passed! ✅")
    print("=" * 50)

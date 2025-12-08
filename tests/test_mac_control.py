"""
Test Mac Control functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mac_control import MacController


def test_app_launcher():
    """Test app launching"""
    print("Testing App Launcher...")
    mac = MacController()
    
    # Test opening an app
    success, message = mac.open_app("terminal")
    print(f"  Open Terminal: {message}")
    assert success, "Failed to open Terminal"
    
    print("✅ App launcher tests passed\n")


def test_volume_control():
    """Test volume control"""
    print("Testing Volume Control...")
    mac = MacController()
    
    # Test setting volume
    success, message = mac.set_volume(50)
    print(f"  Set volume to 50%: {message}")
    assert success, "Failed to set volume"
    
    # Test volume up
    success, message = mac.adjust_volume("up")
    print(f"  Volume up: {message}")
    assert success, "Failed to adjust volume up"
    
    print("✅ Volume control tests passed\n")


def test_app_mapping():
    """Test app name mappings"""
    print("Testing App Mappings...")
    mac = MacController()
    
    # Test that common names map correctly
    assert mac.APP_MAPPINGS["vscode"] == "Visual Studio Code"
    assert mac.APP_MAPPINGS["chrome"] == "Google Chrome"
    assert mac.APP_MAPPINGS["terminal"] == "Terminal"
    
    print("✅ App mapping tests passed\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Mac Control Tests")
    print("=" * 50 + "\n")
    
    test_app_mapping()
    test_app_launcher()
    test_volume_control()
    
    print("=" * 50)
    print("All tests passed! ✅")
    print("=" * 50)

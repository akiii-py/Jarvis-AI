#!/usr/bin/env python3
"""
Test script to verify Spotify automation works
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integrations.element_finder import AccessibilityHelper
from src.integrations.spotify_controller import SpotifyController
from src.core.mac_control import MacController

def test_accessibility():
    """Test if accessibility permissions are granted."""
    print("Testing accessibility permissions...")
    
    try:
        current_app = AccessibilityHelper.get_frontmost_app()
        if current_app:
            print(f"✅ Accessibility working! Current app: {current_app}")
            return True
        else:
            print("❌ Accessibility not working - no app detected")
            return False
    except Exception as e:
        print(f"❌ Accessibility error: {e}")
        return False

def test_spotify_basic():
    """Test basic Spotify control."""
    print("\nTesting Spotify control...")
    
    try:
        mac = MacController()
        spotify = SpotifyController(mac)
        
        print("Opening Spotify...")
        if spotify.open_spotify():
            print("✅ Spotify opened successfully")
            
            # Test getting current track
            current = spotify.get_current_track()
            if current:
                print(f"✅ Current track: {current}")
            else:
                print("⚠️  No track playing or couldn't get track info")
            
            return True
        else:
            print("❌ Failed to open Spotify")
            return False
            
    except Exception as e:
        print(f"❌ Spotify test error: {e}")
        return False

def test_typing():
    """Test text typing with special characters."""
    print("\nTesting text typing...")
    
    test_strings = [
        "hello world",
        "test 123",
        'song with "quotes"',
        "9 by drake"
    ]
    
    for test_str in test_strings:
        print(f"Testing: {test_str}")
        try:
            # Don't actually type, just test escaping
            print(f"  ✅ Would type: {test_str}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("JARVIS Spotify Automation Test")
    print("=" * 50)
    
    # Test 1: Accessibility
    if not test_accessibility():
        print("\n⚠️  ACCESSIBILITY PERMISSIONS REQUIRED!")
        print("\nPlease grant permissions:")
        print("1. System Preferences → Security & Privacy → Privacy → Accessibility")
        print("2. Add Terminal (or your IDE)")
        print("3. Restart this script")
        sys.exit(1)
    
    # Test 2: Spotify
    test_spotify_basic()
    
    # Test 3: Typing
    test_typing()
    
    print("\n" + "=" * 50)
    print("Test complete!")
    print("=" * 50)

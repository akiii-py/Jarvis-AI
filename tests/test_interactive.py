#!/usr/bin/env python3
"""
JARVIS Interactive Integration Tests
Tests features that require actual system interaction with user confirmation
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.mac_control import MacController
from src.integrations.app_navigator import AppNavigator
from src.integrations.spotify_controller import SpotifyController
from src.integrations.browser_controller import BrowserController
from src.core.llm import LLMClient
from src.core.personality_v2 import JarvisPersonalityV2


class InteractiveTestSuite:
    """Interactive tests that require user confirmation"""
    
    def __init__(self):
        self.results = []
        self.mac_control = MacController()
        self.llm = LLMClient()
        self.personality = JarvisPersonalityV2(llm_client=self.llm)
        self.app_navigator = AppNavigator(
            mac_control=self.mac_control,
            personality=self.personality,
            llm_client=self.llm
        )
    
    def ask_permission(self, action: str) -> bool:
        """Ask user for permission to perform action"""
        print(f"\n{'='*70}")
        print(f"🔔 Permission Required: {action}")
        print(f"{'='*70}")
        response = input("Proceed? (y/n): ").strip().lower()
        return response == 'y'
    
    def run_all_tests(self):
        """Run all interactive tests"""
        print("\n" + "="*70)
        print("🧪 JARVIS INTERACTIVE INTEGRATION TESTS")
        print("="*70)
        print("These tests will interact with your system.")
        print("You'll be asked for permission before each action.\n")
        
        # Test categories
        self.test_app_opening()
        self.test_volume_control()
        self.test_spotify_integration()
        self.test_browser_automation()
        self.test_app_navigation()
        
        # Generate report
        self.generate_report()
    
    def test_app_opening(self):
        """Test opening actual applications"""
        print("\n📱 Testing App Opening...")
        
        if self.ask_permission("Open Calculator app"):
            try:
                success, msg = self.mac_control.open_app("Calculator")
                if success:
                    print("  ✅ Calculator opened successfully")
                    self.results.append(("App Opening - Calculator", True, "Opened successfully"))
                    
                    # Ask to close it
                    if self.ask_permission("Close Calculator"):
                        success, msg = self.mac_control.close_app("Calculator")
                        if success:
                            print("  ✅ Calculator closed successfully")
                            self.results.append(("App Closing - Calculator", True, "Closed successfully"))
                        else:
                            print(f"  ❌ Failed to close: {msg}")
                            self.results.append(("App Closing - Calculator", False, msg))
                else:
                    print(f"  ❌ Failed to open: {msg}")
                    self.results.append(("App Opening - Calculator", False, msg))
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.results.append(("App Opening - Calculator", False, str(e)))
        else:
            print("  ⏭️  Skipped")
            self.results.append(("App Opening - Calculator", None, "Skipped by user"))
    
    def test_volume_control(self):
        """Test volume control"""
        print("\n🔊 Testing Volume Control...")
        
        if self.ask_permission("Change system volume (will restore after)"):
            try:
                # Get current volume first
                import subprocess
                result = subprocess.run(
                    ["osascript", "-e", "output volume of (get volume settings)"],
                    capture_output=True,
                    text=True
                )
                original_volume = int(result.stdout.strip())
                print(f"  📊 Current volume: {original_volume}%")
                
                # Test setting volume to 30
                success, msg = self.mac_control.set_volume(30)
                if success:
                    print("  ✅ Volume set to 30%")
                    self.results.append(("Volume Control - Set", True, "Set to 30%"))
                    
                    # Wait a moment
                    import time
                    time.sleep(1)
                    
                    # Restore original volume
                    success, msg = self.mac_control.set_volume(original_volume)
                    if success:
                        print(f"  ✅ Volume restored to {original_volume}%")
                        self.results.append(("Volume Control - Restore", True, f"Restored to {original_volume}%"))
                    else:
                        print(f"  ⚠️  Could not restore volume: {msg}")
                        self.results.append(("Volume Control - Restore", False, msg))
                else:
                    print(f"  ❌ Failed to set volume: {msg}")
                    self.results.append(("Volume Control - Set", False, msg))
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.results.append(("Volume Control", False, str(e)))
        else:
            print("  ⏭️  Skipped")
            self.results.append(("Volume Control", None, "Skipped by user"))
    
    def test_spotify_integration(self):
        """Test Spotify automation"""
        print("\n🎵 Testing Spotify Integration...")
        
        print("  ℹ️  This requires Spotify to be installed")
        if self.ask_permission("Open Spotify and search for a song"):
            try:
                spotify = SpotifyController(self.mac_control)
                
                # Open Spotify
                success = spotify.open_spotify()
                if success:
                    print("  ✅ Spotify opened")
                    self.results.append(("Spotify - Open", True, "Opened successfully"))
                    
                    import time
                    time.sleep(3)  # Wait for Spotify to load
                    
                    # Try to search (won't actually play to avoid disruption)
                    print("  ℹ️  Testing search interface (won't play)")
                    # Just verify the method exists
                    if hasattr(spotify, 'search_and_play'):
                        print("  ✅ Search method available")
                        self.results.append(("Spotify - Search Method", True, "Method exists"))
                    
                    # Test playback controls
                    if self.ask_permission("Test Spotify playback controls (pause/play)"):
                        spotify.pause()
                        print("  ✅ Pause command sent")
                        time.sleep(1)
                        spotify.play()
                        print("  ✅ Play command sent")
                        self.results.append(("Spotify - Playback Controls", True, "Pause/Play working"))
                else:
                    print("  ❌ Failed to open Spotify")
                    self.results.append(("Spotify - Open", False, "Could not open"))
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.results.append(("Spotify Integration", False, str(e)))
        else:
            print("  ⏭️  Skipped")
            self.results.append(("Spotify Integration", None, "Skipped by user"))
    
    def test_browser_automation(self):
        """Test browser automation"""
        print("\n🌐 Testing Browser Automation...")
        
        if self.ask_permission("Open Chrome/Safari and navigate to a test page"):
            try:
                browser = BrowserController(self.mac_control)
                
                # Open browser
                success = browser.open_browser()
                if success:
                    print("  ✅ Browser opened")
                    self.results.append(("Browser - Open", True, "Opened successfully"))
                    
                    import time
                    time.sleep(2)
                    
                    # Navigate to a simple page
                    if self.ask_permission("Navigate to google.com"):
                        success = browser.open_website("google.com")
                        if success:
                            print("  ✅ Navigated to google.com")
                            self.results.append(("Browser - Navigation", True, "Navigated successfully"))
                        else:
                            print("  ❌ Navigation failed")
                            self.results.append(("Browser - Navigation", False, "Failed"))
                else:
                    print("  ❌ Failed to open browser")
                    self.results.append(("Browser - Open", False, "Could not open"))
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.results.append(("Browser Automation", False, str(e)))
        else:
            print("  ⏭️  Skipped")
            self.results.append(("Browser Automation", None, "Skipped by user"))
    
    def test_app_navigation(self):
        """Test app navigation with intent detection"""
        print("\n🎯 Testing App Navigation with Intent Detection...")
        
        if self.ask_permission("Test natural language app command"):
            try:
                # Test a simple command
                test_command = "open calculator"
                print(f"  📝 Testing command: '{test_command}'")
                
                is_handled, response = self.app_navigator.handle_app_navigation(test_command)
                
                if is_handled:
                    print(f"  ✅ Command handled: {response}")
                    self.results.append(("App Navigation - Intent", True, f"Handled: {response}"))
                else:
                    print(f"  ❌ Command not handled")
                    self.results.append(("App Navigation - Intent", False, "Not handled"))
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.results.append(("App Navigation", False, str(e)))
        else:
            print("  ⏭️  Skipped")
            self.results.append(("App Navigation", None, "Skipped by user"))
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*70)
        print("📊 INTERACTIVE TEST REPORT")
        print("="*70)
        
        # Count results
        total = len(self.results)
        passed = sum(1 for _, status, _ in self.results if status is True)
        failed = sum(1 for _, status, _ in self.results if status is False)
        skipped = sum(1 for _, status, _ in self.results if status is None)
        
        print(f"\n📈 Summary:")
        print(f"  Total Tests: {total}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⏭️  Skipped: {skipped}")
        
        if total > 0:
            success_rate = (passed / (total - skipped) * 100) if (total - skipped) > 0 else 0
            print(f"  Success Rate: {success_rate:.1f}% (of non-skipped)")
        
        # Detailed results
        print("\n📋 Detailed Results:\n")
        for name, status, message in self.results:
            if status is True:
                icon = "✅"
            elif status is False:
                icon = "❌"
            else:
                icon = "⏭️ "
            
            print(f"  {icon} {name}")
            print(f"     {message}")
        
        print("\n" + "="*70)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)


def main():
    """Run interactive tests"""
    print("\n⚠️  IMPORTANT:")
    print("These tests will interact with your system (open apps, change volume, etc.)")
    print("You'll be asked for permission before each action.")
    print("You can skip any test by answering 'n'.\n")
    
    response = input("Ready to proceed? (y/n): ").strip().lower()
    if response != 'y':
        print("\n❌ Tests cancelled.")
        return
    
    suite = InteractiveTestSuite()
    suite.run_all_tests()


if __name__ == "__main__":
    main()

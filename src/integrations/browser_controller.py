"""
Browser Controller Module
- Search YouTube and play videos
- Perform Google searches
- Navigate to websites
- Auto-detects system default browser
"""

import subprocess
import time
from .element_finder import AccessibilityHelper


def get_default_browser() -> str:
    """
    Detect the system's default browser on macOS.
    
    Returns:
        str: Name of the default browser app (e.g., "Safari", "Google Chrome", "Firefox")
    """
    try:
        # Use macOS launch services to get default HTTP handler
        result = subprocess.run(
            ['defaults', 'read', 'com.apple.LaunchServices/com.apple.launchservices.secure', 'LSHandlers'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        # Parse output to find HTTP handler
        output = result.stdout
        
        # Common browser identifiers
        browser_map = {
            'safari': 'Safari',
            'chrome': 'Google Chrome',
            'firefox': 'Firefox',
            'brave': 'Brave Browser',
            'edge': 'Microsoft Edge',
            'opera': 'Opera',
            'arc': 'Arc'
        }
        
        # Check which browser is in the output
        output_lower = output.lower()
        for key, browser_name in browser_map.items():
            if key in output_lower:
                return browser_name
        
        # Fallback to Safari (default macOS browser)
        return "Safari"
        
    except Exception as e:
        print(f"Could not detect default browser: {e}")
        return "Safari"  # Safe default for macOS


class BrowserController:
    """Control web browser for navigation and searching."""
    
    def __init__(self, mac_control, browser: str = None):
        self.mac_control = mac_control
        self.accessibility = AccessibilityHelper()
        # Auto-detect browser if not specified
        self.browser = browser if browser else get_default_browser()
        print(f"🌐 Using browser: {self.browser}")
    
    def open_browser(self) -> bool:
        """Open default browser."""
        try:
            self.mac_control.open_app(self.browser)
            return self.accessibility.wait_for_app(self.browser, timeout=4)
        except:
            return False
    
    def go_to_url(self, url: str) -> bool:
        """Navigate to a URL."""
        try:
            if not self.open_browser():
                return False
            
            time.sleep(1)
            self.accessibility.activate_app(self.browser)
            time.sleep(0.2)
            
            # Cmd+L focuses address bar
            subprocess.run(['osascript', '-e', 'keystroke "l" using command down'], timeout=1)
            time.sleep(0.3)
            
            # Add https:// if not present
            if not url.startswith("http"):
                url = "https://" + url
            
            self.accessibility.type_text(url, delay=0.02)
            time.sleep(0.3)
            self.accessibility.press_key("return")
            time.sleep(2)
            
            return True
        except:
            return False
    
    def search_youtube(self, query: str) -> bool:
        """Search YouTube for video."""
        try:
            if not self.go_to_url("youtube.com"):
                return False
            
            time.sleep(2)
            self.accessibility.activate_app(self.browser)
            time.sleep(0.2)
            
            self.accessibility.type_text(query, delay=0.03)
            time.sleep(0.3)
            self.accessibility.press_key("return")
            time.sleep(2)
            
            # Click first video
            subprocess.run(['osascript', '-e', '''
                tell application "System Events"
                    key code 125
                    delay 0.3
                    key code 36
                end tell
            '''], timeout=2)
            
            return True
        except:
            return False
    
    def search_google(self, query: str) -> bool:
        """Perform Google search."""
        try:
            if not self.go_to_url("google.com"):
                return False
            
            time.sleep(1)
            self.accessibility.activate_app(self.browser)
            time.sleep(0.2)
            
            self.accessibility.type_text(query, delay=0.03)
            time.sleep(0.3)
            self.accessibility.press_key("return")
            time.sleep(2)
            
            return True
        except:
            return False
    
    def open_website(self, website: str) -> bool:
        """Open a specific website."""
        return self.go_to_url(website)

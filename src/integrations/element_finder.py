"""
Element Finder Module
- Interact with macOS apps via Accessibility APIs
- Type text, press keys, control UI elements
- Uses AppleScript through osascript
"""

import subprocess
import time
from typing import Optional


class AccessibilityHelper:
    """
    macOS Accessibility API wrapper
    Controls applications through AppleScript
    """
    
    @staticmethod
    def get_frontmost_app() -> str:
        """Get name of currently active application."""
        script = """
        tell application "System Events"
            get name of first application process whose frontmost is true
        end tell
        """
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Error getting frontmost app: {e}")
            return ""
    
    @staticmethod
    def type_text(text: str, delay: float = 0.05) -> bool:
        """Type text character by character."""
        try:
            for char in text:
                if char == '"':
                    subprocess.run(['osascript', '-e', 'keystroke "\\"'], timeout=1)
                else:
                    subprocess.run(['osascript', '-e', f'keystroke "{char}"'], timeout=1)
                time.sleep(delay)
            return True
        except Exception as e:
            print(f"Error typing text: {e}")
            return False
    
    @staticmethod
    def press_key(key: str) -> bool:
        """Press a single key."""
        key_map = {
            "return": "return",
            "enter": "return",
            "tab": "tab",
            "space": "space",
            "delete": "delete",
            "escape": "escape",
        }
        
        mapped_key = key_map.get(key.lower())
        if not mapped_key:
            return False
        
        try:
            subprocess.run(['osascript', '-e', f'keystroke "{mapped_key}"'], timeout=1)
            return True
        except Exception as e:
            print(f"Error pressing key: {e}")
            return False
    
    @staticmethod
    def key_combination(key: str, modifiers: list) -> bool:
        """Press key with modifiers (Cmd, Option, Shift)."""
        try:
            mod_string = ', '.join(f'{m} down' for m in modifiers)
            script = f'keystroke "{key}" using {{{mod_string}}}'
            subprocess.run(['osascript', '-e', script], timeout=1)
            return True
        except Exception as e:
            print(f"Error with key combination: {e}")
            return False
    
    @staticmethod
    def wait_for_app(app_name: str, timeout: int = 5) -> bool:
        """Wait for application to launch and become active."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if AccessibilityHelper.get_frontmost_app() == app_name:
                time.sleep(0.5)
                return True
            time.sleep(0.1)
        
        return False
    
    @staticmethod
    def activate_app(app_name: str) -> bool:
        """Bring app to foreground."""
        try:
            script = f'tell application "{app_name}" to activate'
            subprocess.run(['osascript', '-e', script], timeout=2)
            time.sleep(0.3)
            return True
        except Exception as e:
            print(f"Error activating {app_name}: {e}")
            return False

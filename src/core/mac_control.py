"""
Mac Control Module
Handles macOS system interactions including app launching and system controls
"""

import subprocess
import os
from typing import Optional, Tuple


class MacController:
    """Controls macOS system functions via shell commands and AppleScript."""
    
    # App name mappings (common names -> actual app names)
    APP_MAPPINGS = {
        # Browsers
        "chrome": "Google Chrome",
        "safari": "Safari",
        "firefox": "Firefox",
        "brave": "Brave Browser",
        
        # Development
        "vscode": "Visual Studio Code",
        "vs code": "Visual Studio Code",
        "code": "Visual Studio Code",
        "pycharm": "PyCharm",
        "xcode": "Xcode",
        "terminal": "Terminal",
        "iterm": "iTerm",
        
        # Productivity
        "notion": "Notion",
        "slack": "Slack",
        "discord": "Discord",
        "spotify": "Spotify",
        "notes": "Notes",
        "mail": "Mail",
        "calendar": "Calendar",
        
        # System
        "finder": "Finder",
        "settings": "System Settings",
        "preferences": "System Settings",
    }
    
    def __init__(self, allowed_apps: Optional[list] = None):
        """
        Initialize Mac controller.
        
        Args:
            allowed_apps: Whitelist of allowed apps. None = allow all.
        """
        self.allowed_apps = allowed_apps
    
    def open_app(self, app_name: str) -> Tuple[bool, str]:
        """
        Launch an application.
        
        Args:
            app_name: Name of the app to launch (case-insensitive)
        
        Returns:
            (success: bool, message: str)
        """
        # Normalize app name
        app_name_lower = app_name.lower().strip()
        
        # Check mapping
        actual_app_name = self.APP_MAPPINGS.get(app_name_lower, app_name)
        
        # Check whitelist
        if self.allowed_apps and actual_app_name not in self.allowed_apps:
            return (False, f"Application '{actual_app_name}' is not in the allowed list, sir.")
        
        try:
            # Use macOS 'open' command
            result = subprocess.run(
                ["open", "-a", actual_app_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return (True, f"Opened {actual_app_name}, sir.")
            else:
                # App not found
                return (False, f"I'm afraid I couldn't locate '{actual_app_name}', sir. Please verify the application is installed.")
                
        except subprocess.TimeoutExpired:
            return (False, f"Opening {actual_app_name} timed out, sir.")
        except Exception as e:
            return (False, f"I encountered an error opening {actual_app_name}: {e}")
    
    def close_app(self, app_name: str) -> Tuple[bool, str]:
        """
        Close/quit an application.
        
        Args:
            app_name: Name of the app to close (case-insensitive)
        
        Returns:
            (success: bool, message: str)
        """
        # Normalize app name
        app_name_lower = app_name.lower().strip()
        
        # Check mapping
        actual_app_name = self.APP_MAPPINGS.get(app_name_lower, app_name)
        
        try:
            # Use pkill to close the app
            result = subprocess.run(
                ["pkill", "-i", actual_app_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # pkill returns 0 if it found and killed processes
            if result.returncode == 0:
                return (True, f"Closed {actual_app_name}, sir.")
            else:
                return (False, f"I'm afraid {actual_app_name} doesn't appear to be running, sir.")
                
        except subprocess.TimeoutExpired:
            return (False, f"Closing {actual_app_name} timed out, sir.")
        except Exception as e:
            return (False, f"I encountered an error closing {actual_app_name}: {e}")
    
    def set_volume(self, level: int) -> Tuple[bool, str]:
        """
        Set system volume.
        
        Args:
            level: Volume level (0-100)
        
        Returns:
            (success: bool, message: str)
        """
        if not 0 <= level <= 100:
            return (False, "Volume must be between 0 and 100, sir.")
        
        try:
            # Convert to macOS scale (0-7)
            mac_volume = int((level / 100) * 7)
            
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {mac_volume}"],
                check=True,
                capture_output=True
            )
            
            return (True, f"Volume set to {level}%, sir.")
        except Exception as e:
            return (False, f"I'm afraid I couldn't adjust the volume: {e}")
    
    def adjust_volume(self, direction: str) -> Tuple[bool, str]:
        """
        Adjust volume up or down.
        
        Args:
            direction: "up" or "down"
        
        Returns:
            (success: bool, message: str)
        """
        try:
            if direction == "up":
                script = "set volume output volume (output volume of (get volume settings) + 1)"
            else:
                script = "set volume output volume (output volume of (get volume settings) - 1)"
            
            subprocess.run(
                ["osascript", "-e", script],
                check=True,
                capture_output=True
            )
            
            return (True, f"Volume adjusted {direction}, sir.")
        except Exception as e:
            return (False, f"I'm afraid I couldn't adjust the volume: {e}")
    
    def set_brightness(self, level: int) -> Tuple[bool, str]:
        """
        Set display brightness.
        
        Args:
            level: Brightness level (0-100)
        
        Returns:
            (success: bool, message: str)
        """
        if not 0 <= level <= 100:
            return (False, "Brightness must be between 0 and 100, sir.")
        
        try:
            # Convert to macOS scale (0.0-1.0)
            mac_brightness = level / 100
            
            subprocess.run(
                ["osascript", "-e", f"tell application \"System Events\" to set brightness of display 1 to {mac_brightness}"],
                check=True,
                capture_output=True
            )
            
            return (True, f"Brightness set to {level}%, sir.")
        except Exception as e:
            return (False, f"I'm afraid I couldn't adjust the brightness: {e}")
    
    def get_available_apps(self) -> list:
        """Returns list of apps in the mapping."""
        return list(set(self.APP_MAPPINGS.values()))

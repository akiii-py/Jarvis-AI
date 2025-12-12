"""
Spotify Controller Module
- Play songs, playlists, artists
- Control playback (pause, resume, next, previous)
- Get current track information
"""

import subprocess
import time
from typing import Optional
from .element_finder import AccessibilityHelper


class SpotifyController:
    """Control Spotify application through automation."""
    
    def __init__(self, mac_control):
        self.mac_control = mac_control
        self.accessibility = AccessibilityHelper()
    
    def open_spotify(self) -> bool:
        """Open Spotify application."""
        try:
            self.mac_control.open_app("Spotify")
            return self.accessibility.wait_for_app("Spotify", timeout=3)
        except Exception as e:
            print(f"Error opening Spotify: {e}")
            return False
    
    def search_and_play(self, query: str) -> bool:
        """Search Spotify and play first result."""
        try:
            if not self.open_spotify():
                return False
            
            time.sleep(0.5)
            self.accessibility.activate_app("Spotify")
            time.sleep(0.5)
            
            # Use AppleScript to search and play
            script = f'''
            tell application "System Events"
                tell process "Spotify"
                    -- Open search with Cmd+K
                    keystroke "k" using command down
                    delay 0.5
                    
                    -- Type the search query
                    keystroke "{query}"
                    delay 1
                    
                    -- Press return to search
                    keystroke return
                    delay 1
                    
                    -- Arrow down to first result
                    key code 125
                    delay 0.3
                    
                    -- Press return to play
                    keystroke return
                end tell
            end tell
            '''
            
            subprocess.run(['osascript', '-e', script], timeout=5, check=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Spotify search AppleScript error: {e}")
            return False
        except Exception as e:
            print(f"Spotify search error: {e}")
            return False
    
    def pause(self) -> bool:
        """Pause current playback."""
        try:
            script = 'tell application "Spotify" to pause'
            subprocess.run(['osascript', '-e', script], timeout=1)
            return True
        except:
            return False
    
    def play(self) -> bool:
        """Resume playback."""
        try:
            script = 'tell application "Spotify" to play'
            subprocess.run(['osascript', '-e', script], timeout=1)
            return True
        except:
            return False
    
    def next_track(self) -> bool:
        """Skip to next track."""
        try:
            script = 'tell application "Spotify" to next track'
            subprocess.run(['osascript', '-e', script], timeout=1)
            return True
        except:
            return False
    
    def previous_track(self) -> bool:
        """Go to previous track."""
        try:
            script = 'tell application "Spotify" to previous track'
            subprocess.run(['osascript', '-e', script], timeout=1)
            return True
        except:
            return False
    
    def get_current_track(self) -> Optional[str]:
        """Get currently playing track info."""
        try:
            script = '''
            tell application "Spotify"
                set current_track to current track
                set track_name to name of current_track
                set artist_name to artist of current_track
                return track_name & " by " & artist_name
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            return result.stdout.strip() if result.stdout else None
        except:
            return None

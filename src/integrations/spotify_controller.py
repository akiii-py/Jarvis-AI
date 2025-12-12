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
        """
        Search Spotify and play the track directly (not in playlist context).
        
        Uses Spotlight URL scheme to play individual track, preventing playlist auto-play.
        """
        try:
            if not self.open_spotify():
                return False
            
            time.sleep(0.5)
            self.accessibility.activate_app("Spotify")
            time.sleep(0.5)
            
            # Method 1: Use Spotify's search and play directly via AppleScript
            # This plays the song individually, not in a playlist context
            script = f'''
            tell application "Spotify"
                activate
                
                -- Play the track by searching
                play track "spotify:search:{query.replace('"', '\\"')}"
            end tell
            '''
            
            try:
                subprocess.run(['osascript', '-e', script], timeout=5, check=True)
                time.sleep(1)
                return True
            except:
                # Fallback to UI navigation method
                print("Direct play failed, trying UI navigation...")
                return self._ui_search_and_play(query)
            
        except Exception as e:
            print(f"Spotify search error: {e}")
            return False
    
    def _ui_search_and_play(self, query: str) -> bool:
        """
        Fallback method: Use UI navigation to search and play.
        Tries to select from Songs section to avoid playlist context.
        """
        try:
            # Type the query character by character with delay to ensure it all gets typed
            escaped_query = query.replace('"', '\\"')
            
            script = f'''
            tell application "System Events"
                tell process "Spotify"
                    -- Open search with Cmd+K
                    keystroke "k" using command down
                    delay 1.0
                    
                    -- Clear any existing search
                    keystroke "a" using command down
                    delay 0.2
                    key code 51
                    delay 0.3
                    
                    -- Type the search query slowly
                    keystroke "{escaped_query}"
                    delay 2.0
                    
                    -- Press return to search
                    keystroke return
                    delay 1.5
                    
                    -- Arrow down to first song result
                    -- Skip the "Top Result" which might be a playlist
                    key code 125
                    delay 0.3
                    key code 125
                    delay 0.3
                    key code 125
                    delay 0.3
                    
                    -- Press return to play the song
                    keystroke return
                end tell
            end tell
            '''
            
            subprocess.run(['osascript', '-e', script], timeout=15, check=True)
            return True
            
        except Exception as e:
            print(f"UI navigation error: {e}")
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

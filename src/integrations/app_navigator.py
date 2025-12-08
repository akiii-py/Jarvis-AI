"""
App Navigator Module
- Main controller for app navigation commands
- Routes user input to appropriate handler
"""

import re
from typing import Tuple
from .spotify_controller import SpotifyController
from .browser_controller import BrowserController
from .app_automator import AppAutomator


class AppNavigator:
    """Master controller for all app navigation and automation."""
    
    def __init__(self, mac_control, personality):
        self.mac_control = mac_control
        self.personality = personality
        
        # Initialize controllers
        self.spotify = SpotifyController(mac_control)
        self.browser = BrowserController(mac_control)
        self.automator = AppAutomator(mac_control)
    
    def handle_app_navigation(self, user_input: str) -> Tuple[bool, str]:
        """Main router for app navigation commands."""
        lower_input = user_input.lower().strip()
        
        # Spotify commands
        if any(word in lower_input for word in ["spotify", "play", "pause", "next", "previous"]):
            return self._handle_spotify(user_input)
        
        # YouTube commands
        if "youtube" in lower_input or ("video" in lower_input and "search" in lower_input):
            return self._handle_youtube(user_input)
        
        # Google search
        if ("search" in lower_input or "google" in lower_input) and "youtube" not in lower_input:
            return self._handle_google_search(user_input)
        
        # WhatsApp
        if "whatsapp" in lower_input or ("message" in lower_input and "to" in lower_input):
            return self._handle_whatsapp(user_input)
        
        # Email
        if "email" in lower_input or "mail" in lower_input:
            return self._handle_email(user_input)
        
        # Website visit
        if "open website" in lower_input or "visit" in lower_input or "go to" in lower_input:
            return self._handle_website(user_input)
        
        return (False, "")
    
    def _handle_spotify(self, user_input: str) -> Tuple[bool, str]:
        """Handle Spotify commands."""
        lower_input = user_input.lower()
        
        # Check for common Spotify typos
        has_spotify = any(word in lower_input for word in ["spotify", "spoify", "spotfy", "spotifi"])
        
        # PLAY COMMAND - more flexible detection
        if "play" in lower_input:
            # Extract song/playlist name
            query = re.sub(r'(play|on spotify|spotify|spoify|spotfy|song|playlist|on|the)', '', lower_input).strip()
            if not query:
                return (True, "I didn't catch what to play, sir.")
            
            success = self.spotify.search_and_play(query)
            if success:
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Now playing {query} on Spotify, sir.")
            return (True, f"I couldn't find {query} on Spotify, sir.")
        
        # PAUSE COMMAND
        elif "pause" in lower_input:
            self.spotify.pause()
            return (True, "Pausing Spotify, sir.")
        
        # RESUME/CONTINUE COMMAND
        elif "resume" in lower_input or "continue" in lower_input:
            self.spotify.play()
            return (True, "Resuming playback, sir.")
        
        # NEXT TRACK COMMAND
        elif "next" in lower_input or "skip" in lower_input:
            self.spotify.next_track()
            return (True, "Skipping to next track, sir.")
        
        # PREVIOUS TRACK COMMAND
        elif "previous" in lower_input or "back" in lower_input:
            self.spotify.previous_track()
            return (True, "Going to previous track, sir.")
        
        # CURRENT TRACK COMMAND
        elif "current" in lower_input or "now playing" in lower_input or "what" in lower_input:
            current = self.spotify.get_current_track()
            if current:
                return (True, f"Currently playing: {current}, sir.")
            return (True, "Unable to retrieve current track, sir.")
        
        return (False, "")
    
    def _handle_youtube(self, user_input: str) -> Tuple[bool, str]:
        """Handle YouTube search."""
        query = re.sub(r'(search|find|watch|on youtube|youtube|video)', '', user_input.lower()).strip()
        if not query:
            return (True, "I didn't catch what to search for, sir.")
        
        success = self.browser.search_youtube(query)
        if success:
            ack = self.personality.get_acknowledgment()
            return (True, f"{ack} Searching YouTube for {query}, sir.")
        return (True, "I couldn't search YouTube, sir.")
    
    def _handle_google_search(self, user_input: str) -> Tuple[bool, str]:
        """Handle Google search."""
        query = re.sub(r'(search|google|find|look up)', '', user_input.lower()).strip()
        if not query:
            return (True, "I didn't catch what to search for, sir.")
        
        success = self.browser.search_google(query)
        if success:
            ack = self.personality.get_acknowledgment()
            return (True, f"{ack} Searching for {query}, sir.")
        return (True, "I couldn't search, sir.")
    
    def _handle_whatsapp(self, user_input: str) -> Tuple[bool, str]:
        """Handle WhatsApp messages."""
        pattern = r'(?:message|whatsapp).*?(?:to|for)\s+(\w+)\s+(?:saying)?\s*(.+?)$'
        match = re.search(pattern, user_input, re.IGNORECASE)
        
        if match:
            contact = match.group(1).strip()
            message = match.group(2).strip()
            
            success = self.automator.send_whatsapp_message(contact, message)
            if success:
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Message sent to {contact}, sir.")
            return (True, f"I couldn't send the message to {contact}, sir.")
        
        return (False, "")
    
    def _handle_email(self, user_input: str) -> Tuple[bool, str]:
        """Handle email search."""
        if "search" in user_input.lower():
            query = re.sub(r'(search|mail|email|for|in)', '', user_input.lower()).strip()
            if not query:
                return (True, "I didn't catch what to search for, sir.")
            
            success = self.automator.open_email_search(query)
            if success:
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Searching emails for {query}, sir.")
        
        return (False, "")
    
    def _handle_website(self, user_input: str) -> Tuple[bool, str]:
        """Handle website visits."""
        pattern = r'(?:open|visit|go to).*?([\w\-]+\.[\w\.]{2,})'
        match = re.search(pattern, user_input, re.IGNORECASE)
        
        if match:
            website = match.group(1).strip()
            success = self.browser.open_website(website)
            if success:
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Opening {website}, sir.")
            return (True, f"I couldn't open {website}, sir.")
        
        return (False, "")

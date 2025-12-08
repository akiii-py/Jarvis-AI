"""
Smart Focus Mode
Blocks distractions during work sessions
"""

from datetime import datetime, timedelta
from typing import List, Optional


class FocusMode:
    """Manages focus mode sessions to block distractions."""
    
    def __init__(self, duration_minutes: int, allowed_apps: List[str], mode: str = "coding"):
        """
        Initialize focus mode.
        
        Args:
            duration_minutes: How long to stay focused
            allowed_apps: Apps that can be opened during focus
            mode: Type of focus (coding, research, study)
        """
        self.duration = duration_minutes
        self.allowed_apps = [app.lower() for app in allowed_apps]
        self.mode = mode
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)
        self.paused = False
        self.interruption_count = 0
        
    def is_active(self) -> bool:
        """Check if focus mode is still active."""
        if self.paused:
            return False
        return datetime.now() < self.end_time
    
    def time_remaining(self) -> int:
        """Get minutes remaining in focus session."""
        if not self.is_active():
            return 0
        remaining = (self.end_time - datetime.now()).total_seconds() / 60
        return max(0, int(remaining))
    
    def is_app_allowed(self, app_name: str) -> bool:
        """Check if an app is allowed during focus mode."""
        app_lower = app_name.lower()
        
        # Check exact match
        if app_lower in self.allowed_apps:
            return True
        
        # Check partial match
        for allowed in self.allowed_apps:
            if allowed in app_lower or app_lower in allowed:
                return True
        
        return False
    
    def handle_blocked_request(self, app_name: str) -> str:
        """Generate response for blocked app request."""
        self.interruption_count += 1
        
        remaining = self.time_remaining()
        
        responses = [
            f"I'm afraid that would break focus, sir. {remaining} minutes remaining.",
            f"You're in focus mode, sir. Perhaps after the session? ({remaining} min left)",
            f"That app is blocked during focus, sir. {remaining} minutes to go.",
        ]
        
        # More stern if multiple interruptions
        if self.interruption_count > 3:
            return f"Sir, you've requested distractions {self.interruption_count} times. Shall I end focus mode?"
        
        import random
        return random.choice(responses)
    
    def pause(self):
        """Pause focus mode temporarily."""
        self.paused = True
    
    def resume(self):
        """Resume focus mode."""
        self.paused = False
    
    def end_summary(self) -> str:
        """Generate end-of-session summary."""
        duration = (datetime.now() - self.start_time).total_seconds() / 60
        
        summary = f"""Focus session complete, sir.
- Duration: {int(duration)} minutes
- Mode: {self.mode}
- Interruption attempts: {self.interruption_count}
"""
        
        if self.interruption_count == 0:
            summary += "\nExcellent focus, sir. Well done."
        elif self.interruption_count < 3:
            summary += "\nGood discipline, sir."
        else:
            summary += "\nPerhaps shorter sessions next time, sir?"
        
        return summary

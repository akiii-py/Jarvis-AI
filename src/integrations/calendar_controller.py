"""
Calendar Controller Module
- Interact with macOS Calendar app via AppleScript
- Create events/reminders
- Parse natural language dates
"""

import subprocess
import dateparser
from datetime import datetime
import json
import logging

class CalendarController:
    """Controls macOS Calendar app using AppleScript."""
    
    def __init__(self):
        self.logger = logging.getLogger("Jarvis.Calendar")
    
    def create_event(self, summary: str, start_time_str: str, duration_mins: int = 60) -> tuple[bool, str]:
        """
        Create an event/meeting in the default calendar.
        
        Args:
            summary: Title of the event
            start_time_str: Natural language date string (e.g. "tomorrow at 5pm")
            duration_mins: Duration in minutes (default 60)
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Parse the natural language date
            start_date = dateparser.parse(
                start_time_str,
                settings={'PREFER_DATES_FROM': 'future'}
            )
            
            if not start_date:
                return (False, f"I couldn't understand the date and time '{start_time_str}', sir.")
            
            # Calculate end time
            end_date = start_date.replace(minute=(start_date.minute + duration_mins) % 60)
            # Handle hour overflow roughly (for AppleScript we just need the end date)
            # A cleaner way is using timedelta but we'll let AppleScript handle the duration logic if possible
            # Actually, let's just format the start date for AppleScript and specify end date
            
            from datetime import timedelta
            end_date = start_date + timedelta(minutes=duration_mins)
            
            # Format dates for AppleScript: "jobname, monthname day, year at hours:minutes:seconds"
            # However, AppleScript date parsing can be tricky depending on locale.
            # A safer generic format for AppleScript is usually "MM/DD/YYYY HH:MM:SS"
            
            apple_script_date_start = start_date.strftime("%m/%d/%Y %H:%M:%S")
            apple_script_date_end = end_date.strftime("%m/%d/%Y %H:%M:%S")
            
            # AppleScript to create event
            script = f'''
            tell application "Calendar"
                tell calendar "Calendar"
                    make new event at end with properties {{summary:"{summary}", start date:date "{apple_script_date_start}", end date:date "{apple_script_date_end}"}}
                end tell
            end tell
            '''
            
            # Try specific calendar names if "Calendar" fails or check default
            # Actually, getting the default calendar is safer
            script = f'''
            tell application "Calendar"
                set defaultCal to first calendar
                tell defaultCal
                    make new event at end with properties {{summary:"{summary}", start date:date "{apple_script_date_start}", end date:date "{apple_script_date_end}"}}
                end tell
            end tell
            '''
            
            # Run the script
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            
            if result.returncode == 0:
                fmt_date = start_date.strftime("%A, %B %d at %I:%M %p")
                return (True, f"Scheduled '{summary}' for {fmt_date}.")
            else:
                self.logger.error(f"AppleScript error: {result.stderr}")
                return (False, "I encountered an error accessing your calendar, sir. Please check permissions.")
                
        except Exception as e:
            self.logger.error(f"Calendar error: {e}")
            return (False, f"An error occurred while scheduling: {str(e)}")

    def get_todays_events(self) -> str:
        """Get list of events for today."""
        # TODO: Implement reading logic
        return "Reading calendar is not yet implemented, sir."

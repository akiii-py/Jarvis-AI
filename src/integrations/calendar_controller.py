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
            
            # Format dates for AppleScript using components to avoid locale issues (MM/DD vs DD/MM)
            # We construct a base date independently of string parsing
            
            script = f'''
            tell application "Calendar"
                set preferredCalendars to {{"akshatg570@gmail.com", "Calendar", "Home", "Work"}}
                set targetCalendar to missing value
                
                -- Try to find a preferred calendar
                repeat with calName in preferredCalendars
                    try
                        set targetCalendar to calendar (calName as string)
                        exit repeat
                    end try
                end repeat
                
                if targetCalendar is missing value then
                    set targetCalendar to first calendar
                end if
                
                -- robust date construction
                set startDate to current date
                set year of startDate to {start_date.year}
                set month of startDate to {start_date.month}
                set day of startDate to {start_date.day}
                set time of startDate to ({start_date.hour} * 3600 + {start_date.minute} * 60)
                
                set endDate to current date
                set year of endDate to {end_date.year}
                set month of endDate to {end_date.month}
                set day of endDate to {end_date.day}
                set time of endDate to ({end_date.hour} * 3600 + {end_date.minute} * 60)
                
                set targetName to name of targetCalendar
                
                tell targetCalendar
                    make new event at end with properties {{summary:"{summary}", start date:startDate, end date:endDate}}
                end tell
                
                return targetName
            end tell
            '''
            
            # Run the script
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            
            if result.returncode == 0:
                calendar_name = result.stdout.strip()
                # Include YEAR in the confirmation to fail-safe user's concern
                fmt_date = start_date.strftime("%A, %B %d, %Y at %I:%M %p")
                return (True, f"Scheduled '{summary}' on {fmt_date} ({calendar_name} calendar).")
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

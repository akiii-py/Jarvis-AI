"""
Morning Briefing Protocol
Generates a daily summary of weather, news, and system status.
"""

import requests
import psutil
import datetime
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

class MorningBriefing:
    """Handles generation of the morning briefing."""
    
    def __init__(self):
        self.location = {"lat": 28.6139, "lon": 77.2090} # Default to New Delhi (can be configured)
        
    def get_weather(self) -> str:
        """Get current weather from Open-Meteo."""
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.location['lat']}&longitude={self.location['lon']}&current=temperature_2m,weather_code"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            temp = data['current']['temperature_2m']
            code = data['current']['weather_code']
            
            # WMO Weather interpretation codes (simplified)
            conditions = "clear"
            if code > 0: conditions = "cloudy" 
            if code > 40: conditions = "foggy"
            if code > 50: conditions = "rainy"
            if code > 70: conditions = "snowy"
            if code > 90: conditions = "stormy"
            
            return f"{temp}°C and {conditions}"
        except Exception as e:
            return f"unavailable ({e})"

    def get_news(self, limit: int = 3) -> List[str]:
        """Get top headlines from Google News RSS."""
        headlines = []
        try:
            # Tech news provided by default
            url = "https://news.google.com/rss/search?q=technology&hl=en-US&gl=US&ceid=US:en"
            response = requests.get(url, timeout=5)
            
            root = ET.fromstring(response.content)
            count = 0
            
            for item in root.findall('.//item'):
                if count >= limit:
                    break
                title = item.find('title').text
                # Remove source name if present (e.g. "Title - Source")
                if " - " in title:
                    title = title.rsplit(" - ", 1)[0]
                headlines.append(title)
                count += 1
                
        except Exception as e:
            headlines.append(f"Could not fetch news: {e}")
            
        return headlines

    def get_system_status(self) -> str:
        """Get battery and CPU status."""
        status = []
        
        # Battery
        try:
            battery = psutil.sensors_battery()
            if battery:
                plugged = "charging" if battery.power_plugged else "on battery"
                status.append(f"Battery is at {battery.percent}% and {plugged}")
        except:
            pass
            
        # CPU
        cpu_usage = psutil.cpu_percent(interval=0.1)
        status.append(f"Systems running at {cpu_usage}% capacity")
        
        return ". ".join(status)

    def generate_briefing(self) -> str:
        """Compile the full briefing."""
        date_str = datetime.datetime.now().strftime("%A, %B %d")
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        
        parts = []
        parts.append(f"Good morning, sir. It is {time_str} on {date_str}.")
        
        # Weather
        weather = self.get_weather()
        parts.append(f"Current conditions are {weather}.")
        
        # System
        sys_status = self.get_system_status()
        parts.append(f"System status: {sys_status}.")
        
        # News
        news = self.get_news()
        if news:
            parts.append("Here are today's top tech headlines:")
            for i, headline in enumerate(news, 1):
                parts.append(f"{headline}.")
                
        # Closing
        parts.append("I am ready to assist you.")
        
        return "\n".join(parts)

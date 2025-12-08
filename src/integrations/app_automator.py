"""
App Automator Module
- Send WhatsApp messages
- Search emails
- Create calendar events
"""

import subprocess
import time
from .element_finder import AccessibilityHelper


class AppAutomator:
    """General app automation for macOS applications."""
    
    def __init__(self, mac_control):
        self.mac_control = mac_control
        self.accessibility = AccessibilityHelper()
    
    def send_whatsapp_message(self, contact_name: str, message: str) -> bool:
        """Send WhatsApp message to contact."""
        try:
            self.mac_control.open_app("WhatsApp")
            time.sleep(1)
            self.accessibility.activate_app("WhatsApp")
            time.sleep(0.3)
            
            # Cmd+N to start new chat
            subprocess.run(['osascript', '-e', 'keystroke "n" using command down'], timeout=1)
            time.sleep(0.5)
            
            self.accessibility.type_text(contact_name, delay=0.04)
            time.sleep(0.5)
            self.accessibility.press_key("return")
            time.sleep(0.5)
            
            self.accessibility.type_text(message, delay=0.03)
            time.sleep(0.3)
            
            # Cmd+Enter to send
            subprocess.run(['osascript', '-e', 'keystroke "return" using command down'], timeout=1)
            
            return True
        except:
            return False
    
    def open_email_search(self, search_query: str) -> bool:
        """Search emails in Mail.app."""
        try:
            self.mac_control.open_app("Mail")
            time.sleep(0.5)
            self.accessibility.activate_app("Mail")
            time.sleep(0.3)
            
            # Cmd+F for search
            subprocess.run(['osascript', '-e', 'keystroke "f" using command down'], timeout=1)
            time.sleep(0.3)
            
            self.accessibility.type_text(search_query, delay=0.03)
            time.sleep(0.3)
            self.accessibility.press_key("return")
            time.sleep(1)
            
            return True
        except:
            return False

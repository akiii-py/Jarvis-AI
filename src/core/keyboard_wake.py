"""
Keyboard-based Wake System
Simple and reliable alternative to wake word detection
Press SPACE or ENTER to activate JARVIS
"""

import sys
import select
import termios
import tty


class KeyboardWakeListener:
    """
    Simple keyboard-based wake system.
    Press SPACE or ENTER to activate JARVIS.
    """
    
    def __init__(self):
        """Initialize keyboard listener."""
        self.old_settings = None
        print("🎹 Keyboard wake system initialized")
        print("   Press SPACE or ENTER to talk to JARVIS")
        print("   Press 'q' to quit")
    
    def listen(self) -> bool:
        """
        Wait for user to press SPACE or ENTER.
        
        Returns:
            True when activation key is pressed
            False if quit key is pressed
        """
        try:
            # Save terminal settings
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            
            print("\n⏸️  Press SPACE or ENTER to activate JARVIS...")
            
            while True:
                # Check if input is available
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    
                    # Space or Enter activates
                    if key in [' ', '\n', '\r']:
                        print("✅ Activated! Listening...")
                        return True
                    
                    # 'q' quits
                    elif key.lower() == 'q':
                        print("👋 Goodbye!")
                        return False
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return False
        
        finally:
            # Restore terminal settings
            if self.old_settings:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
    
    def close(self):
        """Clean up resources."""
        if self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

from src.core.memory import ConversationMemory
from src.core.llm import LLMClient
from src.core.voice_io import VoiceInput, VoiceOutput
from src.core.wake_word import WakeWordListener
from src.core.personality import JarvisPersonality
from src.core.mac_control import MacController
from src.config.config import Config
import sys
import re
from datetime import datetime


class Jarvis:
    def __init__(self):
        self.memory = ConversationMemory()
        self.llm = LLMClient()
        self.current_mode = "coding"  # Default mode
        self.session_start_time = None  # Track session duration
        self.interaction_count = 0  # Track number of interactions
        self.mac_control = MacController(allowed_apps=Config.ALLOWED_APPS)
        print(f"Jarvis initialized with model: {Config.DEFAULT_MODEL}")
        print(f"Current mode: {self.current_mode}")


    def switch_model(self, mode: str) -> bool:
        """Switch to a different model based on mode."""
        if mode not in Config.MODEL_PROFILES:
            print(f"Unknown mode: {mode}. Available: {list(Config.MODEL_PROFILES.keys())}")
            return False
        
        new_model = Config.MODEL_PROFILES[mode]
        self.llm = LLMClient(model=new_model)
        self.current_mode = mode
        print(f"Switched to {mode} mode using model: {new_model}")
        return True


    def _extract_app_name(self, user_input: str) -> tuple[bool, str]:
        """
        Extract app name from natural language commands.
        Handles: "launch mail", "can you launch mail for me", "please open chrome", etc.
        
        Returns: (success: bool, app_name: str)
        """
        lower_input = user_input.lower().strip()
        
        # Patterns to detect app launch commands
        patterns = [
            r"(?:can you\s+)?(?:please\s+)?(?:open|launch|start|run)\s+(?:the\s+)?(.+?)(?:\s+(?:app|application|for\s+me|please))?$",
            r"(?:open|launch|start|run)\s+(?:the\s+)?(.+?)$",
            r"(?:bring up|fire up)\s+(?:the\s+)?(.+?)$",
            r"i (?:need|want)\s+you to (?:open|launch|start)\s+(.+?)$",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, lower_input, re.IGNORECASE)
            if match:
                raw_app_name = match.group(1).strip()
                
                # Clean up common filler words
                filler_words = {"the", "app", "application", "for me", "please", "can you", "could you"}
                words = raw_app_name.split()
                cleaned_words = [w for w in words if w.lower() not in filler_words]
                app_name = " ".join(cleaned_words).strip()
                
                if app_name:
                    return True, app_name
        
        return False, ""


    def _extract_close_app(self, user_input: str) -> tuple[bool, str]:
        """
        Extract app name from close/quit commands.
        Handles: "close vscode", "quit discord", "shut down chrome"
        
        Returns: (success: bool, app_name: str)
        """
        lower_input = user_input.lower().strip()
        
        # Patterns to detect close/quit commands
        patterns = [
            r"(?:close|quit|exit|shut down)\s+(?:the\s+)?(.+?)(?:\s+app)?$",
            r"(?:please\s+)?(?:stop|kill)\s+(?:the\s+)?(.+?)$",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, lower_input, re.IGNORECASE)
            if match:
                app_name = match.group(1).strip()
                
                # Clean up filler words
                filler_words = {"the", "app", "application"}
                words = app_name.split()
                cleaned_words = [w for w in words if w.lower() not in filler_words]
                app_name = " ".join(cleaned_words).strip()
                
                if app_name:
                    return True, app_name
        
        return False, ""


    def handle_command(self, user_input: str) -> tuple[bool, str]:
        """
        Check if input is a special command.
        Returns (is_command, response)
        
        IMPORTANT: Commands are checked and executed BEFORE sending to LLM.
        This ensures "launch mail" opens Mail instead of getting LLM response.
        """
        lower_input = user_input.lower().strip()
        
        # ============================================================================
        # APP CONTROL COMMANDS - PRIORITY 1 (Check first!)
        # ============================================================================
        
        # Command Chaining - "open chrome and launch mail"
        if " and " in lower_input and any(word in lower_input for word in ["open", "launch", "start", "close", "quit"]):
            # Split by "and" and process each command
            commands = user_input.split(" and ")
            responses = []
            
            for cmd in commands:
                cmd = cmd.strip()
                
                # Try to extract app name for open
                success, app_name = self._extract_app_name(cmd)
                if success:
                    open_success, message = self.mac_control.open_app(app_name)
                    if open_success:
                        responses.append(f"opened {app_name}")
                    continue
                
                # Try to extract app name for close
                success, app_name = self._extract_close_app(cmd)
                if success:
                    close_success, message = self.mac_control.close_app(app_name)
                    if close_success:
                        responses.append(f"closed {app_name}")
            
            if responses:
                ack = JarvisPersonality.get_acknowledgment()
                return (True, f"{ack} I've {' and '.join(responses)}, sir.")
        
        # Open/Launch App Command
        success, app_name = self._extract_app_name(user_input)
        if success:
            open_success, message = self.mac_control.open_app(app_name)
            # Always respond with personality, regardless of success
            if open_success:
                ack = JarvisPersonality.get_acknowledgment()
                return (True, ack)
            else:
                return (True, f"I'm afraid I couldn't locate {app_name}, sir.")
        
        # Close/Quit App Command
        success, app_name = self._extract_close_app(user_input)
        if success:
            close_success, message = self.mac_control.close_app(app_name)
            if close_success:
                ack = JarvisPersonality.get_acknowledgment()
                return (True, ack)
            else:
                return (True, f"I'm afraid I couldn't close {app_name}, sir.")
        
        # ============================================================================
        # VOLUME CONTROL COMMANDS
        # ============================================================================
        
        if "volume up" in lower_input or "increase volume" in lower_input:
            success, message = self.mac_control.adjust_volume("up")
            return (True, message or JarvisPersonality.get_acknowledgment())
        
        elif "volume down" in lower_input or "decrease volume" in lower_input:
            success, message = self.mac_control.adjust_volume("down")
            return (True, message or JarvisPersonality.get_acknowledgment())
        
        elif "volume to full" in lower_input or "max volume" in lower_input or "full volume" in lower_input:
            success, message = self.mac_control.set_volume(100)
            return (True, message or "Volume set to maximum, sir.")
        
        elif "mute" in lower_input or "volume to 0" in lower_input:
            success, message = self.mac_control.set_volume(0)
            return (True, message or "Muted, sir.")
        
        elif "set volume to" in lower_input or "volume to" in lower_input or "turn volume to" in lower_input:
            try:
                words = lower_input.split()
                for word in words:
                    if word.isdigit():
                        level = int(word)
                        if 0 <= level <= 100:
                            success, message = self.mac_control.set_volume(level)
                            return (True, f"Volume set to {level} percent, sir.")
                return (True, "I didn't catch the volume level, sir. Please specify 0 to 100.")
            except:
                return (True, "I'm afraid I couldn't parse that volume command, sir.")
        
        # ============================================================================
        # BRIGHTNESS CONTROL COMMANDS
        # ============================================================================
        
        if "brightness up" in lower_input or "increase brightness" in lower_input:
            success, message = self.mac_control.set_brightness(75)
            return (True, message or "Brightness increased, sir.")
        
        elif "brightness down" in lower_input or "decrease brightness" in lower_input:
            success, message = self.mac_control.set_brightness(25)
            return (True, message or "Brightness decreased, sir.")
        
        elif "set brightness to" in lower_input or "brightness to" in lower_input:
            try:
                words = lower_input.split()
                for word in words:
                    if word.isdigit():
                        level = int(word)
                        if 0 <= level <= 100:
                            success, message = self.mac_control.set_brightness(level)
                            return (True, f"Brightness set to {level} percent, sir.")
                return (True, "I didn't catch the brightness level, sir. Please specify 0 to 100.")
            except:
                return (True, "I'm afraid I couldn't parse that brightness command, sir.")
        
        # ============================================================================
        # MODEL/MODE SWITCHING COMMANDS
        # ============================================================================
        
        if "switch to coding" in lower_input or "coding mode" in lower_input:
            self.switch_model("coding")
            response = JarvisPersonality.get_success_response("with_pride")
            return (True, f"{response} Switched to coding mode, sir.")
        
        elif "switch to research" in lower_input or "research mode" in lower_input:
            self.switch_model("research")
            response = JarvisPersonality.get_success_response("with_pride")
            return (True, f"{response} Switched to research mode, sir.")
        
        elif "switch to general" in lower_input or "general mode" in lower_input:
            self.switch_model("general")
            response = JarvisPersonality.get_success_response("with_pride")
            return (True, f"{response} Switched to general mode, sir.")
        
        elif "what mode" in lower_input or "current mode" in lower_input:
            return (True, f"Currently in {self.current_mode} mode using {self.llm.model}, sir.")
        
        # ============================================================================
        # MEMORY/PREFERENCE COMMANDS
        # ============================================================================
        
        # Name learning
        if "my name is" in lower_input:
            name = user_input.split("my name is", 1)[1].strip().split()[0].capitalize()
            self.memory.save_preferences({"user_name": name})
            response = JarvisPersonality.get_acknowledgment()
            return (True, f"{response} Noted, sir. I shall address you as Mr. {name} from now on.")
        
        # Remember command - save custom facts
        if lower_input.startswith("remember ") or lower_input.startswith("remember that "):
            fact = user_input.split("remember ", 1)[1].strip()
            if fact.startswith("that "):
                fact = fact[5:].strip()
            
            memories = self.memory.preferences.get("custom_memories", [])
            memories.append(fact)
            self.memory.save_preferences({"custom_memories": memories})
            response = JarvisPersonality.get_acknowledgment()
            return (True, f"{response} I've made a note of that: '{fact}'")
        
        # Forget command - clear custom memories
        if "forget that" in lower_input or "forget what i told you" in lower_input:
            self.memory.save_preferences({"custom_memories": []})
            response = JarvisPersonality.get_acknowledgment()
            return (True, f"{response} Custom memories cleared, sir.")
        
        # Clear history
        if "clear history" in lower_input or "forget everything" in lower_input:
            self.memory.clear_history()
            response = JarvisPersonality.get_acknowledgment()
            return (True, f"{response} I've cleared my memory of our previous conversations.")
        
        # ============================================================================
        # NOT A RECOGNIZED COMMAND - Send to LLM
        # ============================================================================
        
        return (False, "")


    def run(self, voice_mode: bool = False):
        """Main interaction loop."""
        print(f"\nJarvis initialized. Voice Mode: {'ON' if voice_mode else 'OFF'}")
        
        if voice_mode:
            try:
                self.voice_input = VoiceInput(model_size=Config.WHISPER_MODEL_SIZE)
                self.voice_output = VoiceOutput(voice=Config.TTS_VOICE)
                
                # Try Porcupine first, fallback to simple detection
                if Config.PICOVOICE_ACCESS_KEY:
                    from src.core.wake_word import WakeWordListener
                    self.wake_word = WakeWordListener()
                    print("Using Porcupine wake word detection")
                else:
                    from src.core.simple_wake import SimplePushToTalk
                    self.wake_word = SimplePushToTalk()
                    print("Using simple voice detection (no API key needed)")
                    
            except Exception as e:
                print(f"Failed to initialize voice modules: {e}")
                print("Falling back to text mode.")
                voice_mode = False


        # JARVIS-style greeting
        greeting = JarvisPersonality.format_greeting(JarvisPersonality.get_time_of_day())
        print(f"\nJarvis: {greeting}\n")
        if voice_mode and hasattr(self, 'voice_output'):
            self.voice_output.speak(greeting)
        
        # Start session timer
        self.session_start_time = datetime.now()
        
        while True:
            try:
                user_input = ""
                
                # Check session duration and show concern if needed
                if self.session_start_time:
                    session_duration = (datetime.now() - self.session_start_time).total_seconds() / 3600
                    if session_duration > 3 and self.interaction_count % 10 == 0:
                        concern = JarvisPersonality.get_concern_phrase("fatigue", f"{int(session_duration)} hours")
                        print(f"\nJarvis: {concern}\n")
                        if voice_mode and hasattr(self, 'voice_output'):
                            self.voice_output.speak(concern)
                
                if voice_mode:
                    print("Waiting for wake word...")
                    if self.wake_word.listen():
                        self.voice_output.speak("Yes?")
                        user_input = self.voice_input.listen()
                        print(f"You (Voice): {user_input}")
                else:
                    user_input = input("You: ").strip()
                
                if user_input.lower() in ["exit", "quit", "that will be all"]:
                    farewell = "Very good, sir. Until next time."
                    print(f"\nJarvis: {farewell}\n")
                    if voice_mode:
                        self.voice_output.speak(farewell)
                    break
                
                if not user_input:
                    continue

                # Increment interaction count
                self.interaction_count += 1

                # ================================================================
                # CRITICAL: Check for commands FIRST (before sending to LLM!)
                # ================================================================
                is_command, response = self.handle_command(user_input)
                
                if is_command:
                    # It's a system command - execute and respond
                    print(f"Jarvis: {response}")
                    if voice_mode and hasattr(self, 'voice_output'):
                        self.voice_output.speak(response)
                    continue
                
                # ================================================================
                # NOT A COMMAND - Send to LLM for conversation
                # ================================================================

                # Add user input to memory
                self.memory.add_turn("user", user_input)

                # Get response from LLM
                print("Jarvis: ", end="", flush=True)
                full_response = ""
                
                # Get custom memories from preferences
                custom_memories = self.memory.preferences.get("custom_memories", [])
                
                # Stream the response
                for chunk in self.llm.chat(self.memory.get_history(), custom_memories=custom_memories):
                    print(chunk, end="", flush=True)
                    full_response += chunk
                
                print()  # Newline after response

                # Speak response if in voice mode
                if voice_mode and hasattr(self, 'voice_output'):
                    self.voice_output.speak(full_response)

                # Add assistant response to memory
                self.memory.add_turn("assistant", full_response)


            except KeyboardInterrupt:
                print("\nJarvis: Goodbye!")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
            finally:
                if voice_mode and 'wake_word' in self.__dict__:
                    pass  # Keep open for loop


    def cleanup(self):
        if hasattr(self, 'wake_word'):
            self.wake_word.close()


if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.run()

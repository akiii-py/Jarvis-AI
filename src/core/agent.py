from src.core.memory import ConversationMemory
from src.core.llm import LLMClient
from src.core.voice_io import VoiceInput, VoiceOutput
from src.core.wake_word import WakeWordListener
from src.core.personality import JarvisPersonality
from src.config.config import Config
import sys

class Jarvis:
    def __init__(self):
        self.memory = ConversationMemory()
        self.llm = LLMClient()
        self.current_mode = "coding"  # Default mode
        self.session_start_time = None  # Track session duration
        self.interaction_count = 0  # Track number of interactions
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

    def handle_command(self, user_input: str) -> tuple[bool, str]:
        """
        Check if input is a special command.
        Returns (is_command, response)
        """
        lower_input = user_input.lower().strip()
        
        # Name learning
        if "my name is" in lower_input:
            # Extract name after "my name is"
            name = user_input.split("my name is", 1)[1].strip().split()[0].capitalize()
            self.memory.save_preferences({"user_name": name})
            return (True, f"Noted, sir. I shall address you as Mr. {name} from now on.")
        
        # Remember command - save custom facts
        if lower_input.startswith("remember ") or lower_input.startswith("remember that "):
            fact = user_input.split("remember ", 1)[1].strip()
            if fact.startswith("that "):
                fact = fact[5:].strip()
            
            # Store in preferences with timestamp
            memories = self.memory.preferences.get("custom_memories", [])
            memories.append(fact)
            self.memory.save_preferences({"custom_memories": memories})
            return (True, f"Understood, sir. I've made a note of that: '{fact}'")
        
        # Forget command - clear custom memories
        if "forget that" in lower_input or "forget what i told you" in lower_input:
            self.memory.save_preferences({"custom_memories": []})
            return (True, "Very good, sir. I've cleared all custom memories.")
        
        # Model switching commands
        if "switch to coding" in lower_input or "coding mode" in lower_input:
            self.switch_model("coding")
            return (True, "Switched to coding mode. Ready for programming tasks!")
        elif "switch to research" in lower_input or "research mode" in lower_input:
            self.switch_model("research")
            return (True, "Switched to research mode. Ready for deep reasoning!")
        elif "switch to general" in lower_input or "general mode" in lower_input:
            self.switch_model("general")
            return (True, "Switched to general mode. Ready for conversation!")
        elif "what mode" in lower_input or "current mode" in lower_input:
            return (True, f"Currently in {self.current_mode} mode using {self.llm.model}")
        elif "clear history" in lower_input or "forget everything" in lower_input:
            self.memory.clear_history()
            return (True, "Very good, sir. I've cleared my memory of our previous conversations.")
        
        return (False, "")

    def run(self, voice_mode: bool = False):
        """Main interaction loop."""
        print(f"Jarvis initialized. Voice Mode: {'ON' if voice_mode else 'OFF'}")
        
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
        print(greeting)
        if voice_mode and hasattr(self, 'voice_output'):
            self.voice_output.speak(greeting)
        
        # Start session timer
        from datetime import datetime
        self.session_start_time = datetime.now()
        
        while True:
            try:
                user_input = ""
                
                # Check session duration and show concern if needed
                if self.session_start_time:
                    session_duration = (datetime.now() - self.session_start_time).total_seconds() / 3600
                    if session_duration > 3 and self.interaction_count % 10 == 0:  # Every 10 interactions after 3 hours
                        concern = JarvisPersonality.get_concern_phrase("fatigue", f"{int(session_duration)} hours")
                        print(f"\nJarvis: {concern}")
                        if voice_mode and hasattr(self, 'voice_output'):
                            self.voice_output.speak(concern)
                
                if voice_mode:
                    print("\nWaiting for wake word...")
                    if self.wake_word.listen():
                        self.voice_output.speak("Yes?")
                        user_input = self.voice_input.listen()
                        print(f"You (Voice): {user_input}")
                else:
                    user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ["exit", "quit", "that will be all"]:
                    farewell = "Very good, sir. Until next time."
                    print(f"Jarvis: {farewell}")
                    if voice_mode:
                        self.voice_output.speak(farewell)
                    break
                
                if not user_input:
                    continue

                # Increment interaction count
                self.interaction_count += 1

                # Check for special commands
                is_command, response = self.handle_command(user_input)
                if is_command:
                    print(f"Jarvis: {response}")
                    if voice_mode:
                        self.voice_output.speak(response)
                    continue

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
                
                print() # Newline after response

                # Speak response if in voice mode
                if voice_mode:
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
                    # self.wake_word.close() # Keep open for loop, close on exit
                    pass

    def cleanup(self):
        if hasattr(self, 'wake_word'):
            self.wake_word.close()

if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.run()

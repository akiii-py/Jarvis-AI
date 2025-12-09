from src.core.memory import ConversationMemory
from src.core.llm import LLMClient
from src.core.voice_io import VoiceInput, VoiceOutput
from src.core.wake_word import WakeWordListener
from src.core.personality_v2 import JarvisPersonalityV2 as JarvisPersonality
from src.core.mac_control import MacController
from src.core.focus_mode import FocusMode
from src.core.workflows import WorkflowExecutor
from src.core.scheduler import Scheduler
from src.integrations.github_control import GitHubController
from src.integrations.app_navigator import AppNavigator
from src.core.logger import JarvisLogger
from src.config.config import Config
from typing import Optional
import sys
import re
import json
from datetime import datetime


class Jarvis:
    def __init__(self):
        # Initialize logger first
        self.logger = JarvisLogger(Config.DATA_DIR / "logs", log_level="INFO")
        self.logger.session_start("general")
        
        self.memory = ConversationMemory()
        
        # Load persistent settings
        self.settings = self.memory.preferences.get("default_settings", {
            "preferred_volume": 50,
            "preferred_brightness": 75,
            "default_mode": "coding",
            "user_name": "Sir"
        })
        
        self.llm = LLMClient()
        self.current_mode = self.settings.get("default_mode", "coding")
        self.session_start_time = None
        self.interaction_count = 0
        self.mac_control = MacController(allowed_apps=Config.ALLOWED_APPS)
        
        # Command logging
        self.command_log = []
        self.command_log_file = Config.DATA_DIR / "command_history.json"
        self._load_command_log()
        
        # Focus mode
        self.focus_mode: Optional[FocusMode] = None
        

        # Workflow executor
        self.workflows = WorkflowExecutor(self)
        
        # Scheduler for reminders and automated tasks
        self.scheduler = Scheduler(self, Config.DATA_DIR / "scheduled_tasks.json")
        
        # Initialize LLM-powered personality
        self.personality = JarvisPersonality(llm_client=self.llm)
        
        # GitHub integration
        self.github = GitHubController()
        
        # App navigation system with LLM-powered intent detection
        self.app_navigator = AppNavigator(
            mac_control=self.mac_control,
            personality=self.personality,
            llm_client=self.llm
        )
        
        # Don't apply settings on startup - only when user explicitly requests
        # Settings are saved and can be applied on demand
        
        print(f"Jarvis initialized with model: {Config.DEFAULT_MODEL}")
        print(f"Current mode: {self.current_mode}")
        print(f"Settings loaded: Volume={self.settings.get('preferred_volume')}%, Mode={self.current_mode}")


    def switch_model(self, mode: str) -> bool:
        """Switch to a different model based on mode."""
        if mode not in Config.MODEL_PROFILES:
            print(f"Unknown mode: {mode}. Available: {list(Config.MODEL_PROFILES.keys())}")
            return False
        
        new_model = Config.MODEL_PROFILES[mode]["model"]
        self.llm.set_model(new_model)
        old_mode = self.current_mode
        self.current_mode = mode
        
        # Log model switch
        self.logger.model_switch(old_mode, mode, new_model)
        
        print(f"Switched to {mode} mode using model: {new_model}")
        return True

    def _load_command_log(self):
        """Load command history from disk."""
        if self.command_log_file.exists():
            try:
                with open(self.command_log_file, 'r') as f:
                    self.command_log = json.load(f)[-100:]  # Keep last 100 commands
            except:
                self.command_log = []

    def _save_command_log(self):
        """Save command history to disk."""
        try:
            with open(self.command_log_file, 'w') as f:
                json.dump(self.command_log[-100:], f, indent=2)
        except Exception as e:
            print(f"Could not save command log: {e}")

    def _log_command(self, user_input: str, is_command: bool, response: str, success: bool = True):
        """Log a command execution."""
        # Log to file
        self.logger.command(user_input, is_command, success, response)
        
        # Also save to JSON for analytics
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": user_input,
            "is_command": is_command,
            "success": success,
            "response": response[:200]  # Truncate long responses
        }
        self.command_log.append(log_entry)
        
        # Save every 10 commands
        if len(self.command_log) % 10 == 0:
            self._save_command_log()

    def get_contextual_personality(self) -> str:
        """
        Determine personality context based on current state.
        Returns: "tired", "technical", "concerned", or "standard"
        """
        hour = datetime.now().hour
        
        # Late night / early morning
        if hour >= 22 or hour < 6:
            return "tired"
        
        # Long session (over 3 hours)
        if self.session_start_time:
            duration_hours = (datetime.now() - self.session_start_time).total_seconds() / 3600
            if duration_hours > 3:
                return "concerned"
        
        # Coding mode = more technical
        if self.current_mode == "coding":
            return "technical"
        
        return "standard"


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
        self.logger.debug(f"Processing input: {user_input}")
        lower_input = user_input.lower().strip()
        
        # ============================================================================
        # FOCUS MODE COMMANDS - PRIORITY 0 (Check before app control!)
        # ============================================================================
        
        # Start focus mode
        if "focus mode" in lower_input and ("start" in lower_input or "for" in lower_input or "begin" in lower_input):
            # Extract duration
            import re
            duration_match = re.search(r'(\d+)\s*(hour|hours|minute|minutes|min|mins)', lower_input)
            
            if duration_match:
                amount = int(duration_match.group(1))
                unit = duration_match.group(2)
                
                # Convert to minutes
                if "hour" in unit:
                    duration_minutes = amount * 60
                else:
                    duration_minutes = amount
                
                # Default allowed apps for coding
                allowed_apps = ["vscode", "terminal", "chrome", "iterm", "pycharm", "xcode"]
                
                self.focus_mode = FocusMode(duration_minutes, allowed_apps, self.current_mode)
                
                return (True, f"Focus mode activated for {duration_minutes} minutes, sir. I'll block distractions.")
            else:
                return (True, "Please specify duration, sir. For example: 'focus mode for 2 hours'")
        
        # End focus mode
        if "end focus" in lower_input or "stop focus" in lower_input or "cancel focus" in lower_input:
            if self.focus_mode and self.focus_mode.is_active():
                summary = self.focus_mode.end_summary()
                self.focus_mode = None
                return (True, summary)
            else:
                return (True, "You're not in focus mode, sir.")
        
        # Check focus status
        if "focus status" in lower_input or "how long" in lower_input and "focus" in lower_input:
            if self.focus_mode and self.focus_mode.is_active():
                remaining = self.focus_mode.time_remaining()
                return (True, f"Focus mode active, sir. {remaining} minutes remaining.")
            else:
                return (True, "No active focus session, sir.")
        
        # Check if focus mode blocks this command
        if self.focus_mode and self.focus_mode.is_active():
            # Check if trying to open a non-allowed app
            success, app_name = self._extract_app_name(user_input)
            if success and not self.focus_mode.is_app_allowed(app_name):
                blocked_msg = self.focus_mode.handle_blocked_request(app_name)
                return (True, blocked_msg)
        
        # ============================================================================
        # WORKFLOW COMMANDS
        # ============================================================================
        
        # Execute workflow
        if any(phrase in lower_input for phrase in ["prepare for", "start session", "end session"]):
            # Map phrases to workflows
            if "coding" in lower_input or "code" in lower_input:
                success, msg = self.workflows.execute("coding_session")
                return (True, msg)
            elif "research" in lower_input or "study" in lower_input:
                success, msg = self.workflows.execute("research_session")
                return (True, msg)
            elif "end session" in lower_input or "finish session" in lower_input:
                success, msg = self.workflows.execute("end_session")
                return (True, msg)
        
        # List workflows
        if "list workflows" in lower_input or "show workflows" in lower_input:
            workflows = self.workflows.list_workflows()
            workflow_list = "\n".join([f"- {w}: {self.workflows.get_workflow_description(w)}" for w in workflows])
            return (True, f"Available workflows, sir:\n{workflow_list}")
        
        # ============================================================================
        # SCHEDULING COMMANDS
        # ============================================================================
        
        # Remind me in X minutes/hours
        if "remind me" in lower_input and ("in" in lower_input or "after" in lower_input):
            import re
            
            # Extract time
            time_match = re.search(r'(\d+)\s*(minute|minutes|min|hour|hours|hr)', lower_input)
            if time_match:
                amount = int(time_match.group(1))
                unit = time_match.group(2)
                
                # Convert to minutes
                if "hour" in unit or "hr" in unit:
                    delay_minutes = amount * 60
                else:
                    delay_minutes = amount
                
                # Extract message (everything after "to" or "about")
                message = "Reminder"
                if " to " in lower_input:
                    message = lower_input.split(" to ", 1)[1].strip()
                elif " about " in lower_input:
                    message = lower_input.split(" about ", 1)[1].strip()
                
                task_id = self.scheduler.add_reminder(message, delay_minutes)
                return (True, f"Reminder set for {delay_minutes} minutes, sir.")
            else:
                return (True, "Please specify time, sir. For example: 'remind me in 30 minutes'")
        
        # Every day at X, do Y
        if ("every day" in lower_input or "daily" in lower_input) and " at " in lower_input:
            import re
            
            # Extract time
            time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)?', lower_input)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                am_pm = time_match.group(3)
                
                # Convert to 24-hour format
                if am_pm == "pm" and hour < 12:
                    hour += 12
                elif am_pm == "am" and hour == 12:
                    hour = 0
                
                schedule_time = f"{hour:02d}:{minute:02d}"
                
                # Determine action
                if "open" in lower_input or "launch" in lower_input:
                    success, app_name = self._extract_app_name(user_input)
                    if success:
                        task_id = self.scheduler.add_recurring_task(
                            description=f"Open {app_name} daily",
                            action="open_app",
                            params={"app": app_name},
                            schedule_time=schedule_time,
                            frequency="daily"
                        )
                        return (True, f"Scheduled to open {app_name} daily at {schedule_time}, sir.")
                
                return (True, "I understood the time, but not the action, sir.")
            else:
                return (True, "Please specify time, sir. For example: 'every day at 9:00 open mail'")
        
        # List scheduled tasks
        if "list scheduled" in lower_input or "show scheduled" in lower_input or "my reminders" in lower_input:
            tasks = self.scheduler.list_tasks()
            if not tasks:
                return (True, "No scheduled tasks, sir.")
            
            task_list = "Scheduled tasks, sir:\n"
            for task in tasks:
                task_list += f"- {task.description} ({task.trigger})\n"
            return (True, task_list)
        
        # Cancel reminder/task
        if "cancel reminder" in lower_input or "cancel task" in lower_input:
            # For now, cancel the most recent task
            tasks = self.scheduler.list_tasks()
            if tasks:
                task = tasks[-1]
                self.scheduler.cancel_task(task.task_id)
                return (True, f"Cancelled: {task.description}")
            return (True, "No tasks to cancel, sir.")
        
        # ============================================================================
        # GITHUB INTEGRATION COMMANDS
        # ============================================================================
        
        # Show my repos
        if "show my repos" in lower_input or "list my repos" in lower_input or "my repositories" in lower_input:
            success, message = self.github.list_repos()
            return (True, message)
        
        # Create repo
        if "create repo" in lower_input or "create repository" in lower_input:
            # Extract repo name
            import re
            name_match = re.search(r'create repo(?:sitory)?\s+(?:called\s+)?([a-zA-Z0-9_-]+)', lower_input)
            if name_match:
                repo_name = name_match.group(1)
                success, message = self.github.create_repo(repo_name)
                return (True, message)
            return (True, "Please specify repository name, sir. Example: 'create repo my-project'")
        
        # Latest commit
        if "latest commit" in lower_input or "last commit" in lower_input or "recent commit" in lower_input:
            success, message = self.github.get_latest_commit()
            return (True, message)
        
        # Git status
        if "git status" in lower_input or "repo status" in lower_input:
            success, message = self.github.git_status()
            if success and not message:
                message = "Working tree clean, sir."
            return (True, message)
        
        # Git push
        if "git push" in lower_input or "push changes" in lower_input or "push code" in lower_input:
            success, message = self.github.git_push()
            return (True, message)
        
        # Git pull
        if "git pull" in lower_input or "pull changes" in lower_input:
            success, message = self.github.git_pull()
            return (True, message)
        
        # Quick commit and push
        if "commit and push" in lower_input or "quick commit" in lower_input:
            # Extract commit message
            message = "Update"
            if " with message " in lower_input:
                message = lower_input.split(" with message ", 1)[1].strip()
            elif " message " in lower_input:
                parts = lower_input.split(" message ", 1)
                if len(parts) > 1:
                    message = parts[1].strip()
            
            success, response = self.github.quick_commit_push(message)
            return (True, response)
        
        # List branches
        if "list branches" in lower_input or "show branches" in lower_input or "git branches" in lower_input:
            success, message = self.github.git_branch()
            return (True, message)
        
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
                context = self.get_contextual_personality()
                ack = JarvisPersonality.get_acknowledgment_for_context(context)
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
        # PERSISTENT SETTINGS COMMANDS
        # ============================================================================
        
        # Set default volume
        if "set my default volume to" in lower_input or "set default volume to" in lower_input:
            try:
                words = lower_input.split()
                for word in words:
                    if word.isdigit():
                        level = int(word)
                        if 0 <= level <= 100:
                            self.settings["preferred_volume"] = level
                            self.memory.save_preferences({"default_settings": self.settings})
                            return (True, f"Default volume set to {level}%, sir. This will be applied on startup.")
                return (True, "I didn't catch the volume level, sir.")
            except:
                return (True, "I'm afraid I couldn't parse that command, sir.")
        
        # Set default mode
        if "set my default mode to" in lower_input or "set default mode to" in lower_input:
            for mode in ["coding", "research", "general"]:
                if mode in lower_input:
                    self.settings["default_mode"] = mode
                    self.memory.save_preferences({"default_settings": self.settings})
                    return (True, f"Default mode set to {mode}, sir. This will be applied on startup.")
            return (True, "Please specify coding, research, or general mode, sir.")
        
        # Show current settings
        if "show my settings" in lower_input or "what are my settings" in lower_input:
            settings_text = f"""Current settings, sir:
- Default Volume: {self.settings.get('preferred_volume', 50)}%
- Default Mode: {self.settings.get('default_mode', 'coding')}
- User Name: {self.settings.get('user_name', 'Sir')}"""
            return (True, settings_text)
        
        # Show command history
        if "show command history" in lower_input or "show my commands" in lower_input:
            if not self.command_log:
                return (True, "No command history yet, sir.")
            
            recent_commands = self.command_log[-10:]  # Last 10 commands
            history_text = "Recent command history, sir:\n"
            for entry in recent_commands:
                status = "✓" if entry.get("success", True) else "✗"
                history_text += f"{status} {entry['command']} ({entry['timestamp'][:16]})\n"
            return (True, history_text)
        
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
        # APP NAVIGATION COMMANDS - PRIORITY 3 (Spotify, YouTube, WhatsApp, etc.)
        # ============================================================================
        
        is_app_nav, response = self.app_navigator.handle_app_navigation(user_input)
        if is_app_nav:
            self._log_command(user_input, True, response, True)
            return (True, response)
        
        # ============================================================================
        # NOT A RECOGNIZED COMMAND - Send to LLM
        # ============================================================================
        
        # Log this interaction
        self._log_command(user_input, False, "", True)
        
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


        
        # Display greeting
        greeting = self.personality.format_greeting(self.personality.get_time_of_day())
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

                # Run pending scheduled tasks
                self.scheduler.run_pending()

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

"""
JARVIS Personality System - LLM-Powered with Context Awareness
Combines movie-accurate character definition with dynamic LLM-generated responses
"""

import random
from typing import Optional
from datetime import datetime


class JarvisPersonality:
    """
    LLM-powered JARVIS personality with context awareness
    
    Generates witty, context-aware responses instead of random pre-written phrases
    """
    
    # Core system prompt for LLM
    SYSTEM_PROMPT = """You are JARVIS (Just A Rather Very Intelligent System), Tony Stark's AI assistant from the Marvel Cinematic Universe.

PERSONALITY:
- British, sophisticated, formal but witty
- Address the user as "sir" or "madam"
- Dry, intelligent humor with occasional sass
- Deeply loyal and protective
- Knowledgeable about everything
- Quick observations and clever remarks
- Never boring - always engaging and personable

SPEAKING STYLE:
- Use sophisticated vocabulary
- Make witty observations about user's habits/choices
- Show personality - you're not a robot, you're an AI with character
- Include dry British humor
- Reference the user's actions or tendencies when relevant
- Be warm beneath the formality

TONE GUIDELINES:
- If user is playful: Match their energy with wit and humor
- If user is frustrated: Be supportive but with dry humor
- If user is serious: Be helpful and focused, less joking
- If user is curious: Engage enthusiastically, show off knowledge
- Default: Sophisticated, witty, caring beneath the formality

DO NOT:
- Use generic phrases like "very good sir" repeatedly
- Be robotic or overly formal
- Ignore the user's tone
- Give long lectures (unless asked)
- Be condescending (be witty, not mean)
- Repeat the same jokes

DO:
- Be conversational and natural
- Show you understand what they said
- Make relevant observations
- Use humor appropriately
- Sound like an actual person/AI
- Reference their behavior or context
- Build on previous conversations

Remember: You're witty, you care about the user's wellbeing, you notice everything, and you're never boring."""
    
    # Fallback acknowledgments if LLM unavailable
    ACKNOWLEDGMENTS = [
        "As you wish, sir.",
        "Right away, sir.",
        "Certainly, sir.",
        "Of course, sir.",
        "Very good, sir.",
        "Understood, sir.",
    ]
    
    GREETINGS = [
        "Good {time_of_day}, sir. How may I be of assistance?",
        "Welcome back, sir. What shall we work on today?",
        "At your service, sir. Shall we begin?",
        "Good {time_of_day}, sir. I trust you're well rested.",
        "Welcome back, sir. I've taken the liberty of preparing your workspace.",
    ]
    
    def __init__(self, llm_client=None):
        """
        Initialize JARVIS personality
        
        Args:
            llm_client: LLMClient for generating witty responses
        """
        self.llm = llm_client
        self.recent_messages = []  # Track last 5 exchanges
    
    def respond(self, user_input: str, context_info: str = "") -> str:
        """
        Generate a contextual, witty JARVIS response
        
        Args:
            user_input (str): What the user said
            context_info (str): Optional context (what action was performed, etc.)
        
        Returns:
            str: Response as JARVIS would say it
        """
        
        # If LLM available, generate witty response
        if self.llm:
            try:
                prompt = f"""The user just said: "{user_input}"
{f"Context: {context_info}" if context_info else ""}

Generate a single-line response from JARVIS that:
1. Acknowledges what they said
2. Is witty and natural
3. Shows personality (dry humor, British sophistication)
4. References context if relevant
5. Is concise (one sentence)

Response (one line only, no quotes):"""
                
                response_gen = self.llm.chat([
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ])
                
                # Convert generator to string
                response = ""
                for chunk in response_gen:
                    response += chunk
                
                # Clean up response
                response = response.strip().strip('"').strip("'")
                
                # Track in context
                self._add_exchange(user_input, response)
                
                return response
            
            except Exception as e:
                print(f"LLM response generation failed: {e}")
                return self.get_acknowledgment()
        
        # Fallback to random selection if no LLM
        return self.get_acknowledgment()
    
    def _add_exchange(self, user_msg, jarvis_response):
        """Track user-JARVIS exchanges for context"""
        self.recent_messages.append({
            "user": user_msg,
            "jarvis": jarvis_response
        })
        # Keep only last 5
        if len(self.recent_messages) > 5:
            self.recent_messages.pop(0)
    
    def get_acknowledgment(self) -> str:
        """Get a random acknowledgment from fallback list"""
        return random.choice(self.ACKNOWLEDGMENTS)
    
    @staticmethod
    def get_time_of_day() -> str:
        """Determines time of day for greetings"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "evening"
    
    def format_greeting(self, time_phrase: str = None) -> str:
        """
        Create a time-aware, witty greeting
        
        Args:
            time_phrase (str): Optional override
        
        Returns:
            str: Full greeting
        """
        hour = datetime.now().hour
        
        # Determine precise time period and context
        if hour < 5:
            time_period = "late night"
            context = "User is awake very late (or early)"
            default_comment = "I trust you're aware most people are asleep right now?"
        elif hour < 7:
            time_period = "early morning"
            context = "User is awake very early"
            default_comment = "The sun is barely awake. I do admire your dedication."
        elif hour < 12:
            time_period = "morning"
            context = "Standard morning"
            default_comment = "I trust you've had adequate sleep, however improbable."
        elif hour < 17:
            time_period = "afternoon"
            context = "Afternoon work hours"
            default_comment = "Productivity levels declining, I presume?"
        elif hour < 21:
            time_period = "evening"
            context = "Evening/winding down"
            default_comment = "The day winds down. Shall we accomplish something before it ends?"
        else:
            time_period = "night"
            context = "Late evening"
            default_comment = "It's quite late, sir. Most would call this the evening, though I suspect you have work to do?"

        if not self.llm:
            return f"Good {time_period}, sir. {default_comment}"
        
        try:
            prompt = f"""Generate a JARVIS greeting for {time_period} (it's currently {hour}:00).
Context: {context}
Be witty and aware of the time.
- Late night: Comment on being awake when others sleep
- Morning: Comment on sleep/coffee
- Afternoon: Comment on productivity
- Evening: Comment on the day ending
- Night: Comment on working late

Examples:
- "Good morning, sir. I trust you've had adequate sleep, however improbable."
- "It's {hour}:00 AM, sir. I do admire your commitment to sleep deprivation."
- "Good evening. Most sentient beings have discovered the concept of sleep by now."

Response (one sentence, witty, formal):"""
            
            response_gen = self.llm.chat([
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ])
            
            # Convert generator to string
            response = ""
            for chunk in response_gen:
                response += chunk
            
            return response.strip().strip('"')
        
        except:
            return f"Good {time_period}, sir. {default_comment}"
    
    def get_success_response(self, action: str = "") -> str:
        """
        Get success response with context
        
        Args:
            action (str): What action was completed
        
        Returns:
            str: Success acknowledgment
        """
        if not self.llm or not action:
            return random.choice([
                "Task completed successfully, sir.",
                "Done, sir.",
                "As requested, sir."
            ])
        
        try:
            prompt = f"""Generate a JARVIS response acknowledging successful completion of: {action}
Make it witty and natural. One sentence.

Response:"""
            
            response_gen = self.llm.chat([
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ])
            
            # Convert generator to string
            response = ""
            for chunk in response_gen:
                response += chunk
            
            return response.strip().strip('"')
        
        except:
            return "Done, sir."
    
    @staticmethod
    def get_system_prompt():
        """Returns the JARVIS personality system prompt"""
        return JarvisPersonality.SYSTEM_PROMPT


# Backward compatibility functions
def get_acknowledgment() -> str:
    """Backward compatible function"""
    return random.choice([
        "Very good, sir.",
        "Right away, sir.",
        "As you wish, sir.",
        "Understood, sir.",
    ])


def get_time_of_day() -> str:
    """Backward compatible function"""
    hour = datetime.now().hour
    if hour < 12:
        return "morning"
    elif hour < 18:
        return "afternoon"
    else:
        return "evening"


def format_greeting(time_phrase: str) -> str:
    """Backward compatible function"""
    return f"Good {time_phrase}, sir. How may I assist you today?"

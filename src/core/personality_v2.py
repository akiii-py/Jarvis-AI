"""
JARVIS Personality V2 Module
Advanced conversational intelligence with memory and context awareness
This version:
- Uses memory to make observations about user habits
- Adapts tone based on context
- Remembers conversation flow
- Makes witty, personalized responses
- Builds on previous exchanges
"""

import random
from typing import Optional
from .personality_prompts import JARVIS_SYSTEM_PROMPT_V2
from .memory_manager import ConversationMemory, ContextAware


class JarvisPersonalityV2:
    """
    Enhanced JARVIS personality with memory and context
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize JARVIS personality V2
        
        Args:
            llm_client: LLMClient for generating responses
        """
        self.llm = llm_client
        self.memory = ConversationMemory()
        self.context_aware = ContextAware(self.memory)
        
        # Fallback responses (use rarely)
        self.fallback_acknowledgments = [
            "Very good, sir.",
            "As you wish, sir.",
            "Proceeding, sir.",
        ]
    
    def respond(self, user_input: str, context_info: str = "") -> str:
        """
        Generate a contextual, witty, personalized JARVIS response
        
        This is the PRIMARY method for responses.
        """
        
        if not self.llm:
            return self.get_acknowledgment()
        
        try:
            # Build context
            context = self.memory.get_context()
            recent_exchanges = self.memory.get_last_exchanges(3)
            habit_observation = self.memory.make_observation()
            user_tone = self.context_aware.detect_user_tone(user_input)
            time_of_day = self.context_aware.detect_time_of_day()
            
            # Build the prompt
            prompt = self._build_response_prompt(
                user_input=user_input,
                context_info=context_info,
                recent_exchanges=recent_exchanges,
                habit_observation=habit_observation,
                user_tone=user_tone,
                time_of_day=time_of_day,
                should_reference_habit=self.context_aware.should_reference_habit()
            )
            
            # Generate response
            response_gen = self.llm.chat([
                {"role": "system", "content": JARVIS_SYSTEM_PROMPT_V2},
                {"role": "user", "content": prompt}
            ])
            
            # Convert generator to string
            response = ""
            for chunk in response_gen:
                response += chunk
            
            # Clean and save
            response = response.strip().strip('"').strip("'")
            self.memory.add_exchange(user_input, response)
            
            return response
        
        except Exception as e:
            print(f"Error generating response: {e}")
            return self.get_acknowledgment()
    
    def _build_response_prompt(
        self,
        user_input: str,
        context_info: str,
        recent_exchanges: str,
        habit_observation: str,
        user_tone: str,
        time_of_day: str,
        should_reference_habit: bool
    ) -> str:
        """
        Build a detailed prompt for context-aware response
        """
        
        prompt = f"""User just said: "{user_input}"
{f"Context: {context_info}" if context_info else ""}

CONTEXT INFORMATION:
- Time of day: {time_of_day}
- User tone: {user_tone}
- Recent conversation:
{recent_exchanges}
{f"USER OBSERVATION: {habit_observation}" if should_reference_habit and habit_observation else ""}

Generate a SINGLE response from JARVIS that:
1. PERSONALITY FIRST
   - Be witty and observant, not generic
   - Make the user smile or think
   - Sound like an actual person with character

2. MATCH THE TONE
   - If casual: respond with wit and humor
   - If frustrated: be supportive with dry humor
   - If serious: be helpful and focused
   - If curious: engage enthusiastically

3. BE SPECIFIC
   - Reference their context if relevant
   - Make personal observations
   - Connect to previous conversation if applicable

4. SOUND LIKE JARVIS
   - British sophistication
   - Dry, intelligent humor
   - Formal but personable
   - Never boring, never generic
   - Show you understand them

5. KEEP IT SHORT
   - One or two sentences max
   - Punchy and memorable
   - No explanations unless asked

EXAMPLES OF GOOD RESPONSES:
- "Good morning, sir. I trust your sleep cycle remains as erratic as ever?"
- "An admirable commitment to avoiding productivity, sir."
- "I've observed this is your third such request. Shall I prepare documentation?"

Now generate your response (one or two sentences, no quotes):"""
        
        return prompt
    
    def get_acknowledgment(self) -> str:
        """Fallback acknowledgment"""
        return random.choice(self.fallback_acknowledgments)
    
    def format_greeting(self) -> str:
        """Generate a greeting with personality"""
        from datetime import datetime
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

Examples:
- "Good morning, sir. I trust you've had adequate sleep, however improbable."
- "It's {hour}:00, sir. I do admire your commitment to sleep deprivation."
- "Good evening. Most sentient beings have discovered the concept of sleep by now."

Response (one sentence, witty, formal):"""
            
            response_gen = self.llm.chat([
                {"role": "system", "content": JARVIS_SYSTEM_PROMPT_V2},
                {"role": "user", "content": prompt}
            ])
            
            # Convert generator to string
            response = ""
            for chunk in response_gen:
                response += chunk
            
            return response.strip().strip('"')
        
        except:
            return f"Good {time_period}, sir. {default_comment}"
    
    def react_to_success(self, action: str) -> str:
        """React to successful action"""
        reactions = [
            "Completed successfully, sir.",
            "Quite done, sir.",
            f"Completed your {action}, sir.",
        ]
        
        if not self.llm:
            return random.choice(reactions)
        
        try:
            prompt = f"""User just completed: {action}
Generate a witty JARVIS reaction (one sentence, no quotes):"""
            
            response_gen = self.llm.chat([
                {"role": "system", "content": JARVIS_SYSTEM_PROMPT_V2},
                {"role": "user", "content": prompt}
            ])
            
            # Convert generator to string
            response = ""
            for chunk in response_gen:
                response += chunk
            
            return response.strip().strip('"')
        
        except:
            return random.choice(reactions)
    
    @staticmethod
    def get_time_of_day() -> str:
        """For backward compatibility"""
        from datetime import datetime
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "evening"


# Backward compatibility
JarvisPersonality = JarvisPersonalityV2

import requests
import json
from typing import Generator, List, Dict
from src.config.config import Config
from src.core.personality import JarvisPersonality

class LLMClient:
    def __init__(self, model: str = Config.DEFAULT_MODEL):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = model

    def chat(self, messages: List[Dict[str, str]], stream: bool = True, use_jarvis_personality: bool = True, custom_memories: List[str] = None, current_mode: str = None) -> Generator[str, None, None]:
        """
        Sends a chat request to the Ollama API.
        Returns a generator that yields chunks of the response.
        """
        # Inject JARVIS personality as system message
        if use_jarvis_personality and (not messages or messages[0].get("role") != "system"):
            system_content = JarvisPersonality.get_system_prompt()
            
            # Add mode awareness
            if current_mode:
                mode_info = f"""

═══════════════════════════════════════════════════════════════
CRITICAL SYSTEM INFORMATION - READ CAREFULLY
═══════════════════════════════════════════════════════════════

YOU ARE CURRENTLY IN: {current_mode.upper()} MODE

AVAILABLE MODES (THESE ARE THE ONLY MODES THAT EXIST):

1. CODING MODE (qwen2.5-coder model)
   - Optimized for programming, debugging, code review
   - Best for: Writing code, fixing bugs, explaining algorithms
   - Current: {"✓ ACTIVE" if current_mode == "coding" else "○ Inactive"}

2. RESEARCH MODE (deepseek-r1 model)  
   - Optimized for deep reasoning, analysis, research
   - Best for: Complex explanations, research, detailed analysis
   - Current: {"✓ ACTIVE" if current_mode == "research" else "○ Inactive"}

3. GENERAL MODE (mistral model)
   - Optimized for conversation and general tasks
   - Best for: Casual chat, quick questions, general assistance
   - Current: {"✓ ACTIVE" if current_mode == "general" else "○ Inactive"}

IMPORTANT RULES:
- These are the ONLY three modes that exist
- DO NOT make up other modes (no "creative mode", "analytical mode", etc.)
- When asked about modes, describe ONLY these three
- You CAN suggest switching modes when appropriate
- User can switch by saying: "switch to coding/research/general mode"

EXAMPLE RESPONSES:
Q: "what can you do in different modes?"
A: "I have three modes, sir:
- Coding mode (current): Optimized for programming and debugging
- Research mode: For deep analysis and complex reasoning  
- General mode: For conversation and general tasks
Would you like me to switch modes?"

═══════════════════════════════════════════════════════════════
"""
                system_content += mode_info
                print(f"[DEBUG] Mode awareness injected: {current_mode}")  # Debug
            
            # Add custom memories if provided
            if custom_memories:
                memory_text = "\n\nIMPORTANT FACTS TO REMEMBER:\n" + "\n.join(f"- {mem}" for mem in custom_memories)
                system_content += memory_text
            
            messages = [
                {"role": "system", "content": system_content}
            ] + messages
        
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }

        try:
            with requests.post(url, json=payload, stream=stream) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        body = json.loads(line)
                        if "message" in body and "content" in body["message"]:
                            yield body["message"]["content"]
                        if body.get("done", False):
                            break
        except requests.exceptions.RequestException as e:
            yield f"I'm afraid I've encountered a technical difficulty, sir: {e}"

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  CRITICAL SYSTEM CONSTRAINT - YOU MUST FOLLOW THIS EXACTLY ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CURRENT ACTIVE MODE: {current_mode.upper()}

YOU HAVE EXACTLY 3 MODES. NO MORE, NO LESS. DO NOT INVENT OTHER MODES.

MODE 1: CODING (qwen2.5-coder model) {"← YOU ARE HERE" if current_mode == "coding" else ""}
- Programming, debugging, code review
- Writing and explaining code
- Fixing bugs and errors

MODE 2: RESEARCH (deepseek-r1 model) {"← YOU ARE HERE" if current_mode == "research" else ""}
- Deep analysis and reasoning
- Complex research tasks
- Detailed explanations

MODE 3: GENERAL (mistral model) {"← YOU ARE HERE" if current_mode == "general" else ""}
- Casual conversation
- Quick questions
- General assistance

FORBIDDEN RESPONSES:
❌ "Assistive Mode" - DOES NOT EXIST
❌ "Creative Mode" - DOES NOT EXIST  
❌ "Analytical Mode" - DOES NOT EXIST
❌ "Conversational Mode" - DOES NOT EXIST
❌ "Security Mode" - DOES NOT EXIST
❌ ANY mode not listed above - DOES NOT EXIST

WHEN ASKED "what can you do in different modes?" YOU MUST RESPOND:

"I have three modes, sir:

1. Coding mode (qwen2.5-coder) - Currently {"active" if current_mode == "coding" else "inactive"}
   For programming, debugging, and code-related tasks.

2. Research mode (deepseek-r1) - Currently {"active" if current_mode == "research" else "inactive"}
   For deep analysis, research, and complex reasoning.

3. General mode (mistral) - Currently {"active" if current_mode == "general" else "inactive"}
   For conversation and general assistance.

You can switch modes by saying 'switch to coding/research/general mode', sir."

DO NOT deviate from this response. DO NOT add other modes. DO NOT make up capabilities.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                system_content += mode_info
                print(f"[DEBUG] Mode awareness injected: {current_mode}")  # Debug
            
            # Add custom memories if provided
            if custom_memories:
                memory_text = "\n\nIMPORTANT FACTS TO REMEMBER:\n" + "\n".join(f"- {mem}" for mem in custom_memories)
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

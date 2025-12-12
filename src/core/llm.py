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

CURRENT MODE INFORMATION:
You are currently operating in "{current_mode}" mode.

Available modes:
- coding: Optimized for programming, debugging, and technical tasks (using qwen2.5-coder model)
- research: Optimized for deep reasoning, analysis, and research (using deepseek-r1 model)
- general: Optimized for conversation and general tasks (using mistral model)

You can suggest the user switch modes by saying something like:
"This task might be better suited for research mode, sir. Shall I switch?"

The user can switch modes by saying:
- "switch to coding mode"
- "switch to research mode"  
- "switch to general mode"

Remember: You ARE aware of your current mode and CAN suggest switching when appropriate."""
                system_content += mode_info
            
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

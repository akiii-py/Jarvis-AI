import requests
import json
from typing import Generator, List, Dict
from src.config.config import Config
from src.core.personality import JarvisPersonality

class LLMClient:
    def __init__(self, model: str = Config.DEFAULT_MODEL):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = model

    def chat(self, messages: List[Dict[str, str]], stream: bool = True, use_jarvis_personality: bool = True, custom_memories: List[str] = None) -> Generator[str, None, None]:
        """
        Sends a chat request to the Ollama API.
        Returns a generator that yields chunks of the response.
        """
        # Inject JARVIS personality as system message
        if use_jarvis_personality and (not messages or messages[0].get("role") != "system"):
            system_content = JarvisPersonality.get_system_prompt()
            
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

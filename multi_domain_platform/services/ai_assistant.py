from typing import List, Dict
class AIAssistant:
    """Simple wrapper around an AI/chat model.
    In your real project, connect this to OpenAI or another provider.
    """
    def __init__(self, system_prompt: str = "You are a helpful assistant."):
        self._system_prompt = system_prompt
        self._history: List[Dict[str, str]] = []
    def set_system_prompt(self, prompt: str) :
        self._system_prompt = prompt
    def send_message(self, user_message: str) :
        self._history.append({"role": "user", "content": user_message})
        response = f"[AI reply to]: {user_message[:50]}"
        self._history.append({"role": "assistant", "content": response})
        return response
    def clear_history(self):
        self._history.clear()
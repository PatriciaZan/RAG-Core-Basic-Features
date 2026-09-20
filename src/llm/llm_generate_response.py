import os
import requests
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(
            self,
            model="openrouter/free"
    ):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY não encontrada.")
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        response = requests.post(
            self.OPENROUTER_URL,
            headers={
                "Authorization": (
                    f"Bearer {self.api_key}"
                ),
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": messages
            },
            timeout=60
        )

        if response.status_code == 429:
            raise RuntimeError("Limite de requisições da LLM atingido. Aguarde alguns segundos e tente novamente.")

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
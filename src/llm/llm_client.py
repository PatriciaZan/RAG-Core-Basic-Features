import os
import requests
from dotenv import load_dotenv
import json


load_dotenv()
OPENROUTER_URL = ("https://openrouter.ai/api/v1/chat/completions")

def call_llm(
    system_prompt: str,
    user_prompt: str
) -> str:

    api_key = os.getenv(
        "OPENROUTER_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY não configurada."
        )

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openrouter/free",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "response_format": {
                "type": "json_object"
            }
        },
        timeout=60
    )
    response.raise_for_status()
    data = response.json()

# para descobrir oque o OPENIA ta retornando por causa de erros no tests_query_analizer.py
    print("\n================ RESPONSE COMPLETA ================")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    print("====================================================\n")

    return data["choices"][0]["message"]["content"]
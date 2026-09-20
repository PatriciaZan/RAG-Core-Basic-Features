"""
Converte texto em embedding (vetor numérico) usando OpenRouter.

Args:
    text: Texto a ser convertido em embedding
    model: Modelo a usar (padrão: openai/text-embedding-3-small)
    timeout: Tempo máximo de espera em segundos

Returns:
    Lista de números (embedding) representando o texto

Raises:
    ValueError: Se o texto estiver vazio
    requests.HTTPError: Se a requisição à API falhar
    Exception: Se houver erro ao processar a resposta
"""

import requests
import os
from dotenv import load_dotenv
from typing import List, Optional

# Configuração
OPENROUTER_URL = "https://openrouter.ai/api/v1/embeddings"
EMBEDDING_MODEL = "openai/text-embedding-3-small"
TIMEOUT = 60

load_dotenv()
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
if not openrouter_api_key:
    raise ValueError("OPENROUTER_API_KEY is not set in .env file")

def get_embedding(
        text: str,
        model: Optional[str] = None,
        timeout: int = TIMEOUT
) -> List[float]:

    if not text or not text.strip():
        raise ValueError("O texto não pode estar vazio")

    model = model or EMBEDDING_MODEL
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "input": text
            },
            timeout=timeout
        )

        response.raise_for_status()
        data = response.json()

        if "data" not in data or len(data["data"]) == 0:
            raise Exception("Resposta da API sem dados de embedding")

        return data["data"][0]["embedding"]

    except requests.exceptions.Timeout:
        raise Exception(f"Timeout ao conectar com OpenRouter após {timeout}s")
    except requests.exceptions.ConnectionError:
        raise Exception("Erro de conexão com OpenRouter. Verifique sua internet.")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"Erro da API OpenRouter: {e.response.status_code} - {e.response.text}")


def get_embeddings_batch(
        texts: List[str],
        model: Optional[str] = None,
        timeout: int = TIMEOUT
) -> List[List[float]]:

    if not texts or len(texts) == 0:
        raise ValueError("Lista de textos não pode estar vazia")

    model = model or EMBEDDING_MODEL

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "input": texts
            },
            timeout=timeout
        )

        response.raise_for_status()
        data = response.json()

        if "data" not in data:
            raise Exception("Resposta da API sem dados de embedding")

        # Ordena por índice para garantir ordem correta
        embeddings = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in embeddings]

    except requests.exceptions.Timeout:
        raise Exception(f"Timeout ao conectar com OpenRouter após {timeout}s")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"Erro da API OpenRouter: {e.response.status_code}")


# Exemplo de uso
'''
if __name__ == "__main__":
    # Um texto
    texto = "Python é uma linguagem de programação excelente"
    embedding = get_embedding(texto)
    print(f"Dimensão do embedding: {len(embedding)}")
    print(f"Primeiros 5 valores: {embedding[:5]}")

    # Múltiplos textos
    textos = [
        "Gato é um animal doméstico",
        "Cachorro é amigo do homem",
        "Pássaro voa no céu"
    ]
    embeddings = get_embeddings_batch(textos)
    print(f"\nTotal de embedding: {len(embeddings)}")
    print(f"Dimensão de cada embedding: {len(embeddings[0])}")
'''
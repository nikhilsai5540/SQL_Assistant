import os

import httpx


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
)

CHAT_MODEL = os.getenv(
    "OLLAMA_CHAT_MODEL",
    "qwen2.5-coder:3b"
)

EMBEDDING_MODEL = os.getenv(
    "OLLAMA_EMBED_MODEL",
    "nomic-embed-text"
)


def call_ollama(endpoint: str, payload: dict):

    url = f"{OLLAMA_URL}{endpoint}"

    try:

        response = httpx.post(
            url,
            json=payload,
            timeout=120.0,
        )

        response.raise_for_status()

        return response.json()

    except httpx.ConnectError:

        raise RuntimeError(
            "Cannot connect to Ollama. "
            "Make sure Ollama is installed and running."
        )

    except httpx.HTTPStatusError as error:

        try:
            message = error.response.json().get(
                "error",
                str(error)
            )
        except Exception:
            message = str(error)

        raise RuntimeError(
            f"Ollama error: {message}"
        )

    except httpx.RequestError as error:

        raise RuntimeError(
            f"Ollama request failed: {error}"
        )


def chat(messages, temperature=0):

    payload = {
        "model": CHAT_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    response = call_ollama(
        "/api/chat",
        payload
    )

    return response["message"]["content"]


def embed_text(text: str):

    payload = {
        "model": EMBEDDING_MODEL,
        "input": text
    }

    response = call_ollama(
        "/api/embed",
        payload
    )

    embeddings = response.get("embeddings")

    if not embeddings:
        raise RuntimeError(
            "Ollama did not return an embedding."
        )

    return embeddings[0]
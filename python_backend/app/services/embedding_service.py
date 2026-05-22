import requests

from ..config import settings

HF_EMBEDDING_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"
)


def generate_embedding(text: str) -> list[float]:
    headers = {"Content-Type": "application/json"}
    if settings.huggingface_api_key:
        headers["Authorization"] = f"Bearer {settings.huggingface_api_key}"

    response = requests.post(
        HF_EMBEDDING_URL,
        json={"inputs": text},
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()

    embedding = response.json()
    while isinstance(embedding, list) and embedding and isinstance(embedding[0], list):
        embedding = embedding[0]

    if isinstance(embedding, list) and embedding and isinstance(embedding[0], (int, float)):
        return embedding

    raise ValueError("Invalid embedding response")

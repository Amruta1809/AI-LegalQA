import requests

from ..config import settings
from ..utils.prompt_builder import build_prompt
from .embedding_service import generate_embedding
from .search_service import search_laws

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


def ask_question(question: str) -> dict:
    query_embedding = generate_embedding(question)

    relevant_laws: list[dict] = []
    try:
        relevant_laws = search_laws(query_embedding)
    except Exception:
        relevant_laws = []

    prompt = build_prompt(question, relevant_laws)

    response = requests.post(
        OPENROUTER_CHAT_URL,
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "HTTP-Referer": settings.app_url,
            "X-Title": "AI Legal Q&A",
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    answer = data["choices"][0]["message"]["content"]
    full_answer = (
        answer
        + "\n\nThis tool provides general legal information and is not legal advice."
    )
    citations = [
        {"act": law["act"], "section": law["section"]}
        for law in relevant_laws
    ]

    return {"answer": full_answer, "citations": citations}

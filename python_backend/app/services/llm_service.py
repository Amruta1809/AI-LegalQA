from __future__ import annotations

import requests

from ..config import settings
from ..utils.prompt_builder import (
    DISCLAIMER,
    build_prompt,
    classify_intent,
    is_greeting,
)
from .embedding_service import generate_embedding
from .search_service import search_laws

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


def calculate_confidence(relevant_laws: list[dict]) -> tuple[int, str]:
    if not relevant_laws:
        return 32, "Low"

    similarities = [
        float(law.get("similarity", 0))
        for law in relevant_laws
        if law.get("act") and law.get("section") and law.get("content")
    ]
    if not similarities:
        return 40, "Low"

    average_similarity = sum(similarities) / len(similarities)
    top_similarity = max(similarities)
    coverage_bonus = min(len(similarities), 4) * 4

    score = round((average_similarity * 55) + (top_similarity * 25) + coverage_bonus)
    score = max(25, min(score, 98))

    if score >= 90:
        level = "High"
    elif score >= 70:
        level = "Medium"
    else:
        level = "Low"

    return score, level


def normalize_retrieved_laws(relevant_laws: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    seen_keys: set[tuple[str, str, str]] = set()

    for law in relevant_laws:
        act = str(law.get("act", "")).strip()
        section = str(law.get("section", "")).strip()
        content = str(law.get("content", "")).strip()
        similarity = float(law.get("similarity", 0) or 0)

        if not act or not section or not content:
            continue

        key = (act, section, content)
        if key in seen_keys:
            continue

        seen_keys.add(key)
        normalized.append(
            {
                "act": act,
                "section": section,
                "content": content,
                "similarity": similarity,
            }
        )

    return normalized


def build_citations(relevant_laws: list[dict]) -> list[dict]:
    return [
        {
            "act": law["act"],
            "section": law["section"],
            "exact_citation": law["content"],
            "similarity": round(float(law.get("similarity", 0)), 3),
        }
        for law in relevant_laws
    ]


def build_no_source_response(question: str, intent_category: str) -> dict:
    answer = f"""## Summary
I could not find a matching legal provision in the database.

## Relevant Legal Provisions
No sufficiently relevant act or section was retrieved for this question.

## Legal Analysis
Your request appears to fall under **{intent_category}**, but the current legal database did not return a reliable matching provision for the question: "{question}".
To avoid inventing laws or sections, I am not giving a citation-backed legal conclusion.

## Recommended Actions
- Rephrase the question with more specific facts such as the state involved, dates, whether there is a written document, and whether police, employer, landlord, or a government office is involved.
- Mention any known act name, section number, notice, FIR, agreement, or court stage if you have it.
- Consult a qualified advocate if this is urgent, high-value, criminal, or time-sensitive.

## Risk Assessment
Medium Risk
The main risk is acting without a verified legal provision from the available database.

## Confidence Score
Confidence Score: 32% (Low)

## Citations
No citation-backed legal provision was available in the current database context.

## Legal Disclaimer
{DISCLAIMER}
"""

    return {
        "answer": answer,
        "citations": [],
        "intent_category": intent_category,
        "confidence_score": 32,
        "confidence_level": "Low",
        "retrieved_sources_count": 0,
        "used_retrieval": False,
    }


def ensure_disclaimer(answer: str) -> str:
    return answer if DISCLAIMER in answer else f"{answer.rstrip()}\n\n## Legal Disclaimer\n{DISCLAIMER}"


def ask_question(question: str) -> dict:
    intent_category = classify_intent(question)

    if is_greeting(question):
        prompt = build_prompt(
            question=question,
            relevant_laws=[],
            intent_category=intent_category,
            confidence_score=95,
            confidence_level="High",
        )
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
        return {
            "answer": answer,
            "citations": [],
            "intent_category": intent_category,
            "confidence_score": 95,
            "confidence_level": "High",
            "retrieved_sources_count": 0,
            "used_retrieval": False,
        }

    query_embedding = generate_embedding(question)

    relevant_laws: list[dict] = []
    try:
        relevant_laws = normalize_retrieved_laws(
            search_laws(question, query_embedding, match_count=5)
        )
    except Exception:
        relevant_laws = []

    confidence_score, confidence_level = calculate_confidence(relevant_laws)

    if not relevant_laws:
        return build_no_source_response(question, intent_category)

    prompt = build_prompt(
        question=question,
        relevant_laws=relevant_laws,
        intent_category=intent_category,
        confidence_score=confidence_score,
        confidence_level=confidence_level,
    )

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
    answer = ensure_disclaimer(data["choices"][0]["message"]["content"])
    citations = build_citations(relevant_laws)

    return {
        "answer": answer,
        "citations": citations,
        "intent_category": intent_category,
        "confidence_score": confidence_score,
        "confidence_level": confidence_level,
        "retrieved_sources_count": len(relevant_laws),
        "used_retrieval": True,
    }

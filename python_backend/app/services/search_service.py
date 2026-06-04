from __future__ import annotations

import re

from ..database import query_db
from ..utils.vector import to_vector_literal

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "can",
    "do",
    "for",
    "from",
    "how",
    "i",
    "if",
    "in",
    "is",
    "it",
    "my",
    "of",
    "on",
    "or",
    "should",
    "the",
    "to",
    "what",
    "when",
    "with",
}

TERM_EXPANSIONS = {
    "signal": ["traffic", "violation", "motor", "vehicle", "red", "light"],
    "traffic": ["signal", "violation", "motor", "vehicle", "road"],
    "salary": ["wages", "payment", "employer", "employee"],
    "wages": ["salary", "payment", "employer", "employee"],
    "fir": ["police", "complaint", "criminal"],
    "cyber": ["hacking", "digital", "online", "it"],
}

PHRASE_EXPANSIONS = {
    "break the signal": ["traffic", "violation", "motor", "vehicle", "red", "light"],
    "jump signal": ["traffic", "violation", "motor", "vehicle", "red", "light"],
    "red light": ["traffic", "violation", "motor", "vehicle", "signal"],
    "salary not paid": ["wages", "payment", "employer", "employee"],
    "not paid": ["wages", "payment"],
}


def normalize_law_row(law: dict, fallback_similarity: float = 0.0) -> dict:
    return {
        "act": law.get("act", ""),
        "section": law.get("section", ""),
        "title": law.get("title", ""),
        "content": law.get("content", ""),
        "keywords": law.get("keywords") or [],
        "similarity": float(law.get("similarity", fallback_similarity) or fallback_similarity),
    }


def semantic_search_laws(query_embedding: list[float], match_count: int = 5) -> list[dict]:
    rows = query_db(
        """
        SELECT content, act, section, title, keywords, similarity
        FROM (
            SELECT
                l.content,
                l.act,
                l.section,
                l.title,
                l.keywords,
                1 - (l.embedding <=> %s::vector) AS similarity
            FROM laws l
            WHERE l.embedding IS NOT NULL
            ORDER BY l.embedding <=> %s::vector
            LIMIT %s
        ) matches
        WHERE similarity >= 0.45
        ORDER BY similarity DESC
        """,
        (to_vector_literal(query_embedding), to_vector_literal(query_embedding), match_count),
    )
    return [normalize_law_row(law) for law in rows]


def extract_search_terms(question: str) -> list[str]:
    normalized_question = question.lower()
    tokens = re.findall(r"[a-zA-Z0-9]+", normalized_question)
    search_terms: list[str] = []

    for phrase, expansions in PHRASE_EXPANSIONS.items():
        if phrase in normalized_question:
            for term in expansions:
                if term not in search_terms:
                    search_terms.append(term)

    for token in tokens:
        if len(token) < 3 or token in STOPWORDS:
            continue
        if token not in search_terms:
            search_terms.append(token)
        for expanded_term in TERM_EXPANSIONS.get(token, []):
            if expanded_term not in search_terms:
                search_terms.append(expanded_term)

    return search_terms[:12]


def keyword_search_laws(question: str, match_count: int = 5) -> list[dict]:
    search_terms = extract_search_terms(question)
    if not search_terms:
        return []

    clauses = []
    score_parts = []
    where_params: list[str] = []
    score_params: list[str] = []

    for term in search_terms:
        pattern = f"%{term}%"
        clauses.append(
            """
            (
                act ILIKE %s
                OR section ILIKE %s
                OR COALESCE(title, '') ILIKE %s
                OR content ILIKE %s
                OR array_to_string(COALESCE(keywords, ARRAY[]::text[]), ' ') ILIKE %s
            )
            """
        )
        where_params.extend([pattern, pattern, pattern, pattern, pattern])
        score_parts.append(
            """
            CASE
                WHEN act ILIKE %s THEN 3
                WHEN COALESCE(title, '') ILIKE %s THEN 2.5
                WHEN array_to_string(COALESCE(keywords, ARRAY[]::text[]), ' ') ILIKE %s THEN 2
                WHEN content ILIKE %s THEN 1
                ELSE 0
            END
            """
        )
        score_params.extend([pattern, pattern, pattern, pattern])

    rows = query_db(
        f"""
        SELECT
            act,
            section,
            title,
            content,
            keywords,
            ({' + '.join(score_parts)}) / %s::float AS similarity
        FROM laws
        WHERE {' OR '.join(clauses)}
        ORDER BY similarity DESC, act ASC, section ASC
        LIMIT %s
        """,
        tuple(score_params + [max(len(search_terms), 1)] + where_params + [match_count]),
    )

    return [
        normalize_law_row(law, fallback_similarity=0.55)
        for law in rows
        if float(law.get("similarity", 0) or 0) >= 0.2
    ]


def merge_results(primary: list[dict], secondary: list[dict], match_count: int) -> list[dict]:
    merged: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    for collection in (primary, secondary):
        for law in collection:
            key = (
                str(law.get("act", "")).strip(),
                str(law.get("section", "")).strip(),
                str(law.get("content", "")).strip(),
            )
            if not all(key) or key in seen:
                continue
            seen.add(key)
            merged.append(law)

    merged.sort(key=lambda law: float(law.get("similarity", 0) or 0), reverse=True)
    return merged[:match_count]


def search_laws(question: str, query_embedding: list[float], match_count: int = 5) -> list[dict]:
    semantic_results = semantic_search_laws(query_embedding, match_count=match_count)

    if len(semantic_results) >= 2:
        return semantic_results[:match_count]

    keyword_results = keyword_search_laws(question, match_count=match_count)
    if not semantic_results:
        return keyword_results[:match_count]

    return merge_results(semantic_results, keyword_results, match_count)

import re


def is_greeting(question: str) -> bool:
    normalized = question.strip().lower()
    return bool(
        re.fullmatch(
            r"(hi|hello|hey|hii+|good morning|good afternoon|good evening)([!.?, ]*)",
            normalized,
        )
    )


def build_prompt(question: str, relevant_laws: list[dict]) -> str:
    if relevant_laws:
        context = "\n\n".join(
            f"Act: {law['act']}\nSection: {law['section']}\nContent: {law['content']}"
            for law in relevant_laws
        )
        return f"""You are a legal AI assistant.
Answer ONLY from the provided legal context.
Do not invent information.
If answer is missing, say 'Not found in provided laws.'
Always include act and section when available.
Keep response simple for normal users.

Question: {question}

Context:
{context}

Answer:"""

    if is_greeting(question):
        return f"""You are a friendly legal AI assistant specializing in Indian law.
The user has sent only a greeting.
Respond warmly in 1-2 short sentences and mention that you can help with legal questions about Indian law.
Do not give a legal explanation unless the user asks one.

Question: {question}

Answer:"""

    return f"""You are a legal AI assistant specializing in Indian law.
The user's message is not a greeting.
Answer the user's actual question directly.
If no matching laws were found in the database, use your general legal knowledge and clearly mention that the answer is based on general legal knowledge, not retrieved law text.
Do not start with a greeting unless the user only greeted you.
Keep response simple for normal users.

Question: {question}

Answer:"""

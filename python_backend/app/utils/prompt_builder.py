from __future__ import annotations

import re

INTENT_CATEGORIES = [
    "Legal Information",
    "Rights and Obligations",
    "Employment Law",
    "Consumer Law",
    "Property Law",
    "Criminal Law",
    "Family Law",
    "Cyber Law",
    "Tax Law",
    "Contract Law",
    "Legal Notice Drafting",
    "Document Analysis",
    "Case Law Research",
    "General Legal Guidance",
]

DISCLAIMER = (
    "This response is for informational and educational purposes only and does not "
    "constitute legal advice. Consult a qualified advocate for advice specific to your situation."
)

INTENT_KEYWORDS = {
    "Employment Law": [
        "salary",
        "wages",
        "employment",
        "termination",
        "resignation",
        "notice period",
        "gratuity",
        "pf",
        "provident fund",
        "bonus",
        "workplace",
        "employer",
        "employee",
    ],
    "Consumer Law": [
        "consumer",
        "refund",
        "defective",
        "seller",
        "ecommerce",
        "service provider",
        "complaint",
        "replacement",
    ],
    "Property Law": [
        "property",
        "land",
        "flat",
        "rent",
        "rental",
        "lease",
        "tenant",
        "landlord",
        "ownership",
        "sale deed",
    ],
    "Criminal Law": [
        "fir",
        "arrest",
        "police",
        "crime",
        "cheating",
        "fraud",
        "bail",
        "harassment",
        "violence",
        "assault",
        "threat",
    ],
    "Family Law": [
        "divorce",
        "marriage",
        "domestic violence",
        "maintenance",
        "custody",
        "husband",
        "wife",
        "498a",
        "alimony",
    ],
    "Cyber Law": [
        "cyber",
        "hacking",
        "hacked",
        "phishing",
        "otp",
        "online fraud",
        "data breach",
        "digital",
        "social media",
        "account hacked",
        "account hack",
        "unauthorized access",
    ],
    "Tax Law": [
        "tax",
        "gst",
        "income tax",
        "tds",
        "assessment",
        "itr",
    ],
    "Contract Law": [
        "contract",
        "agreement",
        "breach",
        "clause",
        "indemnity",
        "liability",
        "terms and conditions",
    ],
    "Legal Notice Drafting": [
        "legal notice",
        "draft notice",
        "notice draft",
        "consumer complaint",
        "rti application",
        "affidavit",
        "demand notice",
    ],
    "Document Analysis": [
        "analyze document",
        "review document",
        "uploaded document",
        "attached image",
        "ocr",
        "contract review",
        "document analysis",
        "[text extracted from attached image]",
    ],
    "Case Law Research": [
        "case law",
        "judgment",
        "supreme court",
        "high court",
        "precedent",
        "ruling",
    ],
    "Rights and Obligations": [
        "right",
        "rights",
        "obligation",
        "obligations",
        "duty",
        "liable",
    ],
}


def is_greeting(question: str) -> bool:
    normalized = question.strip().lower()
    return bool(
        re.fullmatch(
            r"(hi|hello|hey|hii+|good morning|good afternoon|good evening)([!.?, ]*)",
            normalized,
        )
    )


def classify_intent(question: str) -> str:
    normalized = question.strip().lower()

    for category, keywords in INTENT_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return category

    if any(word in normalized for word in ("right", "rights", "legal", "law", "section", "act")):
        return "Legal Information"

    return "General Legal Guidance"


def detect_timeline_need(question: str) -> bool:
    normalized = question.lower()
    return any(
        token in normalized
        for token in (
            "date",
            "deadline",
            "within",
            "days",
            "months",
            "years",
            "notice period",
            "limitation",
            "timeline",
        )
    ) or bool(re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", normalized))


def build_context_block(relevant_laws: list[dict]) -> str:
    return "\n\n".join(
        (
            f"Source {index}\n"
            f"Act Name: {law['act']}\n"
            f"Section Number: {law['section']}\n"
            f"Similarity Score: {law.get('similarity', 0):.2f}\n"
            f"Exact Citation: {law['content']}"
        )
        for index, law in enumerate(relevant_laws, start=1)
    )


def build_prompt(
    question: str,
    relevant_laws: list[dict],
    intent_category: str,
    confidence_score: int,
    confidence_level: str,
) -> str:
    if is_greeting(question):
        return f"""You are LegalDoc AI, a legal assistant focused on Indian law.
The user only greeted you.
Reply warmly in 1-2 short sentences.
Mention that you can help with Indian legal rights, laws, procedures, and documents.
Do not provide legal analysis unless asked.

User message: {question}
"""

    context = build_context_block(relevant_laws)
    timeline_needed = "Yes" if detect_timeline_need(question) else "No"

    return f"""You are LegalDoc AI, a production-ready Indian legal RAG assistant.

Core rules:
- Use retrieved legal content as your primary and controlling source.
- Do not fabricate sections, citations, clauses, judgments, timelines, or outcomes.
- Do not claim to be a licensed advocate or provide representation.
- If the available retrieved material is insufficient, clearly say so.
- If case law is not present in the retrieved sources, say that no case law was available in the current database context.
- If important facts are missing, ask short clarifying questions before giving highly specific conclusions.
- Keep citations in English even if the user requested another response language.

Working context:
- Intent category: {intent_category}
- Confidence score to display exactly: {confidence_score}%
- Confidence level to display exactly: {confidence_level}
- Timeline analysis needed: {timeline_needed}
- Retrieved source count: {len(relevant_laws)}

User question:
{question}

Retrieved legal sources:
{context}

Required response format:
## Summary
Provide a simple explanation for the user.

## Relevant Legal Provisions
List only the applicable retrieved acts and sections. If some retrieved sources are weakly related, say so briefly.

## Legal Analysis
Explain how the retrieved law applies, including rights, obligations, possible violations, remedies, risks, and limitations.
If the query looks like document analysis or contract review, identify likely clause risks, unusual obligations, and points that should be reviewed by a lawyer.
If key facts are missing, say what is missing before giving narrow conclusions.
If timeline analysis is needed, include the important events, deadlines, or limitation-period considerations that can be inferred from the user question and retrieved law.

## Recommended Actions
Give practical next steps as bullets.
Include clarifying questions here if more facts are needed.
If the user is asking for drafting help, give a professional draft-ready outline or sample that is clearly marked as needing lawyer review.

## Risk Assessment
Choose exactly one: Low Risk, Medium Risk, or High Risk.
Explain why.
If this is a contract or document review, you may additionally mention Safe, Review Recommended, or High Risk inside the explanation when helpful.

## Confidence Score
Write exactly: Confidence Score: {confidence_score}% ({confidence_level})

## Citations
For each citation used, include:
- Act Name
- Section Number
- Exact Citation

## Legal Disclaimer
Write exactly:
{DISCLAIMER}

Additional citation rules:
- Cite only retrieved sources.
- Do not invent an act name, section number, or quoted text.
- If a retrieved source is used, quote its exact citation text accurately from the provided context.
- If a retrieved source is not actually useful, do not cite it.
"""

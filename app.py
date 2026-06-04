from __future__ import annotations

import re
import shutil
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any
from uuid import uuid4

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = PROJECT_ROOT / "python_backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from PIL import Image

from app.config import settings
from app.data.fallback_laws import fallback_laws
from app.services.law_service import fetch_laws_from_db
from app.services.llm_service import ask_question
from app.utils.law_filters import filter_and_group_laws

LANGUAGES = [
    {"code": "en-IN", "label": "English", "ocr": "eng"},
    {"code": "hi-IN", "label": "Hindi", "ocr": "hin"},
    {"code": "mr-IN", "label": "Marathi", "ocr": "mar"},
    {"code": "ta-IN", "label": "Tamil", "ocr": "tam"},
    {"code": "te-IN", "label": "Telugu", "ocr": "tel"},
    {"code": "bn-IN", "label": "Bengali", "ocr": "ben"},
    {"code": "gu-IN", "label": "Gujarati", "ocr": "guj"},
    {"code": "kn-IN", "label": "Kannada", "ocr": "kan"},
    {"code": "ml-IN", "label": "Malayalam", "ocr": "mal"},
    {"code": "pa-IN", "label": "Punjabi", "ocr": "pan"},
]

LANGUAGE_MAP = {item["code"]: item for item in LANGUAGES}

ACT_ICONS = {
    "Indian Penal Code": "⚔️",
    "Information Technology Act 2000": "💻",
    "Indian Contract Act 1872": "📝",
    "Consumer Protection Act 2019": "🛒",
    "Right to Information Act 2005": "📢",
    "Motor Vehicles Act 1988": "🚗",
    "Hindu Marriage Act 1955": "💍",
    "Protection of Women from Domestic Violence Act 2005": "🛡️",
    "POCSO Act 2012": "👶",
    "Constitution of India": "🏛️",
    "Code of Criminal Procedure 1973": "⚖️",
    "Indian Evidence Act 1872": "📋",
}

NAV_ITEMS = [
    {
        "id": "chat",
        "label": "Chat",
        "icon": "💬",
        "description": "Conversations and answers",
    },
    {
        "id": "laws",
        "label": "Laws Explorer",
        "icon": "📚",
        "description": "Browse acts and sections",
    },
    {
        "id": "about",
        "label": "About",
        "icon": "ℹ️",
        "description": "Project notes and scope",
    },
]

SUGGESTED_QUESTIONS = [
    "What is cyber bullying?",
    "What is FIR?",
    "My salary is not paid, what can I do?",
    "What is Section 498A?",
]

DISCLAIMER = (
    "This tool provides general legal information and is not legal advice. "
    "Please consult a qualified lawyer for advice on your specific case."
)


st.set_page_config(
    page_title="AI Legal Q&A",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top, rgba(223, 194, 140, 0.24), transparent 32%),
                linear-gradient(180deg, #f8f4ec 0%, #eef2f6 100%);
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #102542 0%, #0b1729 100%);
        }
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(214, 177, 123, 0.12);
        }
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stMarkdown *,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] h5,
        [data-testid="stSidebar"] h6 {
            color: #f5efe4;
        }
        [data-testid="stSidebar"] .stButton > button {
            background: #f5efe4;
            color: #102542;
            border: 1px solid rgba(214, 177, 123, 0.28);
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: #fff7ea;
            color: #0b1729;
            border-color: rgba(214, 177, 123, 0.45);
        }
        [data-testid="stSidebar"] .stButton > button p,
        [data-testid="stSidebar"] .stButton > button span {
            color: inherit !important;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: #f5efe4;
            color: #102542;
            border: 1px solid rgba(214, 177, 123, 0.28);
        }
        [data-testid="stSidebar"] [data-baseweb="select"] svg {
            fill: #102542;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] span {
            color: #102542 !important;
        }
        .sidebar-brand {
            background: linear-gradient(160deg, rgba(255, 247, 234, 0.08), rgba(214, 177, 123, 0.08));
            border: 1px solid rgba(214, 177, 123, 0.18);
            border-radius: 22px;
            padding: 1rem 1rem 0.95rem 1rem;
            margin-bottom: 0.9rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        }
        .sidebar-kicker {
            color: #d6b17b;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }
        .sidebar-title {
            color: #fff7ea;
            font-size: 1.35rem;
            font-weight: 700;
            margin: 0;
        }
        .sidebar-copy {
            color: rgba(245, 239, 228, 0.82);
            font-size: 0.92rem;
            margin: 0.35rem 0 0 0;
            line-height: 1.45;
        }
        .sidebar-stats {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin-top: 0.85rem;
        }
        .sidebar-stat {
            background: rgba(255, 247, 234, 0.08);
            border: 1px solid rgba(255, 247, 234, 0.08);
            border-radius: 999px;
            color: #fff7ea;
            font-size: 0.78rem;
            padding: 0.28rem 0.6rem;
        }
        .sidebar-section-label {
            color: #d6b17b;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin: 1rem 0 0.55rem 0;
        }
        .sidebar-footer-card {
            background: rgba(255, 247, 234, 0.04);
            border: 1px solid rgba(255, 247, 234, 0.08);
            border-radius: 18px;
            padding: 0.9rem 0.95rem;
            margin-top: 0.9rem;
        }
        .sidebar-footer-card p {
            margin: 0;
        }
        .history-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 0.9rem 0 0.45rem 0;
        }
        .history-count {
            background: rgba(214, 177, 123, 0.14);
            border: 1px solid rgba(214, 177, 123, 0.24);
            color: #fff7ea;
            border-radius: 999px;
            font-size: 0.72rem;
            padding: 0.18rem 0.5rem;
        }
        .hero-card {
            background: linear-gradient(135deg, rgba(16, 37, 66, 0.96), rgba(138, 96, 43, 0.92));
            border: 1px solid rgba(214, 177, 123, 0.35);
            border-radius: 24px;
            color: #fff7ea;
            padding: 1.5rem 1.6rem;
            box-shadow: 0 18px 40px rgba(16, 37, 66, 0.14);
            margin-bottom: 1rem;
        }
        .hero-title {
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 0.35rem 0;
        }
        .hero-copy {
            font-size: 1rem;
            margin: 0;
            opacity: 0.9;
        }
        .status-pill {
            display: inline-block;
            background: rgba(255, 247, 234, 0.12);
            border: 1px solid rgba(255, 247, 234, 0.15);
            border-radius: 999px;
            padding: 0.3rem 0.7rem;
            margin: 0.55rem 0.45rem 0 0;
            font-size: 0.85rem;
        }
        .source-note {
            color: #54606e;
            font-size: 0.9rem;
            margin-top: -0.2rem;
            margin-bottom: 0.8rem;
        }
        .citation-card {
            background: rgba(16, 37, 66, 0.04);
            border: 1px solid rgba(16, 37, 66, 0.1);
            border-radius: 16px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.65rem;
        }
        .meta-strip {
            color: #5f6b7a;
            font-size: 0.9rem;
            margin-bottom: 0.75rem;
        }
        .law-meta {
            color: #6b7280;
            font-size: 0.9rem;
        }
        .small-note {
            color: #7a8494;
            font-size: 0.86rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state() -> None:
    st.session_state.setdefault("chat_sessions", [])
    st.session_state.setdefault("active_chat_id", None)
    st.session_state.setdefault("selected_language", "en-IN")
    st.session_state.setdefault("composer_nonce", 0)
    st.session_state.setdefault("current_view", "chat")


def new_chat(title: str = "New Chat") -> dict[str, Any]:
    chat = {
        "id": uuid4().hex,
        "title": title,
        "messages": [],
        "created_at": datetime.now().isoformat(),
    }
    st.session_state.chat_sessions.insert(0, chat)
    st.session_state.active_chat_id = chat["id"]
    return chat


def get_active_chat() -> dict[str, Any] | None:
    active_chat_id = st.session_state.active_chat_id
    for chat in st.session_state.chat_sessions:
        if chat["id"] == active_chat_id:
            return chat
    return None


def delete_chat(chat_id: str) -> None:
    st.session_state.chat_sessions = [
        chat for chat in st.session_state.chat_sessions if chat["id"] != chat_id
    ]
    if st.session_state.active_chat_id == chat_id:
        st.session_state.active_chat_id = (
            st.session_state.chat_sessions[0]["id"]
            if st.session_state.chat_sessions
            else None
        )


def get_language_name(code: str) -> str:
    return LANGUAGE_MAP.get(code, LANGUAGE_MAP["en-IN"])["label"]


def build_question(question: str, language: str, ocr_text: str = "") -> str:
    final_question = question.strip()
    if ocr_text:
        final_question = (
            f"{final_question}\n\n[Text extracted from attached image]:\n{ocr_text}"
            if final_question
            else f"Please analyze this legal text extracted from an image:\n\n{ocr_text}"
        )

    if language != "en-IN":
        final_question = f"{final_question} (Please respond in {get_language_name(language)})"

    return final_question


def maybe_extract_text_from_image(image_bytes: bytes, language: str) -> tuple[str, str | None]:
    try:
        import pytesseract
    except ImportError:
        return "", "Install `pytesseract` to enable OCR for uploaded documents."

    if not shutil.which("tesseract"):
        return "", "Install the `tesseract` binary to enable OCR for uploaded documents."

    try:
        image = Image.open(BytesIO(image_bytes))
        text = pytesseract.image_to_string(
            image,
            lang=LANGUAGE_MAP.get(language, LANGUAGE_MAP["en-IN"])["ocr"],
        ).strip()
        return text, None if text else "No readable text was detected in the uploaded image."
    except Exception as error:
        return "", f"Image OCR could not be completed: {error}"


def parse_answer_sections(text: str) -> dict[str, str]:
    cleaned_text = text.replace(DISCLAIMER, "").strip()
    if "## " in cleaned_text:
        heading_map = {
            "summary": "summary",
            "relevant legal provisions": "relevant_legal_provisions",
            "legal analysis": "legal_analysis",
            "recommended actions": "recommended_actions",
            "risk assessment": "risk_assessment",
            "confidence score": "confidence_score",
            "citations": "citations_text",
            "legal disclaimer": "legal_disclaimer",
            "disclaimer": "legal_disclaimer",
        }
        sections: dict[str, list[str]] = {value: [] for value in heading_map.values()}
        current_section = "summary"

        for raw_line in cleaned_text.splitlines():
            line = raw_line.strip()
            if not line:
                if sections.get(current_section):
                    sections[current_section].append("")
                continue

            if line.startswith("##"):
                heading = re.sub(r"^#+\s*", "", line).strip().lower()
                current_section = heading_map.get(heading, current_section)
                continue

            sections.setdefault(current_section, []).append(raw_line.rstrip())

        return {key: "\n".join(value).strip() for key, value in sections.items()}

    lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]
    sections: dict[str, list[str]] = {
        "answer": [],
        "explanation": [],
        "punishment": [],
        "advice": [],
    }
    current_section = "answer"

    for line in lines:
        normalized = line.lower()
        if "explanation:" in normalized or "what it means:" in normalized:
            current_section = "explanation"
            sections[current_section].append(re.sub(r"^.*?:", "", line).strip())
            continue
        if "punishment:" in normalized or "penalty:" in normalized:
            current_section = "punishment"
            sections[current_section].append(re.sub(r"^.*?:", "", line).strip())
            continue
        if (
            normalized.startswith("you can")
            or normalized.startswith("you should")
            or "steps:" in normalized
            or "what to do:" in normalized
        ):
            current_section = "advice"
            sections[current_section].append(re.sub(r"^.*?:", "", line).strip())
            continue

        sections[current_section].append(line)

    if not any(sections[key] for key in ("explanation", "punishment", "advice")):
        sections["answer"] = [cleaned_text]

    return {key: "\n".join(value).strip() for key, value in sections.items()}


def render_assistant_message(message: dict[str, Any], index: int) -> None:
    sections = parse_answer_sections(message["text"])

    meta_parts = []
    if message.get("intent_category"):
        meta_parts.append(f"Category: {message['intent_category']}")
    if message.get("confidence_score") is not None and message.get("confidence_level"):
        meta_parts.append(
            f"Confidence: {message['confidence_score']}% ({message['confidence_level']})"
        )
    if message.get("retrieved_sources_count") is not None:
        meta_parts.append(f"Sources: {message['retrieved_sources_count']}")
    if meta_parts:
        st.markdown(
            f"<div class='meta-strip'>{' · '.join(meta_parts)}</div>",
            unsafe_allow_html=True,
        )

    summary = sections.get("summary") or sections.get("answer") or ""
    if summary:
        st.markdown(summary)

    citations = message.get("citations") or []
    provisions_text = sections.get("relevant_legal_provisions", "")
    if citations or provisions_text:
        with st.expander("Relevant Legal Provisions", expanded=True):
            if provisions_text:
                st.markdown(provisions_text)
            for citation in citations:
                st.markdown(
                    (
                        "<div class='citation-card'>"
                        f"<strong>{citation['act']}</strong><br>"
                        f"<span class='law-meta'>Section {citation['section']}</span><br>"
                        f"<span class='law-meta'>Similarity: {citation.get('similarity', 0)}</span><br><br>"
                        f"{citation.get('exact_citation', '')}"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

    legal_analysis = sections.get("legal_analysis") or sections.get("explanation") or ""
    if legal_analysis:
        with st.expander("Legal Analysis", expanded=True):
            st.markdown(legal_analysis)

    risk_assessment = sections.get("risk_assessment") or sections.get("punishment") or ""
    if risk_assessment:
        with st.expander("Risk Assessment", expanded=True):
            st.markdown(risk_assessment)

    recommended_actions = sections.get("recommended_actions") or sections.get("advice") or ""
    if recommended_actions:
        with st.expander("Recommended Actions", expanded=True):
            st.markdown(recommended_actions)

    confidence_text = sections.get("confidence_score", "")
    if confidence_text:
        with st.expander("Confidence Score", expanded=False):
            st.markdown(confidence_text)

    citations_text = sections.get("citations_text", "")
    if citations_text and not citations:
        with st.expander("Citations", expanded=False):
            st.markdown(citations_text)

    with st.expander("Disclaimer", expanded=False):
        st.caption(sections.get("legal_disclaimer") or DISCLAIMER)

    audio_key = f"tts_{index}"
    if st.button("Read aloud", key=audio_key):
        from app.services.voice_service import synthesize_speech

        try:
            audio_bytes = synthesize_speech(message["text"])
            st.audio(audio_bytes, format="audio/mp3")
        except Exception as error:
            st.info(f"Speech playback is unavailable right now: {error}")


def load_laws(search: str) -> tuple[dict[str, list[dict[str, Any]]], int, str]:
    try:
        rows = fetch_laws_from_db(search)
        grouped, total = filter_and_group_laws(rows)
        return grouped, total, "database"
    except Exception:
        grouped, total = filter_and_group_laws(fallback_laws, search)
        return grouped, total, "fallback"


def handle_question_submission(prompt: str, uploaded_image: Any | None) -> None:
    chat = get_active_chat() or new_chat()

    image_bytes = uploaded_image.getvalue() if uploaded_image is not None else b""
    ocr_text = ""
    ocr_note = None

    if image_bytes:
        ocr_text, ocr_note = maybe_extract_text_from_image(
            image_bytes,
            st.session_state.selected_language,
        )

    user_message = {
        "type": "user",
        "text": prompt.strip(),
        "image_bytes": image_bytes if image_bytes else None,
        "ocr_text": ocr_text,
        "ocr_note": ocr_note,
        "created_at": datetime.now().isoformat(),
    }
    chat["messages"].append(user_message)

    if len(chat["messages"]) == 1:
        chat["title"] = (prompt.strip() or "Image analysis")[:40]

    final_question = build_question(
        prompt,
        st.session_state.selected_language,
        ocr_text=ocr_text,
    )

    with st.spinner("Researching the relevant law and drafting an answer..."):
        try:
            response = ask_question(final_question)
            assistant_message = {
                "type": "assistant",
                "text": response["answer"],
                "citations": response.get("citations", []),
                "intent_category": response.get("intent_category"),
                "confidence_score": response.get("confidence_score"),
                "confidence_level": response.get("confidence_level"),
                "retrieved_sources_count": response.get("retrieved_sources_count"),
                "created_at": datetime.now().isoformat(),
            }
        except Exception as error:
            assistant_message = {
                "type": "assistant",
                "text": (
                    "Sorry, I couldn't generate a legal answer right now.\n\n"
                    f"Error: {error}"
                ),
                "citations": [],
                "created_at": datetime.now().isoformat(),
            }

    chat["messages"].append(assistant_message)
    st.session_state.composer_nonce += 1
    st.rerun()


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-brand">
                <div class="sidebar-kicker">Legal Workspace</div>
                <p class="sidebar-title">⚖️ AI Legal Q&A</p>
                <p class="sidebar-copy">Know your rights, explore Indian laws, and keep every legal conversation in one place.</p>
                <div class="sidebar-stats">
                    <span class="sidebar-stat">{len(st.session_state.chat_sessions)} chats</span>
                    <span class="sidebar-stat">{get_language_name(st.session_state.selected_language)}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("+ New chat", use_container_width=True):
            new_chat()
            st.session_state.current_view = "chat"
            st.rerun()

        st.markdown("<div class='sidebar-section-label'>Navigate</div>", unsafe_allow_html=True)
        current_view = st.radio(
            "Navigate",
            options=[item["id"] for item in NAV_ITEMS],
            format_func=lambda item_id: next(
                f"{item['icon']}  {item['label']}" for item in NAV_ITEMS if item["id"] == item_id
            ),
            index=next(
                (idx for idx, item in enumerate(NAV_ITEMS) if item["id"] == st.session_state.current_view),
                0,
            ),
            label_visibility="collapsed",
            key="sidebar_nav",
        )
        st.session_state.current_view = current_view

        st.markdown("<div class='sidebar-section-label'>Response Language</div>", unsafe_allow_html=True)
        st.selectbox(
            "Response language",
            options=[item["code"] for item in LANGUAGES],
            format_func=get_language_name,
            key="selected_language",
            label_visibility="collapsed",
        )

        if current_view == "chat":
            st.markdown(
                f"""
                <div class="history-header">
                    <div class="sidebar-section-label" style="margin:0;">Recent Chats</div>
                    <span class="history-count">{len(st.session_state.chat_sessions)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if not st.session_state.chat_sessions:
                st.caption("No conversations yet.")
            for chat in st.session_state.chat_sessions:
                title_col, delete_col = st.columns([5, 1])
                with title_col:
                    if st.button(
                        chat["title"],
                        key=f"open_{chat['id']}",
                        use_container_width=True,
                    ):
                        st.session_state.active_chat_id = chat["id"]
                        st.session_state.current_view = "chat"
                        st.rerun()
                with delete_col:
                    if st.button("x", key=f"delete_{chat['id']}"):
                        delete_chat(chat["id"])
                        st.rerun()

        st.markdown(
            """
            <div class="sidebar-footer-card">
                <p><strong>Private session</strong></p>
                <p class="small-note">Your legal information stays in this current Streamlit session.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not settings.openrouter_api_key:
            st.warning("`OPENROUTER_API_KEY` is missing, so chat answers will fail until it is configured.")

    return current_view


def render_chat_view() -> None:
    active_chat = get_active_chat()

    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Legal answers with citations</div>
            <p class="hero-copy">Ask questions about Indian laws, review relevant sections, and keep your conversation history in one Python UI.</p>
            <span class="status-pill">Chat history</span>
            <span class="status-pill">Regional language prompting</span>
            <span class="status-pill">Law citations</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not active_chat:
        st.info("Start a new conversation from the sidebar or use one of the suggested prompts below.")
    elif not active_chat["messages"]:
        st.markdown(f"### {active_chat['title']}")
        st.markdown(
            f"<p class='source-note'>Responses can be requested in {get_language_name(st.session_state.selected_language)}.</p>",
            unsafe_allow_html=True,
        )

    suggestion_columns = st.columns(len(SUGGESTED_QUESTIONS))
    for column, question in zip(suggestion_columns, SUGGESTED_QUESTIONS):
        with column:
            if st.button(question, key=f"suggest_{question}", use_container_width=True):
                handle_question_submission(question, None)

    if active_chat:
        for index, message in enumerate(active_chat["messages"]):
            role = "user" if message["type"] == "user" else "assistant"
            with st.chat_message(role):
                if message["type"] == "user":
                    st.markdown(message["text"] or "Uploaded an image for analysis.")
                    if message.get("image_bytes"):
                        st.image(message["image_bytes"], caption="Uploaded document", use_container_width=True)
                    if message.get("ocr_text"):
                        with st.expander("Extracted text from image", expanded=False):
                            st.text(message["ocr_text"])
                    if message.get("ocr_note"):
                        st.caption(message["ocr_note"])
                else:
                    render_assistant_message(message, index)

    st.markdown("### Ask a question")
    uploader_key = f"chat_image_{st.session_state.composer_nonce}"
    uploaded_image = st.file_uploader(
        "Optional: attach a legal document image",
        type=["png", "jpg", "jpeg", "webp"],
        key=uploader_key,
    )
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Document preview", use_container_width=True)
        st.caption(
            "OCR is optional in this Streamlit version and activates only when `pytesseract` and the `tesseract` binary are installed."
        )

    prompt = st.chat_input("Type your legal question here...")
    if prompt:
        handle_question_submission(prompt, uploaded_image)


def render_laws_view() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">Laws Explorer</div>
            <p class="hero-copy">Search across acts, sections, and keywords, then inspect the matching provisions in a clean expandable list.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    search = st.text_input("Search laws, sections, or keywords")
    grouped_laws, total, source = load_laws(search)
    act_names = list(grouped_laws.keys())

    st.markdown(
        f"<p class='source-note'>{total} sections across {len(act_names)} acts · Source: {source}</p>",
        unsafe_allow_html=True,
    )

    if not act_names:
        st.info(f"No laws found for '{search}'.")
        return

    for act in act_names:
        icon = ACT_ICONS.get(act, "📄")
        with st.expander(f"{icon} {act} ({len(grouped_laws[act])})", expanded=bool(search)):
            for law in grouped_laws[act]:
                st.markdown(f"**Section {law['section']} - {law['title']}**")
                st.write(law["content"])
                keywords = law.get("keywords") or []
                if keywords:
                    st.caption("Keywords: " + ", ".join(keywords))
                st.divider()


def render_about_view() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">About This Project</div>
            <p class="hero-copy">This Streamlit app now acts as the primary UI while reusing the existing Python legal search and LLM services from the project backend.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Architecture")
    st.markdown(
        "- `app.py` is the new Streamlit interface.\n"
        "- `python_backend/app/services/llm_service.py` still handles legal retrieval and answer generation.\n"
        "- `python_backend/app/services/law_service.py` still loads searchable law sections.\n"
        "- The old React frontend remains in `frontend/` if you want to keep it as a separate client."
    )

    st.markdown("### Notes")
    st.markdown(
        "- Chat answers require `OPENROUTER_API_KEY`.\n"
        "- The assistant now classifies queries, returns structured legal sections, includes confidence scoring, and cites exact retrieved provisions.\n"
        "- Laws Explorer falls back to bundled sample laws when the database is unavailable.\n"
        "- Case law research is only partial right now because this repo does not yet store a dedicated case law database.\n"
        "- Image OCR is optional in this Streamlit version and needs `pytesseract` plus a local `tesseract` install."
    )

    st.caption(DISCLAIMER)


def main() -> None:
    inject_styles()
    initialize_state()
    view = render_sidebar()

    if view == "chat":
        render_chat_view()
    elif view == "laws":
        render_laws_view()
    else:
        render_about_view()


if __name__ == "__main__":
    main()

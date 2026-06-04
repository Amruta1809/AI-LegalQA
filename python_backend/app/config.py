import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None

if load_dotenv is not None:
    load_dotenv()


def _normalize_secret(value: str | None) -> str:
    if value is None:
        return ""

    normalized = str(value).strip()
    if (
        len(normalized) >= 2
        and normalized[0] == normalized[-1]
        and normalized[0] in {"'", '"'}
    ):
        normalized = normalized[1:-1].strip()

    return normalized


def _get_setting(name: str, default: str = "") -> str:
    env_value = _normalize_secret(os.getenv(name))
    if env_value:
        return env_value

    if st is not None:
        try:
            secret_value = st.secrets.get(name)
        except Exception:
            secret_value = None
        normalized_secret = _normalize_secret(secret_value)
        if normalized_secret:
            return normalized_secret

    return default


@dataclass(frozen=True)
class Settings:
    port: int = int(_get_setting("PORT", "5000"))
    database_url: str = _get_setting("DATABASE_URL", "")
    openrouter_api_key: str = _get_setting("OPENROUTER_API_KEY", "")
    huggingface_api_key: str = _get_setting("HUGGINGFACE_API_KEY", "")
    app_url: str = _get_setting("APP_URL", "http://localhost:8501")
    openrouter_stt_model: str = _get_setting("OPENROUTER_STT_MODEL", "openai/whisper-large-v3")
    openrouter_tts_model: str = _get_setting("OPENROUTER_TTS_MODEL", "openai/gpt-4o-mini-tts-2025-12-15")
    tts_voice: str = _get_setting("TTS_VOICE", "alloy")


settings = Settings()

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    port: int = int(os.getenv("PORT", "5000"))
    database_url: str = os.getenv("DATABASE_URL", "")
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    huggingface_api_key: str = os.getenv("HUGGINGFACE_API_KEY", "")
    app_url: str = os.getenv("APP_URL", "http://localhost:5173")
    openrouter_stt_model: str = os.getenv("OPENROUTER_STT_MODEL", "openai/whisper-large-v3")
    openrouter_tts_model: str = os.getenv("OPENROUTER_TTS_MODEL", "openai/gpt-4o-mini-tts-2025-12-15")
    tts_voice: str = os.getenv("TTS_VOICE", "alloy")


settings = Settings()

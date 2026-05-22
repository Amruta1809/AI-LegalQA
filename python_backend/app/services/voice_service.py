import base64
from dataclasses import dataclass

import requests

from ..config import settings

OPENROUTER_TRANSCRIBE_URL = "https://openrouter.ai/api/v1/audio/transcriptions"
OPENROUTER_SPEECH_URL = "https://openrouter.ai/api/v1/audio/speech"


@dataclass
class VoiceServiceError(Exception):
    message: str
    status: int = 500
    code: str = "voice_error"
    details: str = ""


def get_audio_extension(mime_type: str = "") -> str:
    if "webm" in mime_type:
        return "webm"
    if "mp4" in mime_type:
        return "mp4"
    if "mpeg" in mime_type:
        return "mp3"
    if "wav" in mime_type:
        return "wav"
    if "ogg" in mime_type:
        return "ogg"
    return "webm"


def get_language_hint(language: str = "") -> str:
    return language.split("-")[0] or "en"


def parse_audio_data_url(audio_data_url: str) -> tuple[str, str]:
    try:
        metadata, base64_data = audio_data_url.split(",", 1)
    except ValueError as error:
        raise ValueError("Invalid audio payload.") from error

    if not metadata.startswith("data:") or not metadata.endswith(";base64"):
        raise ValueError("Unsupported audio format.")

    mime_type = metadata[5:-7]
    return mime_type, base64_data


def read_error_payload(response: requests.Response) -> tuple[str, str | None]:
    raw = response.text
    try:
        parsed = response.json()
    except ValueError:
        return raw, None

    message = parsed.get("error", {}).get("message") or parsed.get("message") or raw
    code = parsed.get("error", {}).get("code") or parsed.get("code")
    return message, code


def transcribe_audio(audio_data_url: str, language: str = "en-IN") -> str:
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is required for voice transcription.")

    mime_type, base64_data = parse_audio_data_url(audio_data_url)
    extension = get_audio_extension(mime_type)

    response = requests.post(
        OPENROUTER_TRANSCRIBE_URL,
        json={
            "model": settings.openrouter_stt_model,
            "input_audio": {
                "data": base64_data,
                "format": extension,
            },
            "language": get_language_hint(language),
        },
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.app_url,
            "X-OpenRouter-Title": "AI Legal Q&A",
        },
        timeout=60,
    )

    if not response.ok:
        message, code = read_error_payload(response)
        raise VoiceServiceError(message=message, status=response.status_code, code=code or "transcription_failed")

    data = response.json()
    return data.get("text", "").strip()


def synthesize_speech(text: str) -> bytes:
    if not settings.openrouter_api_key:
        raise ValueError("OPENROUTER_API_KEY is required for text-to-speech.")

    response = requests.post(
        OPENROUTER_SPEECH_URL,
        json={
            "model": settings.openrouter_tts_model,
            "voice": settings.tts_voice,
            "input": text,
            "response_format": "mp3",
        },
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.app_url,
            "X-OpenRouter-Title": "AI Legal Q&A",
        },
        timeout=60,
    )

    if not response.ok:
        message, code = read_error_payload(response)
        raise VoiceServiceError(message=message, status=response.status_code, code=code or "speech_generation_failed")

    return response.content

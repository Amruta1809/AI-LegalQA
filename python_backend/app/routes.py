from fastapi import APIRouter, HTTPException, Response

from .data.fallback_laws import fallback_laws
from .models import AskRequest, VoiceSpeakRequest, VoiceTranscribeRequest
from .services.llm_service import ask_question
from .services.voice_service import VoiceServiceError, synthesize_speech, transcribe_audio
from .utils.law_filters import filter_and_group_laws
from .services.law_service import fetch_laws_from_db

router = APIRouter()


@router.post("/ask")
def ask(request: AskRequest) -> dict:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    try:
        return ask_question(question)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get("/laws")
def get_laws(search: str = "") -> dict:
    try:
        rows = fetch_laws_from_db(search)
        grouped, total = filter_and_group_laws(rows)
        return {"laws": grouped, "total": total, "source": "database"}
    except Exception:
        grouped, total = filter_and_group_laws(fallback_laws, search)
        return {"laws": grouped, "total": total, "source": "fallback"}


@router.post("/voice/transcribe")
def voice_transcribe(request: VoiceTranscribeRequest) -> dict:
    if not request.audio:
        raise HTTPException(status_code=400, detail="Audio is required.")

    try:
        text = transcribe_audio(request.audio, request.language)
        return {"text": text}
    except VoiceServiceError as error:
        raise HTTPException(status_code=error.status, detail=error.message) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.post("/voice/speak")
def voice_speak(request: VoiceSpeakRequest) -> Response:
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required.")

    try:
        audio_bytes = synthesize_speech(request.text)
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except VoiceServiceError as error:
        raise HTTPException(status_code=error.status, detail=error.message) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

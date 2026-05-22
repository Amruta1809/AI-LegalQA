from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class VoiceTranscribeRequest(BaseModel):
    audio: str
    language: str = "en-IN"


class VoiceSpeakRequest(BaseModel):
    text: str

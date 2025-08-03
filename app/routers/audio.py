from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.models.models import AudioResponse
from app.services.AudioTranscript import AudioTranscript
from app.services.AgentOrchestrator import AgentOrchestrator

router = APIRouter(prefix="/audio", tags=["audio"])


@router.get("/")
def get_audio():
    return {"message": "Este endpoint é para subir arquivos de audio"}


@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    audio_transcript: AudioTranscript = Depends(AudioTranscript),
    agent_orchestrator: AgentOrchestrator = Depends(AgentOrchestrator),
) -> dict:

    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser de áudio")

    return await audio_transcript.transcript_audio(file, agent_orchestrator)

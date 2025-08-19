from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from app.models.models import AudioResponse
from app.services.AudioTranscript import AudioTranscript
from app.services.AgentOrchestrator import AgentOrchestrator
from app.security.security import SecurityManager
import json
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


router = APIRouter(prefix="/audio", tags=["audio"])


@router.get("/")
def get_audio():
    return {"message": "Este endpoint é para subir arquivos de audio"}


@router.post("/upload")
@limiter.limit("10/minute")
async def upload_audio(
    headers: Request,
    file: UploadFile = File(...),
    audio_transcript: AudioTranscript = Depends(AudioTranscript),
    security_manager: SecurityManager = Depends(SecurityManager),
) -> AudioResponse:

    security_manager.authenticate_user(headers)

    if file.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Arquivo muito grande")

    allowed_extensions = [".wav", ".mp3", ".m4a", ".webm"]
    if not any(file.filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Formato de arquivo não suportado")

    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser de áudio")

    try:
        decrypted_data = await security_manager.decrypt_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao decriptografar arquivo")

    transcript = await audio_transcript.transcript_audio(decrypted_data)

    return transcript.output


@router.post("/prontuario")
@limiter.limit("10/minute")
async def get_prontuario(
    headers: Request,
    json_data: dict,
    agent_orchestrator: AgentOrchestrator = Depends(AgentOrchestrator),
    security_manager: SecurityManager = Depends(SecurityManager),
) -> dict:

    security_manager.authenticate_user(headers)

    if "transcription" not in json_data:
        raise HTTPException(status_code=400, detail="Transcrição não encontrada")

    if len(json_data["transcription"]) == 0:
        raise HTTPException(status_code=400, detail="Transcrição vazia")

    if type(json_data["transcription"]) != str:
        raise HTTPException(status_code=400, detail="Transcrição no formato errado")

    return json.loads(await agent_orchestrator.process_audio_transcript(json_data))

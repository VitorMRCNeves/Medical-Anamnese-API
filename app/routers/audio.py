from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from app.models.models import AudioResponse
from app.services.AudioTranscript import AudioTranscript
from app.services.AgentOrchestrator import AgentOrchestrator
from app.security.security import SecurityManager
import json

router = APIRouter(prefix="/audio", tags=["audio"])


@router.get("/")
def get_audio():
    return {"message": "Este endpoint é para subir arquivos de audio"}


@router.post("/upload")
async def upload_audio(
    headers: Request,
    file: UploadFile = File(...),
    audio_transcript: AudioTranscript = Depends(AudioTranscript),
    security_manager: SecurityManager = Depends(SecurityManager),
) -> AudioResponse:

    security_manager.authenticate_user(headers)

    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser de áudio")

    try:
        decrypted_data = await security_manager.decrypt_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao decriptografar arquivo")

    transcript = await audio_transcript.transcript_audio(decrypted_data)

    return transcript.output


@router.post("/prontuario")
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


# @router.post("/summary")
# async def get_patient_summary(
#     json_data: dict,
#     amnanesis_summary: AmnanesisSummary = Depends(AmnanesisSummary),
# ) -> dict:
#     return await amnanesis_summary.get_patient_summary(json_data, agent_orchestrator)

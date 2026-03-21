from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from app.models.models import AudioResponse
from app.services.AudioTranscript import AudioTranscript
from app.services.AgentOrchestrator import AgentOrchestrator
from app.config.ConfigDependencies import AppConfigs
import json


def audio_router(deps: AppConfigs):
    router = APIRouter(prefix="/audio", tags=["audio"])

    async def get_transcript() -> AudioTranscript:
        """
        Dependency injection para GraphExecutionManager.

        Returns:
            GraphExecutionManager: Instância configurada do gerenciador de execução
        """
        return AudioTranscript(deps=deps)

    async def get_orchestrator() -> AgentOrchestrator:
        return AgentOrchestrator(deps=deps)

    @router.get("/")
    def get_audio():
        return {"message": "Este endpoint é para subir arquivos de audio"}

    @router.post("/upload")
    async def upload_audio(
        headers: Request,
        file: UploadFile = File(...),
        audio_transcript: AudioTranscript = Depends(get_transcript),
    ) -> AudioResponse:

        deps.security_manager.authenticate_user(headers)

        if file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Arquivo muito grande")

        allowed_extensions = [".wav", ".mp3", ".m4a", ".webm"]
        if not any(file.filename.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400, detail="Formato de arquivo não suportado"
            )

        if not file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Arquivo deve ser de áudio")

        try:
            decrypted_data = await deps.security_manager.decrypt_file(file)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail="Erro ao decriptografar arquivo"
            )

        transcript = await audio_transcript.transcript_audio(decrypted_data)

        return transcript.output

    @router.post("/prontuario")
    async def get_prontuario(
        headers: Request,
        json_data: dict,
        agent_orchestrator: AgentOrchestrator = Depends(get_orchestrator),
    ) -> dict:

        deps.security_manager.authenticate_user(headers)

        if "transcription" not in json_data:
            raise HTTPException(status_code=400, detail="Transcrição não encontrada")

        if len(json_data["transcription"]) == 0:
            raise HTTPException(status_code=400, detail="Transcrição vazia")

        if type(json_data["transcription"]) != str:
            raise HTTPException(status_code=400, detail="Transcrição no formato errado")

        return json.loads(await agent_orchestrator.process_audio_transcript(json_data))

    return router

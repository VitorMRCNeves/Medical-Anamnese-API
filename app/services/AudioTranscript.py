from app.services.ChatInterface import ChatInterface
from app.services.prompts.audio_extractor import prompt_extrator
from app.models.models import AudioResponse
from pydantic_ai import BinaryContent
from fastapi import UploadFile
from app.services.AgentOrchestrator import AgentOrchestrator


class AudioTranscript:
    def __init__(self):
        self.chat_interface = ChatInterface()

    async def convert_audio_to_bytes(self, audio_file: UploadFile) -> bytes:

        bytes_content = BinaryContent(data=audio_file, media_type="audio/webm")
        return bytes_content

    async def transcript_audio(self, audio_file: UploadFile) -> AudioResponse:
        """
        Realiza a transcrição do áudio recebido, utilizando o agente de IA configurado.
        O input_type deve ser BinaryContent, pois estamos enviando o conteúdo binário do áudio.
        O erro comum é passar o tipo errado ou a estrutura errada para o agente.

        Args:
            audio_file (str): Caminho do arquivo de áudio a ser transcrito.

        Returns:
            AudioResponse: Objeto contendo a transcrição.
        """
        agent = self.chat_interface.create_agent(
            system_prompt=prompt_extrator(),
            output_type=AudioResponse,
        )
        audio_transcript = await agent.run(
            [await self.convert_audio_to_bytes(audio_file)]
        )

        return audio_transcript

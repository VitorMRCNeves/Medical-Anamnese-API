from app.services.ChatInterface import ChatInterface
from pydantic import BaseModel, ValidationError
from typing import Type
from app.models.models import criar_modelo_pydantic
from fastapi import HTTPException

from app.services.prompts.prompts_anamnese import (
    prompt_patient_info,
    prompt_generic_validator,
)


class AgentOrchestrator:
    def __init__(self):
        self.chat_interface = ChatInterface()

    async def validate_extraction(
        self, audio_transcript: str, extracted_data: dict
    ) -> bool:
        agent = self.chat_interface.create_agent(
            system_prompt=prompt_generic_validator(),
            output_type=bool,
        )
        return await agent.run(extracted_data)

    async def create_agent_for_extraction(
        self, audio_transcript: str, fields: Type[BaseModel]
    ) -> dict:

        agent = self.chat_interface.create_agent(
            system_prompt=prompt_patient_info(),
            output_type=fields,
        )
        extracted_data = await agent.run(audio_transcript)

        if not self.validate_extraction_model(extracted_data, fields):
            raise HTTPException(status_code=400, detail="Erro ao validar modelo")

        if not await self.create_agent_for_validation(
            audio_transcript, extracted_data.output
        ):
            raise HTTPException(
                status_code=400,
                detail="Transcricao nao corresponde ao extraído",
            )

        return extracted_data

    def validate_extraction_model(
        self, extracted_data: Type[BaseModel], model: Type[BaseModel]
    ) -> bool:

        try:
            model.model_validate(extracted_data.output)
            return True
        except ValidationError as e:
            print(e)
            return False

    async def create_agent_for_validation(
        self, audio_transcript: str, extracted_data: Type[BaseModel]
    ) -> bool:
        agent = self.chat_interface.create_agent(
            system_prompt=prompt_generic_validator(),
            instructions=f"Verifique se a transcricao corresponde ao extraído, se sim, retorne True, se nao, retorne False: {audio_transcript}",
            output_type=bool,
        )
        bolean = await agent.run(extracted_data.model_dump_json())
        return bolean.output

    async def process_audio_transcript(self, json_request: dict) -> dict:
        audio_transcript = json_request["transcription"]
        model = criar_modelo_pydantic(json_request["anamnesis_template"])

        results = await self.create_agent_for_extraction(audio_transcript, model)

        return results.output.model_dump_json()

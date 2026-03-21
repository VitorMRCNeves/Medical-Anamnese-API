from app.config.ConfigDependencies import AppConfigs
from app.agents.validator import TranscriptValidatorAgent
from app.agents.anamnese import AnamnesesModelingAgent
from pydantic import BaseModel, ValidationError
from typing import Type
from app.models.models import criar_modelo_pydantic
from fastapi import HTTPException


class AgentOrchestrator:
    def __init__(self, deps: AppConfigs):
        self.deps = deps

    async def validate_extraction(
        self, audio_transcript: str, extracted_data: dict
    ) -> bool:
        lazy_transcritor = TranscriptValidatorAgent(
            self.deps, llm_model=self.deps.google_model
        )

        return lazy_transcritor.execute(audio_transcript, extracted_data)

    async def extract_anamnese(
        self, audio_transcript: str, fields: Type[BaseModel]
    ) -> dict:
        lazy_anamnese = AnamnesesModelingAgent(
            self.deps, llm_model=self.deps.google_model
        )

        extracted_data = await lazy_anamnese.execute(audio_transcript, fields)

        validation = await self.validate_extraction_model(extracted_data, fields)

        if not validation:
            raise HTTPException(status_code=400, detail="Erro ao validar modelo")

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

    async def process_audio_transcript(self, json_request: dict) -> dict:
        audio_transcript = json_request["transcription"]
        model = criar_modelo_pydantic(json_request["anamnesis_template"])

        results = await self.extract_anamnese(audio_transcript, model)

        return results.output.model_dump_json()

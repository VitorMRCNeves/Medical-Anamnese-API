from app.services.ChatInterface import ChatInterface
import asyncio
from app.models.models import (
    PatientInfo,
    MainComplaint,
    MedicalHistory,
    MedicationHistory,
    PatientAllergies,
    PatientFamilyHistory,
    VitalSigns,
)
from app.services.prompts.audio_extractor import prompt_extrator


class AgentOrchestrator:
    def __init__(self):
        self.chat_interface = ChatInterface()

    async def extract_patient_info(self, audio_transcript: str) -> PatientInfo:
        agent = self.chat_interface.create_agent(
            system_prompt=prompt_extrator(),
            output_type=PatientInfo,
        )
        audio_transcript = await agent.run([audio_transcript])

        return audio_transcript.output

    async def extract_main_complaint(self, audio_transcript: str) -> MainComplaint:
        agent = self.chat_interface.create_agent(
            system_prompt=prompt_extrator(),
            output_type=MainComplaint,
        )
        audio_transcript = await agent.run([audio_transcript])

        return audio_transcript.output

    async def extract_medical_history(self, audio_transcript: str) -> MedicalHistory:
        agent = self.chat_interface.create_agent(
            system_prompt=prompt_extrator(),
            output_type=MedicalHistory,
        )
        audio_transcript = await agent.run([audio_transcript])

        return audio_transcript.output

    async def extract_medication_history(
        self, audio_transcript: str
    ) -> MedicationHistory:
        agent = self.chat_interface.create_agent(
            system_prompt=prompt_extrator(),
            output_type=MedicationHistory,
        )
        audio_transcript = await agent.run([audio_transcript])

        return audio_transcript.output

    async def extract_allergies(self, audio_transcript: str) -> PatientAllergies:
        agent = self.chat_interface.create_agent(
            system_prompt=prompt_extrator(),
            output_type=PatientAllergies,
        )
        audio_transcript = await agent.run([audio_transcript])

        return audio_transcript.output

    async def extract_family_history(
        self, audio_transcript: str
    ) -> PatientFamilyHistory:
        agent = self.chat_interface.create_agent(
            system_prompt=prompt_extrator(),
            output_type=PatientFamilyHistory,
        )
        audio_transcript = await agent.run([audio_transcript])

        return audio_transcript.output

    async def extract_vital_signs(self, audio_transcript: str) -> VitalSigns:
        agent = self.chat_interface.create_agent(
            system_prompt=prompt_extrator(),
            output_type=VitalSigns,
        )
        audio_transcript = await agent.run([audio_transcript])

        return audio_transcript.output

    def formatar_resultados(self, results):
        """
        Formata a lista de objetos retornados pelas extrações em um dicionário estruturado.

        Args:
            results (list): Lista de objetos das extrações.

        Returns:
            dict: Dicionário estruturado com os dados extraídos.
        """
        # Desempacota os resultados na ordem esperada
        (
            patient_info,
            main_complaint,
            medical_history,
            medication_history,
            allergies,
            family_history,
            vital_signs,
        ) = results

        # Constrói o dicionário de resposta
        dados_formatados = {
            "informacoes_paciente": (
                patient_info.dict() if hasattr(patient_info, "dict") else {}
            ),
            "queixa_principal": (
                main_complaint.dict() if hasattr(main_complaint, "dict") else {}
            ),
            "historico_medico": (
                medical_history.dict() if hasattr(medical_history, "dict") else {}
            ),
            "medicacoes": (
                medication_history.dict() if hasattr(medication_history, "dict") else {}
            ),
            "alergias": allergies.dict() if hasattr(allergies, "dict") else {},
            "historico_familiar": (
                family_history.dict() if hasattr(family_history, "dict") else {}
            ),
            "sinais_vitais": vital_signs.dict() if hasattr(vital_signs, "dict") else {},
        }

        return dados_formatados

    async def process_audio_transcript(self, audio_transcript: str) -> dict:

        audio_transcript = audio_transcript.transcription
        extracoes = [
            self.extract_patient_info(audio_transcript),
            self.extract_main_complaint(audio_transcript),
            self.extract_medical_history(audio_transcript),
            self.extract_medication_history(audio_transcript),
            self.extract_allergies(audio_transcript),
            self.extract_family_history(audio_transcript),
            self.extract_vital_signs(audio_transcript),
        ]

        results = await asyncio.gather(*extracoes, return_exceptions=True)

        results = self.formatar_resultados(results)

        return results

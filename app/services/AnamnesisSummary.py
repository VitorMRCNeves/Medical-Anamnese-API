from app.services.ChatInterface import ChatInterface
from app.services.prompts.prompts_anamnese import prompt_anamnesis_summary


class AnamnesisSummary:
    def __init__(self):
        self.chat_interface = ChatInterface()

    async def get_patient_summary(self, json_data: dict) -> str:
        agent = self.chat_interface.create_agent(
            system_prompt=prompt_anamnesis_summary(),
            output_type=str,
        )
        return await agent.run([json_data])

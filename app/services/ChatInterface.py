from typing import Any
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
import os


class ChatInterface:
    def __init__(self):
        self.model = GeminiModel(
            model_name="gemini-2.0-flash",
            provider=GoogleGLAProvider(
                api_key="AIzaSyByp54YcGVlQWDF4NJnO6JTmPfEhvxZ1wQ"
            ),
        )

    def create_agent(self, system_prompt: str, output_type: Any) -> Agent:

        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            output_type=output_type,
        )

        return agent

from typing import Any
import os
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider


class ChatInterface:
    def __init__(self):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        self.model = GeminiModel(
            model_name="gemini-2.0-flash",
            provider=GoogleGLAProvider(api_key=google_api_key),
        )

    def create_agent(
        self, system_prompt: str, output_type: Any, instructions: str = None
    ) -> Agent:

        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            output_type=output_type,
            instructions=instructions,
        )

        return agent

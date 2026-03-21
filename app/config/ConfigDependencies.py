from dataclasses import dataclass
from app.services.ConfigManager import ConfigManager
from app.security.security import SecurityManager
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from typing import Optional, List, Dict
import os


@dataclass
class AppConfigs:
    config_manager: ConfigManager
    security_manager: SecurityManager
    google_model: GeminiModel
    is_production: bool

    @classmethod
    def load_dependencies(cls):
        config_instance = ConfigManager()
        security_instance = SecurityManager()
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        google_model = GeminiModel(
            model_name="gemini-2.0-flash",
            provider=GoogleGLAProvider(api_key=google_api_key),
        )
        IS_PRODUCTION = (
            os.getenv("RAILWAY_ENVIRONMENT") is not None
            or os.getenv("PORT") is not None
        )

        instance = cls(
            config_manager=config_instance,
            security_manager=security_instance,
            google_model=google_model,
            is_production=IS_PRODUCTION,
        )

        return instance


@dataclass
class AgentExecutionInputs:
    """
    Entrada padronizada para execução de agentes.

    Contém todas as informações necessárias para executar um agente:
    - Mensagem do usuário
    - Contexto da conversa
    - Identificação do usuário
    - Prompt customizado (opcional)
    """

    message: str
    user_id: Optional[str] = None
    context: Optional[List[Dict]] = None
    prompt: str | None = None

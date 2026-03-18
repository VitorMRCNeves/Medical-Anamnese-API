import logging
from typing import Optional, Dict, Any
from pydantic_ai import Agent
from agents.AgentBase import BaseAgent
from config.ConfigDependencies import AppConfigs
from pydantic_ai import BinaryContent
from fastapi import UploadFile
from app.models.models import AudioResponse

logger = logging.getLogger(__name__)


class TranscriptAgent(BaseAgent):
    """
    Agente transcritor para transcrever a Anamnese.
    """

    def __init__(
        self,
        deps: AppConfigs,
        llm_model: Any,
    ):
        """
        Inicializa o agente transcritor.
        """
        super().__init__(
            agent_name="transcritor",
            config_manager=deps.config_manager,
            llm_model=llm_model,
        )
        self._agent: Optional[Agent] = None
        self._deps = deps

    def _inicia_agente(self) -> Agent:
        """
        Inicializa a instância do agente com prompt personalizado.

        Returns:
            Instância do Agent configurado
        """
        self._agent = self._create_agent_instance(
            output_type=AudioResponse,
        )
        return self._agent

    async def execute(
        self,
        audio: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Executa o agente transcritor de intenção com a mensagem e contexto do usuário.

        Args:
            message: Mensagem do usuário
            user_id: ID do usuário (opcional, para personalização)
            context: Contexto adicional (histórico, metadata, etc) do N8N

        Returns:
            Resposta do agente como string

        Raises:
            Exception: Erros durante a execução
        """
        try:
            agent = self._inicia_agente()

            logger.info(
                f"Executando agente de intenção para user_id={user_id}, "
                f"message_length={len(message)}"
            )

            result = await agent.run(
                message,
            )

            response = result.output

            if isinstance(response, IntencaoConversa):
                logger.info(
                    f"Agente de intenção executado com sucesso para user_id={user_id}"
                )
            else:
                logger.warning(
                    f"Saída do agente de intenção não é do tipo esperado: {type(response)}"
                )

            logger.info(
                f"Agente de intenção executado com sucesso para user_id={user_id}"
            )

            return response

        except Exception as e:
            logger.error(
                f"Erro ao executar agente de intenção: {e}",
                exc_info=True,
            )
            raise

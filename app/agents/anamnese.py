import logging
from typing import Optional, Dict, Any
from pydantic_ai import Agent
from pydantic import BaseModel
from app.agents.AgentBase import BaseAgent
from app.config.ConfigDependencies import AppConfigs

logger = logging.getLogger(__name__)


class AnamnesesModelingAgent(BaseAgent):
    """
    Agente modela a Anamnese apartir da transcrição.
    """

    def __init__(
        self,
        deps: AppConfigs,
        llm_model: Any,
    ):
        """
        Inicializa o agente anamnese.
        """
        super().__init__(
            agent_name="anamnese",
            config_manager=deps.config_manager,
            llm_model=llm_model,
        )
        self._agent: Optional[Agent] = None
        self._deps = deps

    def _inicia_agente(self, fields) -> Agent:
        """
        Inicializa a instância do agente com prompt personalizado.

        Returns:
            Instância do Agent configurado
        """
        self._agent = self._create_agent_instance(
            output_type=fields,
        )
        return self._agent

    async def execute(
        self,
        transcript: str,
        fields: BaseModel,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Executa o agente validador, recebendo o transcript e o extraction,
        e valida se a extraction está boa o suficiente dado o transcript.

        Args:
            transcript: Transcrição da consulta médica
            user_id: ID do usuário (opcional)
            context: Contexto adicional (opcional)

        Returns:
            Resposta do agente como string (True/False)

        Raises:
            Exception: Erros durante a execução
        """
        try:
            agent = self._inicia_agente()

            logger.info(
                f"Executando agente validador para user_id={user_id}, "
                f"message_length={len(transcript)}"
            )

            user_prompt = (
                "A seguir está a transcrição completa de uma consulta médica. "
                "Com base apenas nesse transcript, extraia e retorne um JSON com os campos relevantes da anamnese conforme o modelo esperado. "
                "Certifique-se de preencher todos os campos possíveis a partir das informações disponíveis, mantendo a precisão e completude. "
                "Retorne apenas o JSON extraído, sem explicações adicionais.\n\n"
                "TRANSCRIÇÃO:\n"
                f"{transcript}\n\n"
                "Retorne o JSON de campos extraídos:"
            )

            result = await agent.run(user_prompt)

            response = result.output

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

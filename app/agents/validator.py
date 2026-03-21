import logging
from typing import Optional, Dict, Any
from pydantic_ai import Agent
from app.agents.AgentBase import BaseAgent
from app.config.ConfigDependencies import AppConfigs

logger = logging.getLogger(__name__)


class TranscriptValidatorAgent(BaseAgent):
    """
    Agente validador para transcrever a Anamnese.
    """

    def __init__(
        self,
        deps: AppConfigs,
        llm_model: Any,
    ):
        """
        Inicializa o agente validador.
        """
        super().__init__(
            agent_name="validador",
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
            output_type=bool,
        )
        return self._agent

    async def execute(
        self,
        transcript: str,
        extraction: dict,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Executa o agente validador, recebendo o transcript e o extraction,
        e valida se a extraction está boa o suficiente dado o transcript.

        Args:
            transcript: Transcrição da consulta médica
            extraction: Dicionário com os dados extraídos do transcript
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
                "Você receberá abaixo uma transcrição de uma consulta médica e, em seguida, um JSON "
                "representando as informações extraídas dessa transcrição. "
                "Sua tarefa é validar se a extração (JSON) está boa o suficiente, "
                "ou seja, se reflete com precisão e qualidade todas as informações contidas no transcript. "
                "\n\n"
                "TRANSCRIÇÃO:\n"
                f"{transcript}\n\n"
                "EXTRAÇÃO (JSON extraído):\n"
                f"{extraction}\n\n"
                "Responda apenas True (se a extração está adequada) ou False (se faltar algo ou tiver inconsistências)."
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

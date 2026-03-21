import logging
from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic_ai import Agent, RunContext
from app.services.ChatInterface import AgentFactory
from app.services.ConfigManager import ConfigManager
from app.config.ConfigDependencies import AgentExecutionInputs

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Classe base para todos os agentes da aplicação.
    Fornece estrutura comum para carregar prompts e criar agentes.
    """

    def __init__(
        self,
        agent_name: str,
        config_manager: ConfigManager,
        llm_model: Any,
    ):
        """
        Inicializa o agente base.

        Args:
            agent_name: Nome do agente (deve corresponder ao YAML)
            config_manager: Instância do ConfigManager
            llm_model: Modelo de linguagem a ser usado pelo agente
        """
        self.agent_name = agent_name
        self.config_manager = config_manager
        self.agent_factory = AgentFactory(llm_model=llm_model)
        self._agent: Optional[Agent] = None
        self._config: Optional[dict] = None
        self._load_config()

    def _load_config(self) -> None:
        """
        Carrega configuração do prompt do ConfigManager.
        """
        try:
            self._config = self.config_manager.get(self.agent_name)
            logger.debug(f"Configuração carregada para agente '{self.agent_name}'")
        except KeyError as e:
            logger.error(f"Erro ao carregar config do agente '{self.agent_name}': {e}")
            raise

    def _build_system_prompt(self, ctx: RunContext[AgentExecutionInputs]) -> str:
        """
        Constrói o system prompt genérico para o agente, podendo incluir variáveis dinâmicas
        com base nas dependências de execução.

        Returns:
            System prompt formatado
        """
        base_prompt = self.config_manager.get_system_prompt(self.agent_name)

        try:
            return base_prompt.format(
                user_id=ctx.deps.user_id if ctx.deps.user_id else "",
            )
        except KeyError as e:
            logger.warning(
                f"Campo '{e}' não encontrado no prompt YAML para agente '{self.agent_name}'. Usando prompt sem formatação completa."
            )
            return base_prompt

    def _get_instructions(self) -> str:
        """
        Obtém as instruções do prompt.

        Returns:
            String com as instruções
        """
        return self.config_manager.get_instructions(self.agent_name)

    def _create_agent_instance(
        self,
        output_type: Any = str,
        deps_type: Any = None,
        **agent_kwargs: Any,
    ) -> Agent:
        """
        Cria instância do agente pydantic-ai usando a fábrica injetada.

        Args:
            output_type: Tipo de saída esperado
            deps_type: Tipo de dependência para o Pydantic AI

        Returns:
            Instância do Agent configurado
        """

        agent = self.agent_factory.create_agent(
            system_prompt=(
                self.config_manager.get_system_prompt(self.agent_name)
                if self.agent_name != "conversational"
                else ""
            ),
            output_type=output_type,
            instructions=self._get_instructions(),
            deps_type=deps_type,
            agent_name=self.agent_name,
            **agent_kwargs,
        )

        logger.debug(f"Agente '{self.agent_name}' criado com sucesso")
        return agent

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Método abstrato que deve ser implementado por cada agente específico.
        Define a lógica de execução do agente.

        Args:
            **kwargs: Parâmetros específicos de cada agente

        Returns:
            Resultado da execução do agente
        """
        pass

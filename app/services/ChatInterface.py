import asyncio
import logging
from functools import wraps
from typing import Any
from pydantic_ai import Agent

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = (408, 429, 500, 502, 503, 504)
MAX_RETRY_ATTEMPTS = 5
INITIAL_RETRY_DELAY_SECONDS = 1.0
MAX_RETRY_DELAY_SECONDS = 16.0


class AgentFactory:
    def __init__(self, llm_model):
        self.llm_model = llm_model

    def _is_retryable_exception(self, exc: Exception) -> bool:
        """
        Decide se a exceção deve disparar retry.

        Cobre falhas transitórias típicas de chamadas LLM/HTTP sem depender
        rigidamente de uma classe específica do provider.
        """
        status_code = getattr(exc, "status_code", None)
        if status_code in RETRYABLE_STATUS_CODES:
            return True

        response = getattr(exc, "response", None)
        response_status = getattr(response, "status_code", None)
        if response_status in RETRYABLE_STATUS_CODES:
            return True

        exc_name = exc.__class__.__name__.lower()
        if exc_name in {
            "ratelimiterror",
            "apiconnectionerror",
            "apitimeouterror",
            "serviceunavailableerror",
            "internalservererror",
        }:
            return True

        message = str(exc).lower()
        retryable_fragments = (
            "429",
            "408",
            "500",
            "502",
            "503",
            "504",
            "rate limit",
            "resource exhausted",
            "resource_exhausted",
            "deadline exceeded",
            "timed out",
            "timeout",
            "temporarily unavailable",
            "service unavailable",
            "connection reset",
            "connection aborted",
            "server error",
        )
        return any(fragment in message for fragment in retryable_fragments)

    async def _run_with_retry(self, run_method, *args, **kwargs):
        delay = INITIAL_RETRY_DELAY_SECONDS
        last_exception = None

        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            try:
                return await run_method(*args, **kwargs)
            except Exception as exc:
                last_exception = exc

                if attempt == MAX_RETRY_ATTEMPTS or not self._is_retryable_exception(
                    exc
                ):
                    raise

                logger.warning(
                    "Falha transitória ao executar agente '%s' (tentativa %s/%s). "
                    "Retry em %.1fs. Erro: %s",
                    getattr(self.llm_model, "model_name", "unknown-model"),
                    attempt,
                    MAX_RETRY_ATTEMPTS,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, MAX_RETRY_DELAY_SECONDS)

        raise last_exception

    def _wrap_agent_run_with_retry(self, agent: Agent) -> Agent:
        original_run = agent.run

        @wraps(original_run)
        async def run_with_retry(*args, **kwargs):
            return await self._run_with_retry(original_run, *args, **kwargs)

        agent.run = run_with_retry
        return agent

    def create_agent(
        self,
        system_prompt: Any,
        agent_name: str | None,
        output_type: Any = str,
        instructions: str = "",
        deps_type: Any = None,
        model_settings: Any = None,
        tools: Any | None = None,
    ) -> Agent:
        """
        Cria um agente do Pydantic AI para processar a mensagem do usuário.

        Args:
            system_prompt (Any): Prompt de sistema para o agente.
            agent_name (str | None): Nome do agente.
            output_type (Any): Tipo de saída do agente.
            instructions (str): Instruções para o agente.
            deps_type (Any): Tipo de dependência para o agente.
            model_settings (Any): Configurações do modelo.
            tools (Any | None): Ferramentas disponíveis para o agente.

        Returns:
            Agent: Instância do agente configurado com lógica de retry.
        """
        agent = Agent(
            model=self.llm_model,
            system_prompt=system_prompt,
            output_type=output_type,
            instructions=instructions,
            deps_type=deps_type,
            name=agent_name,
            model_settings=model_settings if model_settings else None,
            tools=tools if tools else [],
        )

        return self._wrap_agent_run_with_retry(agent)

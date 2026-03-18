import yaml
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Singleton responsável por carregar e gerenciar prompts de arquivos YAML.
    Suporta hot reload via método reload().
    """

    _instance: Optional["ConfigManager"] = None
    _prompts: Dict[str, dict] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._prompts_dir = Path(__file__).parent.parent / "config" / "configuracao"
            self._initialized = True
            self.load_all()

    def _load_yaml(self, file_path: Path) -> dict:
        """
        Carrega e valida um arquivo YAML.

        Args:
            file_path: Caminho para o arquivo YAML

        Returns:
            Dict com o conteúdo do YAML

        Raises:
            FileNotFoundError: Se o arquivo não existir
            yaml.YAMLError: Se o YAML estiver mal formatado
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                if content is None:
                    logger.error(f"Arquivo YAML vazio: {file_path}")
                    raise ValueError()
                return content
        except FileNotFoundError:
            logger.error(f"Arquivo de prompt não encontrado: {file_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Erro ao parsear YAML {file_path}: {e}")
            raise

    def _load_agente_prompt(self, prompt_config: dict, yaml_file: Path) -> None:
        agent_name = prompt_config.get("agent")
        if not agent_name:
            logger.warning(
                f"YAML {yaml_file.name} não possui campo 'agent'. Ignorando..."
            )
            raise ValueError(f"YAML {yaml_file.name} não está formatado corretamente")

        self._prompts[agent_name] = prompt_config
        logger.info(f"Prompt '{agent_name}' carregado de {yaml_file.name}")

    def _load_config(self, prompt_config: dict, yaml_file: Path) -> None:
        config_name = prompt_config.get("name")
        if not config_name:

            logger.warning(
                f"YAML {yaml_file.name} não possui campo 'name'. Ignorando..."
            )

            raise ValueError(f"YAML {yaml_file.name} não está formatado corretamente")

        self._configs[config_name] = prompt_config
        logger.info(f"Config '{config_name}' carregado de {yaml_file.name}")

    def load_all(self):
        """
        Carrega todos os arquivos YAML do diretório prompts/.

        Returns:
           None

        Raises:
            FileNotFoundError: Se o diretório prompts/ não existir
        """
        if not self._prompts_dir.exists():
            logger.warning(
                f"Diretório de prompts não encontrado: {self._prompts_dir}. Criando..."
            )
            raise FileNotFoundError(
                f"Diretório de prompts não encontrado: {self._prompts_dir}"
            )

        self._prompts = {}
        self._configs = {}
        yaml_files = list(self._prompts_dir.glob("*.yaml")) + list(
            self._prompts_dir.glob("*.yml")
        )
        for yaml_file in yaml_files:
            try:
                config = self._load_yaml(yaml_file)
                if config.get("type") == "agente_prompt":
                    self._load_agente_prompt(config, yaml_file)
                    continue
                self._load_config(config, yaml_file)
            except Exception as e:
                logger.error(f"Erro ao carregar {yaml_file}: {e}", exc_info=True)

        logger.info(
            f"Total de arquivos carregados: {len(self._prompts) + len(self._configs)}"
        )

    def reload(self) -> Dict[str, dict]:
        """
        Recarrega todos os prompts dos arquivos YAML.
        Útil para hot reload sem reiniciar a aplicação.

        Returns:
            Dict com todos os prompts recarregados
        """
        logger.info("Iniciando reload de prompts...")
        old_count = len(self._prompts)
        self.load_all()
        new_count = len(self._prompts)
        logger.info(
            f"Reload concluído. Antes: {old_count}, Depois: {new_count} prompts"
        )
        return self._prompts

    def get(self, file_name: str, type: str = "agente_prompt") -> dict:
        """
        Obtém configuração de um arquivo específico.

        Args:
            file_name: Nome do arquivo (deve corresponder ao campo 'agent' do YAML)

        Returns:
            Dict com a configuração completa do prompt

        Raises:
            KeyError: Se o arquivo não for encontrado
        """
        if file_name not in [*self._prompts.keys(), *self._configs.keys()]:
            available = ", ".join([*self._prompts.keys(), *self._configs.keys()])
            raise KeyError(
                f"Arquivo de {type} '{file_name}' não encontrado. "
                f"Arquivos disponíveis: {available}"
            )
        if type == "agente_prompt":
            return self._prompts[file_name]

        return self._configs[file_name]

    def get_system_prompt(self, agent_name: str) -> str:
        """
        Extrai apenas o system_prompt de um agente.

        Args:
            agent_name: Nome do agente

        Returns:
            String com o system prompt
        """
        config = self.get(file_name=agent_name)
        return config.get("system_prompt", "")

    def get_instructions(self, agent_name: str) -> str:
        """
        Extrai apenas as instructions de um agente.

        Args:
            agent_name: Nome do agente

        Returns:
            String com as instruções
        """
        config = self.get(file_name=agent_name)
        return config.get("instructions", "")

    def get_prompt_inputs(self, agent_name: str, prompt: str, **kwargs) -> str:
        """
        Extrai apenas as instructions de um agente.

        Args:
            agent_name: Nome do agente

        Returns:
            String com as instruções
        """
        config = self.get(file_name=agent_name)
        prompt = config.get(prompt, "")
        return prompt

    def extrai_propriedades_grupo(
        self, config_name: str, property_name: str, group_name: str
    ) -> None:
        """Extrai todas as propriedades de um grupo."""
        properties = (
            self.get(config_name, {}).get(property_name, {}).get(group_name, [])
        )
        return properties

    def extrai_todas_propriedades_incluidas(
        self, config_name: str, property_name: str
    ) -> None:
        """Extrai todas as propriedades de todos os grupos para cache."""
        self._all_properties = self.get(config_name, {}).get(property_name, {})

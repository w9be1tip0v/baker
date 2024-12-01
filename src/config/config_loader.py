import os
import yaml


class Config:
    """Load and manage configuration settings."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        return self._resolve_env_variables(config)

    def _resolve_env_variables(self, config: dict) -> dict:
        if isinstance(config, dict):
            return {k: self._resolve_env_variables(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._resolve_env_variables(i) for i in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            return os.getenv(env_var) or config
        return config
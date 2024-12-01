import json
import logging
import os
from pathlib import Path

from bs4 import BeautifulSoup
import yaml
from langchain.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.runnables import RunnableSequence
from langchain_xai import ChatXAI

from prompts import get_summary_prompt

# =========================
# Configuration and Logging Setup
# =========================

class Config:
    """Class to load and maintain configuration settings."""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Loads configuration from a YAML file and resolves environment variables."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        return self.resolve_env_variables(config)

    def resolve_env_variables(self, config: dict) -> dict:
        """Resolve environment variable placeholders in the configuration."""
        if isinstance(config, dict):
            return {key: self.resolve_env_variables(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self.resolve_env_variables(item) for item in config]
        elif (
            isinstance(config, str) and config.startswith("${") and config.endswith("}")
        ):
            env_var = config[2:-1]
            env_value = os.getenv(env_var)
            if not env_value:
                raise EnvironmentError(f"Environment variable '{env_var}' is not set.")
            return env_value
        return config


def setup_logging(log_file: str, log_level: str):
    """Set up logging."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


# =========================
# HTML Processing Classes
# =========================

class HTMLExtractor:
    """Class to extract text from HTML files."""

    @staticmethod
    def extract_text(html_path: Path) -> str:
        logger.info(f"Extracting text from HTML file: {html_path}")
        try:
            with open(html_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
                return soup.get_text(separator="\n").strip()
        except Exception as e:
            logger.error(f"Error extracting text from {html_path}: {e}")
            raise


class HTMLAnalyzer:
    """Class to manage HTML analysis and save results."""

    def __init__(self, chat_xai: ChatXAI, prompt_template: PromptTemplate, max_length: int):
        self.chain = RunnableSequence(prompt_template, chat_xai)
        self.max_length = max_length

    def analyze_text(self, text: str) -> dict:
        logger.info("Analyzing text using the Grok AI model.")
        try:
            with get_openai_callback() as cb:
                summary = self.chain.invoke({"document": text})
                summary_text = getattr(summary, "content", str(summary))

                # Truncate if necessary
                if len(summary_text) > self.max_length:
                    summary_text = summary_text[:self.max_length]
                    logger.warning("Summary truncated due to length limit.")

                return {
                    "summary": summary_text,
                    "input_tokens": cb.prompt_tokens,
                    "output_tokens": cb.completion_tokens,
                }
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            raise

    @staticmethod
    def save_to_json(data: dict, output_path: Path):
        logger.info(f"Saving analysis results to {output_path}")
        try:
            with open(output_path, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error saving JSON file: {e}")
            raise


# =========================
# Main Processing Function
# =========================

def load_configuration(config_path: str = "config.yaml") -> dict:
    return Config(config_path).config


def main():
    logger.info("Starting the application.")

    config = load_configuration()
    max_length = config.get("summary", {}).get("max_length", 2500)

    input_dir = Path(config["directories"]["input"])
    output_dir = Path(config["directories"]["output"])
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")

    chat_xai = ChatXAI(
        xai_api_key=config["xai"]["api_key"],
        model=config["xai"]["model"],
        temperature=0.7,
    )
    template = get_summary_prompt(max_length=max_length)
    analyzer = HTMLAnalyzer(chat_xai, template, max_length)

    for html_path in input_dir.glob("*.html"):
        try:
            output_path = output_dir / f"{html_path.stem}_summary.json"
            if output_path.exists():
                logger.info(f"Skipping {html_path.name}: Output file already exists.")
                continue

            text = HTMLExtractor.extract_text(html_path)
            analysis_result = analyzer.analyze_text(text)

            # Replace placeholder in the prompt with actual value
            formatted_prompt = template.template.replace("{max_length}", str(max_length))
            result = {
                "input_html": str(html_path),
                "prompt": formatted_prompt,
                "summary": analysis_result["summary"],
                "input_tokens": analysis_result["input_tokens"],
                "output_tokens": analysis_result["output_tokens"],
            }
            analyzer.save_to_json(result, output_path)
        except Exception as e:
            logger.error(f"Failed to process {html_path.name}: {e}")

    logger.info("Application processing completed.")


if __name__ == "__main__":
    logger = setup_logging(log_file="app.log", log_level="INFO")
    main()
import logging
from pathlib import Path
from config.config_loader import Config
from logging.logger import setup_logger
from extractors.html_extractor import HTMLExtractor
from analyzers.html_analyzer import HTMLAnalyzer
from utils.file_utils import save_to_json
from langchain_xai import ChatXAI
from prompts import get_summary_prompt

def main():
    config = Config().config
    logger = setup_logger(
        config["logging"]["log_file"],
        config["logging"]["log_level"]
    )

    input_dir = Path(config["directories"]["input"])
    output_dir = Path(config["directories"]["output"])
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    html_files = input_dir.glob("*.html")
    if not html_files:
        logger.warning("No HTML files found.")

    chat_xai = ChatXAI(config["xai"]["api_key"])
    template = get_summary_prompt(max_length=config["summary"]["max_length"])

    extractor = HTMLExtractor()
    analyzer = HTMLAnalyzer(chat_xai, template)

    for file in html_files:
        text = extractor.extract_text(file)
        analysis = analyzer.analyze(text)
        save_to_json(analysis, output_dir / f"{file.stem}_summary.json")


if __name__ == "__main__":
    main()
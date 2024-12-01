from pathlib import Path
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class HTMLExtractor:
    """Extract text content from HTML files."""

    @staticmethod
    def extract_text(html_path: Path) -> str:
        try:
            with open(html_path, "r", encoding="utf-8") as file:
                soup = BeautifulSoup(file, "html.parser")
            return soup.get_text(separator="\n").strip()
        except Exception as e:
            logger.error(f"Failed to extract text from {html_path}: {e}")
            raise
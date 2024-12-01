import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def save_to_json(data: dict, output_path: Path):
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Failed to save JSON to {output_path}: {e}")
        raise
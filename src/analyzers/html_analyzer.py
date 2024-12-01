from langchain.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.runnables import RunnableSequence
import logging

logger = logging.getLogger(__name__)


class HTMLAnalyzer:
    """Analyze HTML content and save results."""

    def __init__(self, chat_xai, prompt_template: PromptTemplate, max_length: int = 500):
        self.chain = RunnableSequence(prompt_template, chat_xai)
        self.max_length = max_length

    def analyze(self, text: str) -> dict:
        try:
            with get_openai_callback() as cb:
                summary = self.chain.invoke({"document": text})
            return {
                "summary": summary[: self.max_length],
                "used_tokens": cb.total_tokens,
            }
        except Exception as e:
            logger.error(f"Failed to analyze text: {e}")
            raise
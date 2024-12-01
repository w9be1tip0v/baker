from langchain.prompts import PromptTemplate

def get_summary_prompt(max_length: int) -> PromptTemplate:
    """
    Generate a summary prompt template that ensures the summary does not exceed a specified length.

    Args:
        max_length (int): Maximum length of the summary.

    Returns:
        PromptTemplate: The prompt template for summarization.
    """
    template = (
        "You are an advanced summarization model. Your task is to provide a concise "
        "summary of the given document. The summary must not exceed than {max_length} characters,"
        "ensuring clarity and relevance. Avoid including unnecessary "
        "details or repeating information. If necessary, focus only on the "
        "most critical points to adhere to the character limit.\n\n"
        "Document:\n{document}\n\n"
        "Summary (max {max_length} characters):"
    )
    return PromptTemplate(
        input_variables=["document"],
        template=template,
        partial_variables={"max_length": max_length}
    )
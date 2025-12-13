# from server.ai.llm_processor import extract_with_llm
from server.ai.gpt_extractor import extract_with_gpt

def analyzeResume(text: str) -> dict:
    """
        Method Name: analyzeResume
        Description: Analyzes plain text from resume using TinyLlama via LLM processor.
        Input: Resume text
        Output: Structured resume data (dict)

        Written By: Aman Sharma
        Version: 1.0
    """
    return extract_with_gpt(text)

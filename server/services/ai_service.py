from typing import Dict, Any
from server.ai.llm_client import chat_messages
from server.ai.prompts.registry import load_prompt

def _clean(s: str) -> str:
    return (s or "").strip()

def _require(name: str, val: str, min_len: int = 3) -> str:
    v = _clean(val)
    if len(v) < min_len:
        raise ValueError(f"{name} is required")
    return v

class AIService:
    def cover_letter_uk(self,*,resume_text: str,job_title: str,job_description: str,prompt_version: str = "v1",) -> str:
        resume_text = _require("resume_text",resume_text,50)
        job_title = _require("job_title",job_title,2)
        job_description = _require("job_description",job_description,20)

        template = load_prompt("cover_letter_uk",version=prompt_version)
        base = template.format(resume_text=resume_text,job_title=job_title,job_description=job_description,)

        wrapper = (
            "You are writing for a UK job application.\n"
            "Rules:\n"
            "- Use only the information present in the resume_text and job_description.\n"
            "- Do not invent employers, degrees, dates, skills, or achievements.\n"
            "- If something is missing, write around it professionally.\n"
            "- Keep it UK style: concise, polite, confident, 250-350 words.\n"
            "- Output only the cover letter text.\n\n"
            f"{base}"
        )

        r = chat_messages([{"role": "user","content": wrapper,},],temperature=0.6,max_tokens=750,)
        return r["text"]

    def mock_questions(self,*,resume_text: str,job_description: str,prompt_version: str = "v1",) -> Dict[str, Any]:
        resume_text = _require("resume_text",resume_text,50)
        job_description = _require("job_description",job_description,20)

        template = load_prompt("mock_questions",version=prompt_version)
        base = template.format(resume_text=resume_text,job_description=job_description,)

        wrapper = (
            "Generate mock interview questions for a UK role.\n"
            "Rules:\n"
            "- Questions must be grounded in resume_text and job_description.\n"
            "- Mix behavioural + technical.\n"
            "- Do not ask generic filler questions.\n"
            "- Output valid JSON only.\n\n"
            f"{base}"
        )

        r = chat_messages([{"role": "user","content": wrapper,},],json_mode=True,temperature=0.4,max_tokens=800,)
        return r["json"]

    def career_advice(self,*,question: str,prompt_version: str = "v1",) -> Dict[str, Any]:
        question = _require("question",question,10)

        template = load_prompt("career_advice_plan",version=prompt_version)
        base = template.format(question=question)

        wrapper = (
            "You are a UK-focused career advisor.\n"
            "Rules:\n"
            "- Give a structured action plan.\n"
            "- Be practical and step-by-step.\n"
            "- Do not hallucinate personal facts about the user.\n"
            "- Output valid JSON only.\n\n"
            f"{base}"
        )

        r = chat_messages([{"role": "user","content": wrapper,},],json_mode=True,temperature=0.4,max_tokens=700,)
        return r["json"]
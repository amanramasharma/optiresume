from typing import Dict, Any, List
from pydantic import BaseModel, Field, ValidationError
from server.ai.llm_client import chat_messages
from server.ai.prompts.registry import load_prompt
from server.core.logger import get_logger

log = get_logger("optiresume.resume_ai")

class Links(BaseModel):
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    other: List[str] = Field(default_factory=list)

class Skills(BaseModel):
    technical: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    ml_ai: List[str] = Field(default_factory=list)
    other: List[str] = Field(default_factory=list)

class EducationItem(BaseModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    location: str = ""
    dates: str = ""
    modules: List[str] = Field(default_factory=list)
    grade: str = ""

class ExperienceItem(BaseModel):
    company: str = ""
    title: str = ""
    location: str = ""
    dates: str = ""
    bullets: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)

class ProjectItem(BaseModel):
    name: str = ""
    description: str = ""
    bullets: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    link: str = ""

class CertificationItem(BaseModel):
    name: str = ""
    issuer: str = ""
    date: str = ""

class Evidence(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""

class Confidence(BaseModel):
    contact: int = 0
    summary: int = 0
    skills: int = 0
    experience: int = 0
    education: int = 0
    projects: int = 0
    overall: int = 0

class ResumeExtract(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    links: Links = Field(default_factory=Links)
    summary: str = ""
    skills: Skills = Field(default_factory=Skills)
    education: List[EducationItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    publications: List[str] = Field(default_factory=list)
    awards: List[str] = Field(default_factory=list)
    volunteering: List[str] = Field(default_factory=list)
    evidence: Evidence = Field(default_factory=Evidence)
    confidence: Confidence = Field(default_factory=Confidence)

def extract_resume(resume_text: str,*,prompt_version: str = "v1") -> Dict[str, Any]:
    if not resume_text or len(resume_text.strip()) < 50:
        raise ValueError("Resume text is too short to analyze")

    template = load_prompt("resume_extract",version=prompt_version)
    prompt = template.format(resume_text=resume_text)

    r = chat_messages([{"role": "user","content": prompt,}],json_mode=True,max_tokens=1400,temperature=0.2,)
    data = r["json"]

    try:
        parsed = ResumeExtract.model_validate(data)
    except ValidationError as e:
        log.warning("resume_extract_schema_failed",extra={"error": str(e),},)
        raise ValueError("LLM output failed schema validation")

    out = parsed.model_dump()
    out["meta"] = {"analysis_version": prompt_version,"source": "llm_json","llm_model": r.get("model"),"llm_latency_ms": r.get("latency_ms"),"cache_hit": r.get("cache_hit", False),}
    return out
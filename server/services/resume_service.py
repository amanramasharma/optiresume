from datetime import datetime
from typing import Dict, Any, List
from server.parsers import parseResume
from server.ai.resume_ai import extract_resume
from server.scoring.scorer import score
from server.db.repositories.resumes_repo import ResumesRepo
from server.core.config import load_settings
from server.core.logger import get_logger

log = get_logger("optiresume.resume_service")

def _now() -> str:
    return datetime.utcnow().isoformat()

def _cap_text(text: str, limit: int) -> str:
    t = text or ""
    if len(t) <= limit:
        return t
    return t[:limit] + "\n\n...[truncated]"

class ResumeService:
    def __init__(self):
        self.repo = ResumesRepo()

    async def ingest_and_analyze(self, upload_file, *, email: str) -> str:
        s = load_settings()
        t0 = datetime.utcnow()

        text = await parseResume(upload_file)
        if not text or not text.strip():
            log.info("resume_text_extract_failed",extra={"email": email,"file_name": (upload_file.filename or "").lower(),},)
            raise ValueError("Could not extract text from resume")

        extracted = extract_resume(text,prompt_version="v1")

        extracted["file_name"] = (upload_file.filename or "").lower()
        extracted["uploaded_at"] = _now()
        extracted["uploaded_by"] = email
        extracted["raw_text"] = _cap_text(text,limit=12000)

        scoring = score(extracted)
        extracted["score"] = scoring
        extracted["resume_score"] = scoring["score"]
        extracted["scoring_version"] = scoring.get("rubric_version","v1_uk")

        resume_id = self.repo.create(extracted)

        latency_ms = int((datetime.utcnow() - t0).total_seconds() * 1000)
        log.info("resume_ingest_ok",extra={"email": email,"resume_id": resume_id,"file_name": extracted["file_name"],"latency_ms": latency_ms,"score": extracted["resume_score"],"scoring_version": extracted["scoring_version"],},)

        return resume_id

    def list_uploads(self, email: str) -> List[Dict[str, Any]]:
        items = self.repo.list_for_user(email)
        for it in items:
            it["_id"] = str(it["_id"])
        log.info("resume_list_ok",extra={"email": email,"count": len(items),},)
        return items

    def get_resume(self, resume_id: str, email: str) -> Dict[str, Any]:
        r = self.repo.find_one_for_user(resume_id,email)
        if not r:
            log.info("resume_get_not_found",extra={"email": email,"resume_id": resume_id,},)
            raise KeyError("Resume not found")
        r["_id"] = str(r["_id"])
        log.info("resume_get_ok",extra={"email": email,"resume_id": resume_id,},)
        return r
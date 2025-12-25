from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse
from server.services.ai_service import AIService
from server.services.resume_service import ResumeService
from server.core.logger import get_logger

router = APIRouter()
log = get_logger("optiresume.ai_tools")

ai = AIService()
resumes = ResumeService()

@router.post("/ai/cover_letter")
def cover_letter(request: Request,resume_id: str = Form(...),job_title: str = Form(...),job_description: str = Form(...),):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse("/site/login.html",status_code=302)

    resume = resumes.get_resume(resume_id,email=email)
    text = resume.get("raw_text","")

    result = ai.cover_letter_uk(resume_text=text,job_title=job_title,job_description=job_description,)
    log.info("cover_letter_generated",extra={"email": email,"resume_id": resume_id,},)
    return JSONResponse({"cover_letter": result})

@router.post("/ai/mock_questions")
def mock_questions(request: Request,resume_id: str = Form(...),job_description: str = Form(...),):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse("/site/login.html",status_code=302)

    resume = resumes.get_resume(resume_id,email=email)
    text = resume.get("raw_text","")

    result = ai.mock_questions(resume_text=text,job_description=job_description,)
    log.info("mock_questions_generated",extra={"email": email,"resume_id": resume_id,},)
    return JSONResponse(result)

@router.post("/ai/career_advice")
def career_advice(request: Request,question: str = Form(...),):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse("/site/login.html",status_code=302)

    result = ai.career_advice(question=question)
    log.info("career_advice_generated",extra={"email": email,},)
    return JSONResponse(result)
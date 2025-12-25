from io import BytesIO
from fastapi import APIRouter, File, UploadFile, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from server.services.resume_service import ResumeService
from server.core.logger import get_logger
from server.core.config import load_settings
from server.core.paths import TEMPLATES_DIR

router = APIRouter()
log = get_logger("optiresume.resumes")
svc = ResumeService()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@router.post("/upload_resume")
async def upload_resume(request: Request,resume: UploadFile = File(...)):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse("/site/login.html",status_code=302)

    settings = load_settings()
    filename = (resume.filename or "").lower()

    if not filename.endswith(settings.allowed_extensions):
        return HTMLResponse("<h3>Unsupported file format.</h3>",status_code=400)

    content = await resume.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        return HTMLResponse(f"<h3>File too large (max {settings.max_upload_mb}MB).</h3>",status_code=413,)

    resume.file = BytesIO(content)
    resume.filename = filename

    try:
        resume_id = await svc.ingest_and_analyze(resume,email=email)
        log.info("resume_uploaded",extra={"email": email,"resume_id": resume_id,"file_name": filename,},)
        return RedirectResponse(f"/view_resume/{resume_id}",status_code=302)

    except ValueError as e:
        log.info("resume_upload_validation_error",extra={"email": email,"error": str(e),},)
        return HTMLResponse(f"<h3>{str(e)}</h3>",status_code=400)

    except Exception as e:
        log.exception("resume_upload_failed",extra={"email": email,"error": str(e),},)
        return HTMLResponse("<h3>Resume analysis failed.</h3>",status_code=500)

@router.get("/my_uploads")
def my_uploads(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse("/site/login.html",status_code=302)

    uploads = svc.list_uploads(email=email)
    log.info("my_uploads_view",extra={"email": email,"count": len(uploads),},)

    return templates.TemplateResponse("my_uploads.html",{"request": request,"uploads": uploads,"email": email,},)

@router.get("/view_resume/{resume_id}")
def view_resume(resume_id: str,request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse("/site/login.html",status_code=302)

    try:
        resume = svc.get_resume(resume_id,email=email)
    except KeyError:
        raise HTTPException(status_code=404,detail="Resume not found")

    log.info("resume_view",extra={"email": email,"resume_id": resume_id,},)
    return templates.TemplateResponse("result.html",{"request": request,"result": resume,},)

@router.get("/edit_resume/{resume_id}")
def edit_resume(resume_id: str,request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse("/site/login.html",status_code=302)

    try:
        resume = svc.get_resume(resume_id,email=email)
    except KeyError:
        raise HTTPException(status_code=404,detail="Resume not found")

    log.info("resume_edit_view",extra={"email": email,"resume_id": resume_id,},)
    return templates.TemplateResponse("edit_resume.html",{"request": request,"result": resume,},)
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from server.services.user_service import UserService
from server.core.logger import get_logger

router = APIRouter()
log = get_logger("optiresume.auth")
svc = UserService()

@router.post("/signup")
def signup(username: str = Form(...),email: str = Form(...),password: str = Form(...),):
    try:
        svc.signup(username=username,email=email,password=password)
        log.info("user_signup",extra={"email": (email or "").strip().lower(),},)
        return RedirectResponse("/site/login.html",status_code=302)
    except ValueError as e:
        return HTMLResponse(f"<h2>{str(e)}</h2>",status_code=400)

@router.post("/login")
def login(request: Request,email: str = Form(...),password: str = Form(...),):
    ok = svc.login(email=email,password=password)
    em = (email or "").strip().lower()
    if ok:
        request.session["user_email"] = em
        log.info("user_login",extra={"email": em,},)
        return RedirectResponse("/site/dashboard.html",status_code=302)
    log.info("login_failed",extra={"email": em,},)
    return HTMLResponse("<h2>Invalid credentials</h2>",status_code=401)

@router.get("/logout")
def logout(request: Request):
    email = request.session.get("user_email") or "-"
    request.session.clear()
    log.info("user_logout",extra={"email": email,},)
    return RedirectResponse("/site/login.html",status_code=302)

@router.get("/current_user")
def current_user(request: Request):
    email = request.session.get("user_email")
    if not email:
        return JSONResponse({"error": "Not logged in"},status_code=401)
    return {"email": email}
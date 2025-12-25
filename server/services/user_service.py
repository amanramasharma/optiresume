from passlib.context import CryptContext
from server.db.repositories.users_repo import UsersRepo
from server.core.logger import get_logger

log = get_logger("optiresume.user_service")
_pwd = CryptContext(schemes=["bcrypt"],deprecated="auto")

def _normalize_password(p: str) -> str:
    p = (p or "").strip()
    if len(p.encode("utf-8")) <= 72:
        return p
    import hashlib
    return hashlib.sha256(p.encode("utf-8")).hexdigest()

def _clean_email(email: str) -> str:
    return (email or "").strip().lower()

def _clean_username(username: str) -> str:
    return (username or "").strip()

class UserService:
    def __init__(self):
        self.repo = UsersRepo()

    def signup(self, username: str, email: str, password: str) -> None:
        email = _clean_email(email)
        username = _clean_username(username)
        password = (password or "").strip()

        if not username or not email or not password:
            log.info("signup_missing_fields",extra={"email": email or "-",},)
            raise ValueError("Missing fields")

        if "@" not in email or "." not in email:
            log.info("signup_invalid_email",extra={"email": email,},)
            raise ValueError("Invalid email")

        if len(password) < 8:
            log.info("signup_weak_password",extra={"email": email,},)
            raise ValueError("Password must be at least 8 characters")

        if self.repo.find_by_email(email):
            log.info("signup_email_exists",extra={"email": email,},)
            raise ValueError("Email already registered")

        hashed = _pwd.hash(_normalize_password(password))
        self.repo.create_user(username=username,email=email,password_hash=hashed)
        log.info("signup_ok",extra={"email": email,},)

    def login(self, email: str, password: str) -> bool:
        email = _clean_email(email)
        password = (password or "").strip()

        u = self.repo.find_by_email(email)
        if not u:
            log.info("login_user_not_found",extra={"email": email or "-",},)
            return False

        ok = _pwd.verify(_normalize_password(password),u.get("password",""))
        log.info("login_ok" if ok else "login_failed",extra={"email": email,},)
        return ok
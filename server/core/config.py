import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator

def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip()
    return v if v else default

def _env_int(name: str, default: int) -> int:
    try:
        return int(_env(name, str(default)) or default)
    except Exception:
        return default

def _env_float(name: str, default: float) -> float:
    try:
        return float(_env(name, str(default)) or default)
    except Exception:
        return default

def _env_bool(name: str, default: bool) -> bool:
    v = (_env(name, "true" if default else "false") or "").lower()
    return v in {"1", "true", "yes", "y", "on"}

class Settings(BaseModel):
    app_name: str = Field(default="OptiResume")
    environment: str = Field(default="dev")  # dev | staging | prod
    cors_allow_origins: str = Field(default="*")

    session_secret: str = Field(default="")

    max_upload_mb: int = Field(default=5)
    allowed_extensions: tuple[str, ...] = (".pdf", ".docx", ".png", ".jpeg", ".jpg")

    mongo_uri: str = Field(default="")
    mongo_db_name: str = Field(default="optiresume")

    openai_api_key: str = Field(default="")
    openai_model_default: str = Field(default="gpt-4o-mini")
    openai_timeout_s: int = Field(default=30)
    openai_retries: int = Field(default=2)
    openai_temperature_default: float = Field(default=0.2)
    openai_max_tokens_default: int = Field(default=900)

    llm_cache_enabled: bool = Field(default=True)
    llm_cache_ttl_s: int = Field(default=86400)

    scoring_version: str = Field(default="v1")
    rubric_locale: str = Field(default="UK")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        v = (v or "").strip().lower()
        if v not in {"dev", "staging", "prod"}:
            raise ValueError("environment must be dev, staging, or prod")
        return v

    @field_validator("session_secret")
    @classmethod
    def validate_session_secret(cls, v: str, info):
        env = info.data.get("environment", "dev")
        v = (v or "").strip()
        if env == "prod" and (not v or v == "change-me"):
            raise ValueError("SESSION_SECRET must be securely set in production")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        raw = (self.cors_allow_origins or "").strip()
        if raw == "*" or not raw:
            return ["*"]
        return [x.strip() for x in raw.split(",") if x.strip()]

def load_settings() -> Settings:
    return Settings(
        app_name=_env("APP_NAME", "OptiResume"),
        environment=_env("ENVIRONMENT", "dev"),
        cors_allow_origins=_env("CORS_ALLOW_ORIGINS", "*"),
        session_secret=_env("SESSION_SECRET", _env("SECRET_KEY", "")) or "",

        max_upload_mb=_env_int("MAX_UPLOAD_MB", 5),

        mongo_uri=_env("MONGO_URI", _env("MONGODB_URI", "")) or "",
        mongo_db_name=_env("MONGO_DB_NAME", _env("DB_NAME", "optiresume")) or "optiresume",

        openai_api_key=_env("OPENAI_API_KEY", "") or "",
        openai_model_default=_env("OPENAI_MODEL", "gpt-4o-mini"),
        openai_timeout_s=_env_int("OPENAI_TIMEOUT_S", 30),
        openai_retries=_env_int("OPENAI_RETRIES", 2),
        openai_temperature_default=_env_float("OPENAI_TEMPERATURE", 0.2),
        openai_max_tokens_default=_env_int("OPENAI_MAX_TOKENS", 900),

        llm_cache_enabled=_env_bool("LLM_CACHE_ENABLED", True),
        llm_cache_ttl_s=_env_int("LLM_CACHE_TTL_S", 86400),

        scoring_version=_env("SCORING_VERSION", "v1"),
        rubric_locale=_env("RUBRIC_LOCALE", "UK"),
    )
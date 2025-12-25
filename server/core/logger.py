import os
import sys
import json
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

_request_id: ContextVar[str] = ContextVar("request_id", default="-")

def set_request_id(value: Optional[str]) -> None:
    _request_id.set(value or "-")

def get_request_id() -> str:
    return _request_id.get()

class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base: Dict[str, Any] = {
            "ts": datetime.utcnow().isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": get_request_id(),
        }

        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)

        skip = {
            "name","msg","args","levelname","levelno","pathname","filename","module",
            "exc_info","exc_text","stack_info","lineno","funcName","created","msecs",
            "relativeCreated","thread","threadName","processName","process","message"
        }

        extras: Dict[str, Any] = {}
        for k, v in record.__dict__.items():
            if k in skip:
                continue
            try:
                json.dumps(v)
                extras[k] = v
            except Exception:
                extras[k] = str(v)

        if extras:
            base.update(extras)

        return json.dumps(base, ensure_ascii=False)

_configured = False

def _level_from_env() -> int:
    raw = (os.getenv("LOG_LEVEL") or "INFO").strip().upper()
    return getattr(logging, raw, logging.INFO)

def configure_logging() -> None:
    global _configured
    if _configured:
        return

    level = _level_from_env()
    log_dir = Path(os.getenv("LOG_DIR") or "logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    for h in list(root.handlers):
        root.removeHandler(h)

    formatter = _JsonFormatter()

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(formatter)
    root.addHandler(console)

    file_path = log_dir / (os.getenv("LOG_FILE") or "app.log")
    file_handler = RotatingFileHandler(
        file_path,
        maxBytes=int(os.getenv("LOG_MAX_BYTES") or 5_000_000),
        backupCount=int(os.getenv("LOG_BACKUP_COUNT") or 3),
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    _configured = True

def get_logger(name: str = "optiresume") -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
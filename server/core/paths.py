from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]   # OptiResume/
SERVER_DIR = BASE_DIR / "server"
TEMPLATES_DIR = SERVER_DIR / "templates"
PUBLIC_DIR = BASE_DIR / "public_site"
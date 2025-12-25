from pathlib import Path
from server.core.paths import BASE_DIR

PROMPTS_DIR = Path(BASE_DIR) / "server" / "ai" / "prompts" / "versions"

def load_prompt(name: str, version: str = "v1") -> str:
    path = PROMPTS_DIR / version / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")
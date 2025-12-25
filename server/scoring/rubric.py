from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class RubricItem:
    key: str
    max_points: int
    description: str


RUBRIC_V1_UK: List[RubricItem] = [
    RubricItem("contact", 15, "Name, email, phone present and professional"),
    RubricItem("summary", 10, "Clear 2–3 line summary tailored to target role"),
    RubricItem("skills", 20, "Role-relevant skills depth and clarity"),
    RubricItem("experience", 30, "Experience entries with impact and metrics"),
    RubricItem("education", 15, "Education present with key details"),
    RubricItem("projects", 10, "Projects with stack + outcomes + links where possible"),
]


def rubric_map() -> Dict[str, RubricItem]:
    return {r.key: r for r in RUBRIC_V1_UK}
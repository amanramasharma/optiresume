from typing import Any, Dict, List
from server.scoring.rubric import rubric_map
from server.scoring.explain import REASONS

def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return [value]

def _text_has_metrics(text: str) -> bool:
    if not text:
        return False
    t = text.lower()
    if "%" in t or "+" in t:
        return True
    for ch in t:
        if ch.isdigit():
            return True
    return False

def _experience_has_metrics(experience: List[Any]) -> bool:
    for item in experience:
        if isinstance(item, dict):
            metrics = _as_list(item.get("metrics"))
            if metrics and any(_text_has_metrics(str(m)) for m in metrics):
                return True
            bullets = _as_list(item.get("bullets"))
            if bullets and any(_text_has_metrics(str(b)) for b in bullets):
                return True
            if _text_has_metrics(json_safe_str(item)):
                return True
        else:
            if _text_has_metrics(str(item)):
                return True
    return False

def json_safe_str(obj: Any) -> str:
    try:
        return str(obj)
    except Exception:
        return ""

def score(resume: Dict[str, Any]) -> Dict[str, Any]:
    rmap = rubric_map()
    breakdown: Dict[str, Dict[str, Any]] = {}
    reasons: List[str] = []
    recommendations: List[str] = []

    total_points = 0
    max_points = sum(r.max_points for r in rmap.values())

    contact_points = 0
    if resume.get("name"):
        contact_points += 5
    if resume.get("email"):
        contact_points += 5
    if resume.get("phone"):
        contact_points += 5

    breakdown["contact"] = {"points": contact_points,"max": rmap["contact"].max_points,}
    total_points += contact_points

    summary = (resume.get("summary") or "").strip()
    if summary:
        pts = rmap["summary"].max_points
    else:
        pts = 0
        reasons.append("missing_summary")
        recommendations.append("Add a concise 2–3 line professional summary tailored to your target role.")

    breakdown["summary"] = {"points": pts,"max": rmap["summary"].max_points,}
    total_points += pts

    skills = _as_list((resume.get("skills") or {}).get("technical"))
    if len(skills) >= 8:
        pts = rmap["skills"].max_points
    elif len(skills) >= 4:
        pts = int(rmap["skills"].max_points * 0.6)
        reasons.append("few_skills")
        recommendations.append("Expand your skills section to 8–15 role-relevant tools and technologies.")
    else:
        pts = 0
        reasons.append("few_skills")
        recommendations.append("Add a dedicated Skills section with core tools, frameworks, and technologies.")

    breakdown["skills"] = {"points": pts,"max": rmap["skills"].max_points,"count": len(skills),}
    total_points += pts

    experience = _as_list(resume.get("experience"))
    if experience:
        if _experience_has_metrics(experience):
            pts = rmap["experience"].max_points
        else:
            pts = int(rmap["experience"].max_points * 0.66)
            reasons.append("no_metrics")
            recommendations.append("Add measurable impact to experience (e.g., % improvement, scale, users, performance).")
    else:
        pts = 0
        reasons.append("missing_experience")
        recommendations.append("Add at least one experience entry (job, internship, research, or major project).")

    breakdown["experience"] = {"points": pts,"max": rmap["experience"].max_points,"entries": len(experience),}
    total_points += pts

    education = _as_list(resume.get("education"))
    if education:
        pts = rmap["education"].max_points
    else:
        pts = 0
        reasons.append("missing_education")
        recommendations.append("Include education details (degree, institution, dates, relevant modules).")

    breakdown["education"] = {"points": pts,"max": rmap["education"].max_points,}
    total_points += pts

    projects = _as_list(resume.get("projects"))
    if projects:
        pts = rmap["projects"].max_points
    else:
        pts = 0
        reasons.append("missing_projects")
        recommendations.append("Add 2–3 projects with clear outcomes and a technology stack.")

    breakdown["projects"] = {"points": pts,"max": rmap["projects"].max_points,}
    total_points += pts

    score_pct = int((total_points / max_points) * 100)

    return {"score": max(0,min(100,score_pct)),"breakdown": breakdown,"reasons": reasons,"reasons_human": [REASONS.get(r,r) for r in reasons],"recommendations": recommendations[:5],"rubric_version": "v1_uk",}
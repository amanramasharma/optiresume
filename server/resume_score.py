def score_resume(resume: dict) -> dict:
    score = 0 
    recs = []

    name = (resume.get("name") or "").strip()
    email = (resume.get("email") or "").strip()
    phone = (resume.get("phone") or "").strip()
    summary = (resume.get("summary") or "").strip()
    
    skills = resume.get("skills") or []
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    education = resume.get("education") or []
    experience = resume.get("experience") or []
    projects = resume.get("projects") or []
    certifications = resume.get("certifications") or []

    if isinstance(education, str): education = [education]
    if isinstance(experience, str): experience = [experience]
    if isinstance(projects, str): projects = [projects]
    if isinstance(certifications, str): certifications = [certifications]

    if name: score += 5
    if email: score += 5
    if phone: score += 5

    if summary:
        score += 10
    else:
        recs.append("Add a 2–3 line professional summary tailored to the role you want.")
    
    if isinstance(skills, list) and len(skills) >= 8:
        score += 20
    else:
        if isinstance(skills, list) and len(skills) > 0:
            score += 10
            if len(skills) < 6:
                recs.append("Add more relevant skills (tools, libraries, cloud, and domain skills). Aim for 8–15.")
        else:
            recs.append("Add a dedicated Skills section (8–15 items: Python, SQL, ML, NLP, Docker, AWS, etc.).")
    if isinstance(experience, list) and len(experience)>0:
        score += 25
        has_metrics = any(("%" in str(x) or any(ch.isdigit() for ch in str(x))) for x in experience)
        if not has_metrics:
            recs.append("Add measurable impact in experience (accuracy %, latency, time saved, revenue, scale, users).")
    else:
        recs.append("Add at least 1–2 experience entries (internships, projects, freelance, university work).")

    if isinstance(education, list) and len(education) > 0:
        score += 15
    else:
        recs.append("Add your education details (degree, university, year).")

    if isinstance(projects, list) and len(projects) > 0:
        score += 10
    else:
        recs.append("Add 2–3 projects with tech stack + outcomes. Link GitHub if available.")

    if isinstance(certifications, list) and len(certifications) > 0:
        score += 5

    score = max(0, min(100, score))
    recs = recs[:3]

    return {"score": score, "recommendations": recs}
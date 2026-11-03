"""
Resume text extract + offline skill summary — NO Gemini API.
"""
import re


def extract_text_from_pdf_stream(file_stream) -> str:
    """Extract raw text from an uploaded file stream (BytesIO or file-like object)."""
    from pypdf import PdfReader

    reader = PdfReader(file_stream)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


_SKILL_KEYWORDS = [
    "figma", "adobe", "xd", "sketch", "ui", "ux", "design", "prototype",
    "html", "css", "javascript", "typescript", "react", "next", "vue", "angular",
    "node", "python", "django", "flask", "fastapi", "java", "spring",
    "sql", "mysql", "postgres", "mongodb", "aws", "azure", "gcp", "docker",
    "git", "github", "seo", "wordpress", "tailwind", "bootstrap",
    "machine learning", "ai", "llm", "android", "ios", "flutter", "kotlin",
    "swift", "c++", "golang", "rust", "php", "laravel",
]


def analyze_resume_profile(resume_text: str, api_key: str = None) -> dict:
    """
    Offline analysis: pick skills by keyword scan + short plain summary.
    api_key ignored (kept for call-site compatibility).
    """
    text = (resume_text or "").strip()
    low = text.lower()

    found = []
    for kw in _SKILL_KEYWORDS:
        if kw in low and kw.title() not in found and kw.upper() not in found:
            # Prefer original casing snippet if present
            found.append(kw if len(kw) > 3 else kw.upper())
    # unique preserve order
    seen = set()
    skills = []
    for s in found:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            skills.append(s)
    skills = skills[:18]

    # First non-empty lines as bio hint
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    head = " ".join(lines[:4])[:280] if lines else "General tech profile"

    skills_line = ", ".join(skills) if skills else "general product / web skills"
    analysis = (
        f"### Summary of Strengths:\n"
        f"- {head}\n\n"
        f"### Top Technical Skills:\n"
        f"- {skills_line}\n\n"
        f"### Suggested LinkedIn Content Pillars / Topics:\n"
        f"- UI tips (buttons, spacing, dashboards)\n"
        f"- Website speed, SEO, and simple layout\n"
        f"- Simple AI / tech notes in plain English\n"
    )

    return {
        "raw_text": text[:1000],
        "analysis": analysis,
        "skills": skills,
    }

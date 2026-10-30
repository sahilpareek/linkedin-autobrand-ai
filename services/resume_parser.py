import io
import os
from pypdf import PdfReader
from google import genai
from google.genai import types

def extract_text_from_pdf_stream(file_stream) -> str:
    """Extract raw text from an uploaded file stream (BytesIO or file-like object)."""
    reader = PdfReader(file_stream)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

def analyze_resume_profile(resume_text: str, api_key: str = None) -> dict:
    """
    Analyzes resume text using Gemini to extract key skills,
    domain, and content creation ideas.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key missing! Please set GEMINI_API_KEY.")

    client = genai.Client(api_key=key)

    prompt = f"""
You are an expert tech recruiter and personal branding coach.
Analyze the following resume and return a structured summary formatted in clean markdown:

### Summary of Strengths:
- Brief 2-3 line summary of candidate's domain and experience level.

### Top Technical Skills:
- List of main skills, tools, languages, frameworks.

### Suggested LinkedIn Content Pillars / Topics:
- 5-8 specific topics, technical concepts, or problem-solving areas from their experience that would make high-engagement LinkedIn posts.

Resume Text:
\"\"\"
{resume_text}
\"\"\"
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {
        "raw_text": resume_text[:1000],  # preview
        "analysis": response.text.strip()
    }

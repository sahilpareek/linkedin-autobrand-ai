import os
from google import genai

POST_STYLES = [
    "Practical Tech Tip / How-To (Direct actionable knowledge)",
    "Common Mistake vs Best Practice (Before & After)",
    "Project Architecture / Lessons Learned Breakdown",
    "Quick Code Snippet & Explanation",
    "Opinion / Industry Trend & Discussion Starter"
]

def generate_post(profile_analysis: str, 
                  topic_focus: str = None, 
                  style: str = None, 
                  include_code: bool = False, 
                  api_key: str = None) -> str:
    """Generates an engaging, high-performing LinkedIn post."""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key missing! Please set GEMINI_API_KEY.")

    client = genai.Client(api_key=key)

    code_instruction = (
        "Include a clean, concise, syntax-formatted code snippet illustrating the concept." 
        if include_code else "Focus on conceptual clarity and real-world intuition."
    )

    topic_instruction = f"Specific Focus Area: {topic_focus}" if topic_focus else "Pick one strong technical skill or topic from the profile."
    selected_style = style or "Practical Tech Tip / How-To"

    prompt = f"""
You are an elite LinkedIn content creator specializing in developer & tech personal branding.
Generate a high-converting, professional, and authentic LinkedIn post based on this candidate profile:

Candidate Profile & Skills:
\"\"\"
{profile_analysis}
\"\"\"

Style Requirement: {selected_style}
{topic_instruction}
Code Snippet: {code_instruction}

Format Rules:
1. First 2 lines MUST be a catchy 'hook' that stops the scroll (no greetings like 'Hello Connections').
2. Short sentences, 1-2 lines per paragraph. Generous whitespace for mobile readability.
3. Use bullet points or numbered steps where explaining steps.
4. Conclude with an engaging question to spark meaningful comments in the comment section.
5. Add 3-5 relevant and trending hashtags at the very end.
6. Only output the actual post content. Do not include markdown code block backticks around the entire post.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()


def refine_post(current_post: str, user_feedback: str, api_key: str = None) -> str:
    """
    Refines and edits the existing post based on user instructions
    (e.g., 'make it shorter', 'add a python snippet', 'make tone more casual', etc.).
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key missing! Please set GEMINI_API_KEY.")

    client = genai.Client(api_key=key)

    prompt = f"""
You are an expert editor for LinkedIn posts.
Here is the current draft of the post:

--- CURRENT POST ---
{current_post}
--- END OF CURRENT POST ---

The user requested the following modifications/corrections:
\"{user_feedback}\"

Apply these modifications carefully while preserving formatting, high readability, and relevant hashtags.
Return ONLY the revised post text directly.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()

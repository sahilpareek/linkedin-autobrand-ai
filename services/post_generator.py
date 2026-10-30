import os
import random
from google import genai

# Common system instruction for viral LinkedIn reach in simple English
BASE_VIRAL_INSTRUCTION = """
Language & Tone Rules:
1. Use VERY SIMPLE, PLAIN, AND CASUAL ENGLISH (Grade 6 level).
2. DO NOT use heavy, complicated dictionary words (e.g., avoid words like 'paradigm', 'plethora', 'delve', 'myriad', 'leverage'). Use everyday friendly words that anyone can read in 30 seconds.
3. Structure:
   - Line 1-2: A super catchy, scroll-stopping hook (make people want to click '...see more').
   - Body: Short 1-2 line paragraphs with lots of clean spacing and emoji bullet points.
   - Actionable Value: Real, clear, and practical insight.
   - Call to Action (CTA): An easy question at the end to get people commenting.
   - Mentions / Communities: Recommend 2-3 relevant topic tags/communities.
   - Hashtags: EXACTLY 10 to 15 relevant, high-reach hashtags at the very bottom.
"""

def get_client(api_key: str = None):
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("Gemini API Key missing! Please set GEMINI_API_KEY.")
    return genai.Client(api_key=key)


def generate_morning_ui_post(profile_context: str = "", custom_topic: str = None, api_key: str = None) -> dict:
    """
    Morning Post (08:30 - 09:30 AM):
    UI/UX & Design Short Tricks (Figma, Adobe XD, Mobile button sizes, 8pt grid, contrast, micro-interactions).
    Inspired by top Behance/Dribbble/Pinterest design principles, but 100% original.
    """
    client = get_client(api_key)
    
    topics = [
        "Mobile Button Sizes: Why 48x48px touch target saves your conversion rate",
        "The 8pt Grid System: How to stop guessing margins and padding in Figma",
        "Color Contrast Rule (60-30-10): Making your app look clean and balanced",
        "Typography Hierarchy: The 3 font sizes that work for 90% of mobile screens",
        "Figma Auto Layout Secret: Building responsive cards in 30 seconds",
        "Card Shadows that look premium instead of dirty (Blur vs Spread trick)",
        "Form UX: Why floating labels hurt UX and what to use instead",
        "Bottom Sheet vs Full Screen Modal: When to use which in mobile apps"
    ]
    chosen_topic = custom_topic if custom_topic else random.choice(topics)

    prompt = f"""
{BASE_VIRAL_INSTRUCTION}

Role: Top UI/UX Design Coach.
Topic: {chosen_topic}

Goal:
Write a viral morning LinkedIn post sharing an actionable UI/UX design short trick (Figma, XD, or mobile app design rules).
Draw inspiration from clean, modern trends on Behance, Dribbble, and Pinterest, but ensure the advice is 100% original, practical, and actionable.

Format:
- Hook that addresses a common design mistake.
- The Quick Fix / Rule (e.g. exact px values, ratio, or Figma shortcut).
- Why it matters for user experience.
- Question for designers (e.g. "Do you use 8pt grid or 4pt grid in your team?").
- Visual Suggestion: Add a small line: "[🖼️ Visual Tip: Side-by-side Bad vs Good UI comparison or Figma canvas screenshot]"
- End with 10 to 15 targeted hashtags (like #UIUX #Figma #UIDesign #ProductDesign #DesignTips #MobileUI #UXProcess #FigmaCommunity #WebDesign #InteractionDesign #UserExperience #DesignSystem #FrontendDesign #TechDesign #CleanUI).

Candidate Context (if any):
{profile_context[:500]}
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return {
        "slot": "Morning (UI/UX Short Trick)",
        "topic": chosen_topic,
        "content": response.text.strip(),
        "visual_idea": "Side-by-side comparison: Bad UX (small touch target) vs Good UX (48px clean button)."
    }


def generate_afternoon_frontend_post(profile_context: str = "", custom_topic: str = None, api_key: str = None) -> dict:
    """
    Afternoon Post (01:00 - 02:00 PM):
    Frontend Development Short Tricks (CSS magic, JavaScript hacks, React hooks tips, web performance).
    """
    client = get_client(api_key)

    topics = [
        "CSS `clamp()`: Stop writing 5 media queries for responsive font sizes",
        "JavaScript `Array.at(-1)` vs `arr[arr.length - 1]`: Clean modern syntax",
        "CSS Glassmorphism in 3 lines: `backdrop-filter: blur(10px)` done right",
        "React `useCallback` trap: When you are actually slowing down your app",
        "CSS `:has()` selector: How to style a parent element based on its child",
        "JavaScript `structuredClone()`: The native way to deep copy objects",
        "Flexbox `gap` property vs margin hacks: Keep layout code 50% cleaner",
        "Web Vitals (LCP/CLS): 1 tiny image optimization trick that cuts load time in half"
    ]
    chosen_topic = custom_topic if custom_topic else random.choice(topics)

    prompt = f"""
{BASE_VIRAL_INSTRUCTION}

Role: Friendly Senior Frontend Developer.
Topic: {chosen_topic}

Goal:
Write a high-traffic afternoon LinkedIn post sharing a super useful frontend shortcut or code trick (CSS, JS, React, Web).
Keep code examples short (3-6 lines maximum) so it looks clean on mobile screens.

Format:
- Hook: A painful old way vs the modern 1-line solution.
- Short Code snippet (Clean and readable).
- Quick explanation in simple terms (explain like you are talking to a friend).
- Interactive question for developers (e.g., "Are you already using this in production?").
- Visual Suggestion: "[💻 Visual Tip: Clean carbon-style code snippet card or browser preview]"
- End with 10 to 15 top frontend hashtags (like #Frontend #WebDevelopment #JavaScript #CSS #ReactJS #CodingTips #100DaysOfCode #WebDesign #ProgrammerLife #DevCommunity #SoftwareEngineering #CodeNewbie #WebDev #UIEngineering #TechCommunity).

Candidate Skills Context:
{profile_context[:500]}
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return {
        "slot": "Afternoon (Frontend Short Trick)",
        "topic": chosen_topic,
        "content": response.text.strip(),
        "visual_idea": "Syntax-highlighted code snippet showing the Before vs After solution."
    }


def generate_evening_ai_post(profile_context: str = "", custom_topic: str = None, api_key: str = None) -> dict:
    """
    Evening Major Post (06:30 - 07:30 PM):
    Trending AI News, new model updates, AI tools, or practical workflows.
    High viral potential.
    """
    client = get_client(api_key)

    topics = [
        "Open-source AI models matching proprietary LLMs: What it means for builders",
        "AI Agents in 2026: Moving from chat boxes to autonomous background workers",
        "Small Language Models (SLMs) running locally on phones and laptops",
        "AI Developer Tools: How AI coding assistants changed pair-programming",
        "Multimodal AI breakthroughs: Real-time voice, vision, and action execution",
        "Top 3 free AI tools that will save you 5 hours every single week"
    ]
    chosen_topic = custom_topic if custom_topic else random.choice(topics)

    prompt = f"""
{BASE_VIRAL_INSTRUCTION}

Role: Tech & AI Trend Analyst who explains complex tech simply.
Topic: {chosen_topic}

Goal:
Write a major evening LinkedIn post breaking down a trending AI topic or news development.
Make it super easy to understand for everyone — no heavy mathematical jargon. Focus on practical real-world impact.

Format:
- Scroll-stopping hook about the latest AI trend or shift.
- What happened (in 2-3 super simple bullet points).
- Why this matters to normal developers, designers, and professionals.
- Actionable takeaway or how to try it.
- Engaging debate question (e.g., "Will local AI models replace cloud APIs? Drop your thoughts below!").
- Visual Suggestion: "[🤖 Visual Tip: Modern AI workflow infographic, diagram, or tool screenshot]"
- End with 10 to 15 high-volume AI hashtags (like #ArtificialIntelligence #GenerativeAI #AITools #TechNews #MachineLearning #Innovation #FutureOfWork #AICommunity #DeepLearning #TechTrends #OpenAI #LLM #Automation #SoftwareDevelopment #EmergingTech).
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return {
        "slot": "Evening (Trending AI News & Breakdown)",
        "topic": chosen_topic,
        "content": response.text.strip(),
        "visual_idea": "Clean infographic or banner highlighting the key AI breakthrough."
    }


def generate_weekend_interactive_post(interactive_type: str = "poll", api_key: str = None) -> dict:
    """
    Weekend Special (Saturday / Sunday):
    Interactive Polls, Quiz, or 'Which UI is better: A vs B?'
    These generate massive comments and reach on weekends!
    """
    client = get_client(api_key)

    prompt = f"""
{BASE_VIRAL_INSTRUCTION}

Goal:
Create an interactive weekend LinkedIn post designed for MAXIMUM COMMENTS and ENGAGEMENT.
Type: {interactive_type.upper()} (e.g., Quiz question with 4 options, OR 'Design A vs Design B' challenge, OR 'Guess the JavaScript output').

Rules:
1. Make the question fun, quick, and relatable to designers & developers.
2. Provide 4 clear options (A, B, C, D) with emojis.
3. Encourage everyone to comment their choice and explain why.
4. Keep the explanation hidden or reveal it in the comments.
5. End with 10 to 15 relevant weekend tech hashtags (#LinkedInPoll #TechQuiz #CodingChallenge #UIUXPoll #DeveloperHumor #WebDev #DesignChallenge #TechCommunity #WeekendTech #LearnInPublic #Programming #CodeQuiz #DesignDiscussion #CareerInTech #SoftwareEngineering).
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return {
        "slot": f"Weekend Special ({interactive_type.title()})",
        "topic": f"Weekend Interactive {interactive_type.title()}",
        "content": response.text.strip(),
        "visual_idea": "Poll graphic with Option A and Option B clearly marked for quick voting."
    }


def refine_post(current_post: str, user_feedback: str, api_key: str = None) -> str:
    """Refines and modifies the existing post based on user instructions."""
    client = get_client(api_key)

    prompt = f"""
You are an expert LinkedIn editor.
Here is the current draft of the post:

--- CURRENT POST ---
{current_post}
--- END CURRENT POST ---

The user wants the following specific changes:
"{user_feedback}"

Rules:
1. Apply the user's modifications accurately.
2. Keep the English very simple, clean, and conversational.
3. Preserve the 10 to 15 relevant hashtags and engaging call-to-action.
4. Directly return only the updated post content.
"""
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text.strip()

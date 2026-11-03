"""
Template-based post generator — NO Gemini / external AI API.
Class-6 English, tags, hashtags, resume skills injected from profile text.
"""
import os
import re
import random

UI_TOPICS = [
    ("Mobile button size", "Make buttons at least 48x48 px so thumbs can tap easy."),
    ("Dashboard clutter", "Too many cards confuse people. Keep one clear main action."),
    ("8pt grid in Figma", "Use 8 / 16 / 24 spacing. Stop guessing padding."),
    ("App nav choice", "On small screens, bottom bar beats a hidden hamburger."),
    ("Form labels", "Tiny labels kill signups. Keep labels clear and close to the field."),
    ("Color contrast", "Light grey text on white fails. Check contrast before ship."),
    ("Empty states", "When a dashboard has no data, show a short tip + one button."),
    ("Web spacing", "Clean Dribbble-style spacing: 8pt rhythm on every block."),
    ("Icon + label", "Icon-only buttons get missed. Add a short label."),
    ("Modal vs sheet", "On mobile, bottom sheet is easier than a center modal."),
]

WEB_TOPICS = [
    ("Slow homepage", "If the page loads slow, users leave in about 3 seconds."),
    ("Semantic HTML", "One good tag (main, nav, h1) helps SEO and screen readers."),
    ("Mobile-first layout", "Design the small screen first. Then grow to desktop."),
    ("Accessible links", "Links and buttons need clear text, not only color."),
    ("Clean URLs", "Short, plain URLs help users and search."),
    ("Hero image weight", "A heavy hero image breaks Core Web Vitals. Compress it."),
    ("Simple CSS layout", "Flex or grid with few breakpoints is enough for most sites."),
    ("Contact form UX", "Few fields + clear error text = more form completes."),
    ("Nav labels", "Nav words should match how users search, not fancy jargon."),
    ("Basic site hygiene", "HTTPS, favicon, and a clear title tag still matter."),
]

AI_TOPICS = [
    ("AI coding helpers", "AI coding tools draft code fast. You still check and fix it."),
    ("Local AI on a laptop", "Small models can run offline on a laptop for private work."),
    ("AI agents", "Agents can do background tasks, not only chat answers."),
    ("AI design tools", "New AI design tools sketch screens in minutes. Edit by hand after."),
    ("AI for support", "Teams use AI to sort support tickets and draft first replies."),
    ("Open vs paid models", "Open models cost less to try. Paid APIs are easier to start."),
    ("AI workflow tip", "One small AI step in your daily work can save real time."),
    ("Tech beyond AI", "Other trends matter too: web speed, privacy, and clean UX."),
]

WEEKEND_POLLS = [
    ("Which UI habit helps you most?", ["A) 48px buttons", "B) 8pt grid", "C) Clear labels", "D) Less dashboard cards"]),
    ("What should a homepage do first?", ["A) Load fast", "B) Look fancy", "C) Show many menus", "D) Auto-play video"]),
    ("Best weekend learning pick?", ["A) One UI tip", "B) One web tip", "C) One AI tool try", "D) Rest and review"]),
]

WEEKEND_QUIZ = [
    ("Safe mobile tap size is about…", ["A) 24px", "B) 32px", "C) 48px", "D) 8px"], "C"),
    ("For SEO, a clear page title is…", ["A) Optional", "B) Important", "C) Only for blogs", "D) Bad for UX"], "B"),
]

PAGE_TAGS = {
    "morning": "@Figma @Dribbble @Behance @NNGroup @GoogleDesign @IxDF",
    "afternoon": "@GitHub @MDNWebDocs @CSSTricks @webdev @Vercel @GoogleChrome",
    "evening": "@OpenAI @GoogleDeepMind @HuggingFace @NVIDIA @TechCrunch @Wired",
    "weekend": "@LinkedIn @Figma @GitHub @ProductHunt @Dribbble",
}

HASHTAGS = {
    "morning": "#UIUX #UIDesign #UXDesign #ProductDesign #Figma #MobileUI #DashboardDesign #WebDesign #DesignTips #UX #DesignSystem #AppDesign #Dribbble #Pinterest #CleanUI",
    "afternoon": "#WebDesign #Website #WebDevelopment #Frontend #HTML #CSS #JavaScript #UX #SEO #WebPerf #Accessibility #CodingTips #100DaysOfCode #DevCommunity #BuildInPublic",
    "evening": "#AI #ArtificialIntelligence #TechNews #GenerativeAI #MachineLearning #FutureOfWork #AITools #Innovation #LLM #TechTrends #Startups #Automation #DeepLearning #OpenSource #Trending",
    "weekend": "#LinkedInPoll #TechQuiz #UIUXPoll #WebDev #DesignChallenge #LearnInPublic #CareerInTech #WeekendVibes #ProductDesign #CodingChallenge #AI #Developer #QuizTime #BuildInPublic #Community",
}


def _pick_skills(profile_context: str) -> str:
    text = (profile_context or "").strip()
    if not text:
        return "design and web work"
    # Prefer a short skills-looking line
    for line in text.splitlines():
        low = line.lower()
        if any(k in low for k in ("skill", "figma", "react", "html", "css", "ui", "ux", "python", "javascript")):
            clean = re.sub(r"^[#*\-\s]+", "", line).strip()
            if 8 < len(clean) < 120:
                return clean
    # Fallback: first non-empty short chunk
    chunk = re.sub(r"\s+", " ", text)[:90].strip()
    return chunk or "design and web work"


def _pick_name(profile_context: str) -> str:
    for line in (profile_context or "").splitlines():
        if line.lower().startswith("name:"):
            return line.split(":", 1)[1].strip() or "there"
    return "there"


def _body(slot: str, topic: str, tip: str, skills: str, name: str) -> str:
    hooks = {
        "morning": f"Tiny UI tip that saves real users 👇",
        "afternoon": f"Simple website tip (no heavy words) 👇",
        "evening": f"Quick tech note in plain English 👇",
    }
    hook = hooks.get(slot, "Quick tip 👇")
    cta = {
        "morning": "Which UI fix will you try this week?",
        "afternoon": "What is one thing you will improve on your site?",
        "evening": "Are you trying any new AI tool right now?",
    }.get(slot, "What do you think?")

    return (
        f"{hook}\n\n"
        f"{topic}\n\n"
        f"{tip}\n\n"
        f"I keep this in mind in my work with: {skills}.\n\n"
        f"Banner idea: good vs bad example (clean Pinterest / Dribbble style).\n\n"
        f"{cta}\n\n"
        f"Pages: {PAGE_TAGS[slot]}\n\n"
        f"{HASHTAGS[slot]}"
    )


def generate_morning_ui_post(profile_context: str = "", custom_topic: str = None, api_key: str = None) -> dict:
    topic, tip = random.choice(UI_TOPICS)
    if custom_topic:
        topic = custom_topic
        tip = "Keep the rule simple and test it on a real screen today."
    skills = _pick_skills(profile_context)
    name = _pick_name(profile_context)
    content = _body("morning", topic, tip, skills, name)
    return {
        "slot": "Morning (UI/UX Design)",
        "slot_key": "morning",
        "topic": topic,
        "content": content,
        "visual_idea": "Pinterest/Dribbble style banner: Bad tiny button vs Good 48px button.",
        "page_tags": PAGE_TAGS["morning"],
        "hashtags": HASHTAGS["morning"],
    }


def generate_afternoon_frontend_post(profile_context: str = "", custom_topic: str = None, api_key: str = None) -> dict:
    topic, tip = random.choice(WEB_TOPICS)
    if custom_topic:
        topic = custom_topic
        tip = "Ship one small fix on a real page this week."
    skills = _pick_skills(profile_context)
    name = _pick_name(profile_context)
    content = _body("afternoon", topic, tip, skills, name)
    return {
        "slot": "Afternoon (Website / Web)",
        "slot_key": "afternoon",
        "topic": topic,
        "content": content,
        "visual_idea": "Website wireframe: messy homepage vs clean homepage.",
        "page_tags": PAGE_TAGS["afternoon"],
        "hashtags": HASHTAGS["afternoon"],
    }


def generate_evening_ai_post(profile_context: str = "", custom_topic: str = None, api_key: str = None) -> dict:
    topic, tip = random.choice(AI_TOPICS)
    if custom_topic:
        topic = custom_topic
        tip = "Try one small step. Keep the language simple."
    skills = _pick_skills(profile_context)
    name = _pick_name(profile_context)
    content = _body("evening", topic, tip, skills, name)
    return {
        "slot": "Evening (AI / Trending Tech)",
        "slot_key": "evening",
        "topic": topic,
        "content": content,
        "visual_idea": "Simple AI news banner: one headline + three bullets.",
        "page_tags": PAGE_TAGS["evening"],
        "hashtags": HASHTAGS["evening"],
    }


def generate_weekend_interactive_post(interactive_type: str = "poll", profile_context: str = "", api_key: str = None) -> dict:
    kind = (interactive_type or "poll").lower()
    if kind not in ("poll", "quiz", "ab"):
        kind = random.choice(["poll", "quiz"])
    skills = _pick_skills(profile_context)

    if kind == "quiz":
        q, opts, ans = random.choice(WEEKEND_QUIZ)
        options = "\n".join(opts)
        content = (
            f"Weekend quiz (answer in comments) 🧠\n\n"
            f"{q}\n\n{options}\n\n"
            f"Hint later. Reply with A B C or D.\n\n"
            f"My work area: {skills}\n\n"
            f"Pages: {PAGE_TAGS['weekend']}\n\n"
            f"{HASHTAGS['weekend']}"
        )
        topic = f"Quiz: {q}"
    else:
        q, opts = random.choice(WEEKEND_POLLS)
        options = "\n".join(opts)
        content = (
            f"Weekend poll — pick one 👇\n\n"
            f"{q}\n\n{options}\n\n"
            f"Comment your letter. I will share what I use in: {skills}.\n\n"
            f"Pages: {PAGE_TAGS['weekend']}\n\n"
            f"{HASHTAGS['weekend']}"
        )
        topic = f"Poll: {q}"

    return {
        "slot": f"Weekend ({kind.title()})",
        "slot_key": "weekend",
        "topic": topic,
        "content": content,
        "visual_idea": "Big A vs B or quiz card for comments.",
        "page_tags": PAGE_TAGS["weekend"],
        "hashtags": HASHTAGS["weekend"],
    }


def refine_post(current_post: str, user_feedback: str, api_key: str = None) -> str:
    """No AI: apply simple text replace / append instructions."""
    post = (current_post or "").strip()
    fb = (user_feedback or "").strip()
    if not fb:
        return post

    low = fb.lower()
    # "remove hashtags" etc.
    if "remove hashtag" in low or "no hashtag" in low:
        post = re.sub(r"(?m)^#\S+(?:\s+#\S+)*\s*$", "", post).strip()
        return post + "\n\n(updated: hashtags removed)"

    if low.startswith("add "):
        return post + "\n\n" + fb[4:].strip()

    if low.startswith("replace ") and " with " in low:
        try:
            rest = fb[8:]
            old, new = rest.split(" with ", 1)
            return post.replace(old.strip(), new.strip())
        except Exception:
            pass

    # Default: append user note as an edit line
    return (
        post
        + "\n\n---\nEdit note from you:\n"
        + fb
        + "\n---"
    )

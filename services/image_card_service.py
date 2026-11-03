import os
from typing import List

THEMES = {
    "ui_ux": {"bg": (30, 27, 75), "accent": (129, 140, 248), "badge": "UI / UX DESIGN"},
    "morning": {"bg": (30, 27, 75), "accent": (129, 140, 248), "badge": "UI / UX DESIGN"},
    "frontend": {"bg": (15, 23, 42), "accent": (56, 189, 248), "badge": "WEBSITE TIP"},
    "afternoon": {"bg": (15, 23, 42), "accent": (56, 189, 248), "badge": "WEBSITE TIP"},
    "ai_news": {"bg": (24, 24, 27), "accent": (192, 132, 252), "badge": "AI + TECH NEWS"},
    "evening": {"bg": (24, 24, 27), "accent": (192, 132, 252), "badge": "AI + TECH NEWS"},
    "weekend": {"bg": (28, 25, 23), "accent": (251, 146, 60), "badge": "WEEKEND POLL"},
}


def _wrap(text: str, width: int) -> List[str]:
    words = (text or "").split()
    lines, current = [], []
    for w in words:
        current.append(w)
        if len(" ".join(current)) > width:
            lines.append(" ".join(current[:-1]) or w)
            current = [w] if len(" ".join(current)) > width else []
            if current == [w] and len(w) > width:
                current = []
                lines.append(w)
    if current:
        lines.append(" ".join(current))
    return lines[:5] or ["Design tip"]


def generate_svg_banner(title: str, category: str, bullet_points: list = None, author: str = "@AutoBrand") -> str:
    bullets = bullet_points or ["Simple rule you can use today", "Save this post", "Share with your team"]
    key = (category or "morning").lower()
    theme = THEMES.get(key, THEMES["morning"])
    lines = _wrap(title, 24)
    title_svg = ""
    for i, line in enumerate(lines):
        safe = (
            line.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        title_svg += f'<text x="100" y="{360 + i * 64}" fill="#ffffff" font-size="48" font-weight="800" font-family="system-ui, sans-serif">{safe}</text>\n'
    bullets_svg = ""
    for j, b in enumerate(bullets[:3]):
        safe_b = b.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        bullets_svg += f'<text x="100" y="{720 + j * 50}" fill="#e2e8f0" font-size="26" font-family="system-ui, sans-serif">• {safe_b}</text>\n'
    accent = "#818cf8"
    return f"""<svg width="1080" height="1080" viewBox="0 0 1080 1080" xmlns="http://www.w3.org/2000/svg">
    <rect width="1080" height="1080" fill="rgb{theme['bg']}"/>
    <rect x="60" y="60" width="960" height="960" rx="40" fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.12)"/>
    <text x="100" y="180" fill="{accent}" font-size="22" font-weight="800" font-family="system-ui, sans-serif">{theme['badge']}</text>
    {title_svg}
    {bullets_svg}
    <text x="100" y="980" fill="#94a3b8" font-size="22" font-family="system-ui, sans-serif">{author}</text>
</svg>"""


def generate_png_banner(
    title: str,
    category: str,
    bullet_points: list = None,
    author: str = "@AutoBrand",
    filepath: str = "banner.png",
) -> str:
    from PIL import Image, ImageDraw, ImageFont

    bullets = bullet_points or ["Simple rule you can use today", "Save this post", "Share with your team"]
    key = (category or "morning").lower()
    theme = THEMES.get(key, THEMES["morning"])
    img = Image.new("RGB", (1080, 1080), theme["bg"])
    draw = ImageDraw.Draw(img)
    try:
        font_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_md = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except Exception:
        font_lg = font_md = font_sm = ImageFont.load_default()

    draw.rounded_rectangle((60, 60, 1020, 1020), radius=40, outline=(200, 200, 220), width=3)
    draw.text((100, 140), theme["badge"], fill=theme["accent"], font=font_sm)
    y = 280
    for line in _wrap(title, 22):
        draw.text((100, y), line, fill=(255, 255, 255), font=font_lg)
        y += 70
    y += 40
    for b in bullets[:3]:
        draw.text((100, y), "• " + b[:48], fill=(226, 232, 240), font=font_md)
        y += 56
    draw.text((100, 960), author[:40], fill=(148, 163, 184), font=font_sm)
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    img.save(filepath, "PNG")
    return filepath


def save_svg_to_file(svg_string: str, filepath: str = "banner.svg"):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_string)
    return filepath

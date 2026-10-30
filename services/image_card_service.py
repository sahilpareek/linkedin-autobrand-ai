import os
import io

def generate_svg_banner(title: str, category: str, bullet_points: list = None, author: str = "@DesignAndTech") -> str:
    """
    Generates a modern, high-res SVG graphic banner (1080x1080) for LinkedIn.
    Uses modern design aesthetics inspired by Dribbble/Behance:
    - Vibrant mesh/radial dark gradients
    - Clean typography hierarchy
    - Glassmorphism accent badge
    """
    bullets = bullet_points or [
        "100% Practical & Actionable Tip",
        "Save this post for quick reference",
        "Share with a designer or dev friend"
    ]
    
    # Category color schemes
    themes = {
        "ui_ux": {"grad1": "#1e1b4b", "grad2": "#4338ca", "accent": "#818cf8", "badge": "🎨 UI/UX DESIGN TIP"},
        "frontend": {"grad1": "#0f172a", "grad2": "#0284c7", "accent": "#38bdf8", "badge": "💻 FRONTEND SHORT TRICK"},
        "ai_news": {"grad1": "#18181b", "grad2": "#9333ea", "accent": "#c084fc", "badge": "🤖 TRENDING AI NEWS"},
        "weekend": {"grad1": "#1c1917", "grad2": "#ea580c", "accent": "#fb923c", "badge": "⚡ WEEKEND CHALLENGE"}
    }
    
    theme = themes.get(category.lower(), themes["ui_ux"])

    # Format title into lines
    words = title.split()
    lines = []
    current_line = []
    for w in words:
        current_line.append(w)
        if len(" ".join(current_line)) > 24:
            lines.append(" ".join(current_line))
            current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    lines = lines[:4] # max 4 lines

    title_svg = ""
    start_y = 380
    for i, line in enumerate(lines):
        title_svg += f'<text x="100" y="{start_y + (i * 68)}" fill="#ffffff" font-size="52" font-weight="800" font-family="system-ui, -apple-system, sans-serif">{line}</text>\n'

    bullets_svg = ""
    bullet_start_y = start_y + (len(lines) * 68) + 60
    for j, b in enumerate(bullets[:3]):
        bullets_svg += f'''
        <g transform="translate(100, {bullet_start_y + (j * 75)})">
            <circle cx="20" cy="0" r="14" fill="{theme['accent']}" opacity="0.25"/>
            <circle cx="20" cy="0" r="6" fill="{theme['accent']}"/>
            <text x="56" y="8" fill="#e2e8f0" font-size="30" font-weight="500" font-family="system-ui, -apple-system, sans-serif">{b}</text>
        </g>
        '''

    svg_content = f"""<svg width="1080" height="1080" viewBox="0 0 1080 1080" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <radialGradient id="bgGrad" cx="30%" cy="20%" r="80%">
            <stop offset="0%" stop-color="{theme['grad2']}"/>
            <stop offset="100%" stop-color="{theme['grad1']}"/>
        </radialGradient>
        <filter id="cardGlow" x="-10%" y="-10%" width="120%" height="120%">
            <feDropShadow dx="0" dy="24" stdDeviation="32" flood-color="#000000" flood-opacity="0.45"/>
        </filter>
    </defs>

    <!-- Background -->
    <rect width="1080" height="1080" fill="url(#bgGrad)"/>

    <!-- Decorative Glow Circles -->
    <circle cx="920" cy="180" r="260" fill="{theme['accent']}" opacity="0.12" filter="blur(80px)"/>
    <circle cx="160" cy="900" r="300" fill="{theme['grad2']}" opacity="0.2" filter="blur(90px)"/>

    <!-- Glassmorphic Card Container -->
    <rect x="60" y="60" width="960" height="960" rx="40" fill="rgba(255, 255, 255, 0.04)" stroke="rgba(255, 255, 255, 0.12)" stroke-width="2" filter="url(#cardGlow)"/>

    <!-- Category Pill Badge -->
    <g transform="translate(100, 160)">
        <rect width="360" height="54" rx="27" fill="{theme['accent']}" opacity="0.2"/>
        <text x="180" y="34" fill="{theme['accent']}" font-size="20" font-weight="800" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" letter-spacing="1.5">{theme['badge']}</text>
    </g>

    <!-- Title Lines -->
    {title_svg}

    <!-- Bullets -->
    {bullets_svg}

    <!-- Footer Branding -->
    <line x1="100" y1="940" x2="980" y2="940" stroke="rgba(255, 255, 255, 0.1)" stroke-width="1.5"/>
    <text x="100" y="990" fill="#94a3b8" font-size="24" font-weight="600" font-family="system-ui, -apple-system, sans-serif">{author}</text>
    <text x="980" y="990" fill="{theme['accent']}" font-size="22" font-weight="700" text-anchor="end" font-family="system-ui, -apple-system, sans-serif">Swipe for details 👉</text>
</svg>"""
    return svg_content


def save_svg_to_file(svg_string: str, filepath: str = "banner.svg"):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_string)
    return filepath

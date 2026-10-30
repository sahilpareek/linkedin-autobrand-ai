"""
CLI Auto Runner for GitHub Actions / Cron Scheduling.
Supports 3 daily traffic peak slots + weekend interactive posts:
  - morning: UI/UX & Design Short Tricks (09:00 AM IST)
  - afternoon: Frontend Code Hacks (01:00 PM IST)
  - evening: Trending AI News & Breakdown (07:00 PM IST)
  - weekend: Interactive Poll / Quiz / A vs B (Saturday/Sunday)
"""

import argparse
import datetime
import os
import sys
from dotenv import load_dotenv

from services.storage_service import load_profile, add_post_to_history
from services.post_generator import (
    generate_morning_ui_post,
    generate_afternoon_frontend_post,
    generate_evening_ai_post,
    generate_weekend_interactive_post
)
from services.image_card_service import generate_svg_banner, save_svg_to_file
from services.linkedin_service import publish_linkedin_post
from services.whatsapp_service import send_whatsapp_preview

load_dotenv()

def detect_auto_slot():
    """Detects best slot based on current Indian Standard Time (IST) or day."""
    # Convert UTC to IST (+5:30)
    now_ist = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)
    weekday = now_ist.weekday() # 5 = Saturday, 6 = Sunday
    hour = now_ist.hour

    if weekday in (5, 6):
        return "weekend"
    elif hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    else:
        return "evening"

def run_slot(slot_name: str, mode: str = "preview"):
    profile = load_profile()
    profile_text = profile.get("analysis", "") if profile else ""

    print(f"🎯 Target Slot: {slot_name.upper()} | Mode: {mode.upper()}")

    if slot_name == "morning":
        result = generate_morning_ui_post(profile_text)
        cat_key = "ui_ux"
    elif slot_name == "afternoon":
        result = generate_afternoon_frontend_post(profile_text)
        cat_key = "frontend"
    elif slot_name == "evening":
        result = generate_evening_ai_post(profile_text)
        cat_key = "ai_news"
    elif slot_name == "weekend":
        result = generate_weekend_interactive_post("poll")
        cat_key = "weekend"
    else:
        result = generate_morning_ui_post(profile_text)
        cat_key = "ui_ux"

    post_content = result["content"]
    topic = result["topic"]

    # Generate matching visual graphic banner
    svg_banner = generate_svg_banner(
        title=topic,
        category=cat_key,
        author="@LinkedInCreator"
    )
    save_svg_to_file(svg_banner, "latest_banner.svg")

    print("\n" + "="*50)
    print(f"[{result['slot']}] {topic}")
    print("="*50)
    print(post_content)
    print("="*50 + "\n")

    if mode == "preview":
        print("📱 Sending draft preview to WhatsApp...")
        res = send_whatsapp_preview(post_content)
        if res.get("success"):
            print("✅ WhatsApp preview sent successfully!")
        else:
            print(f"❌ WhatsApp failed: {res.get('error')}")

    elif mode == "post":
        print("🚀 Publishing directly to LinkedIn...")
        res = publish_linkedin_post(post_content)
        if res.get("success"):
            print("✅ Published successfully to LinkedIn!")
            add_post_to_history(post_content, f"PUBLISHED ({slot_name.upper()})", res.get("post_id", ""))
        else:
            print(f"❌ LinkedIn posting failed: {res.get('error')}")

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Bot 3x Daily Auto Runner")
    parser.add_argument("--slot", choices=["auto", "morning", "afternoon", "evening", "weekend"], default="auto",
                        help="Select slot (default auto-detects by time).")
    parser.add_argument("--mode", choices=["preview", "post"], default="preview",
                        help="Choose 'preview' for WhatsApp or 'post' for direct publishing.")
    args = parser.parse_args()

    chosen_slot = detect_auto_slot() if args.slot == "auto" else args.slot
    run_slot(chosen_slot, args.mode)

if __name__ == "__main__":
    main()

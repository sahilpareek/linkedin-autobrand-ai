"""
CLI Auto Runner for GitHub Actions / Cron Scheduling.
Usage:
  python cli_auto_runner.py --mode preview   # Generates & sends to WhatsApp
  python cli_auto_runner.py --mode post      # Directly posts to LinkedIn
"""

import argparse
import os
import sys
from dotenv import load_dotenv

from services.storage_service import load_profile, add_post_to_history
from services.post_generator import generate_post
from services.linkedin_service import publish_linkedin_post
from services.whatsapp_service import send_whatsapp_preview

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Bot Auto Runner")
    parser.add_argument("--mode", choices=["preview", "post"], default="preview",
                        help="Choose 'preview' to send WhatsApp draft or 'post' to publish directly.")
    args = parser.parse_args()

    profile = load_profile()
    if not profile or "analysis" not in profile:
        print("❌ Error: No profile found in data/profile.json. Please upload your resume in the Streamlit UI first.")
        sys.exit(1)

    print("🤖 Generating LinkedIn Post from Profile...")
    post_content = generate_post(profile["analysis"])
    print("\n--- GENERATED POST ---")
    print(post_content)
    print("----------------------\n")

    if args.mode == "preview":
        print("📱 Sending Preview to WhatsApp...")
        res = send_whatsapp_preview(post_content)
        if res.get("success"):
            print("✅ WhatsApp preview sent successfully!")
        else:
            print(f"❌ WhatsApp failed: {res.get('error')}")
    elif args.mode == "post":
        print("🚀 Publishing directly to LinkedIn...")
        res = publish_linkedin_post(post_content)
        if res.get("success"):
            print("✅ Published successfully to LinkedIn!")
            add_post_to_history(post_content, "PUBLISHED", res.get("post_id", ""))
        else:
            print(f"❌ LinkedIn posting failed: {res.get('error')}")

if __name__ == "__main__":
    main()

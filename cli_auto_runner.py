"""CLI dispatcher for cron / GitHub Actions. Always sends Telegram drafts for approval."""

import argparse
import sys
from dotenv import load_dotenv

load_dotenv()

from services.user_manager import get_all_users
from services.schedule_utils import detect_slot
from services.slot_engine import dispatch_slot_for_all_users


def main():
    parser = argparse.ArgumentParser(description="AutoBrand multi-user dispatcher")
    parser.add_argument(
        "--slot",
        choices=["auto", "morning", "afternoon", "evening", "weekend"],
        default="auto",
    )
    parser.add_argument(
        "--mode",
        choices=["preview", "post"],
        default="preview",
        help="Both modes send Telegram drafts. LinkedIn publish happens only after user approval.",
    )
    args = parser.parse_args()

    chosen_slot = detect_slot() if args.slot == "auto" else args.slot
    print(f"Running slot: {chosen_slot} (mode={args.mode}, approval required)")

    users = get_all_users()
    if not users:
        print("No registered users in data/users/. Onboard via the website first.")
        sys.exit(0)

    result = dispatch_slot_for_all_users(chosen_slot)
    print(result)
    print("Drafts sent. Users must Approve on Telegram before LinkedIn publish.")


if __name__ == "__main__":
    main()

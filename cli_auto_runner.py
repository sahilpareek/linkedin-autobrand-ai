"""
CLI Auto Runner for GitHub Actions / Cron Scheduling.
Supports multi-user dispatch:
Loops through all registered users in data/users/ and sends WhatsApp draft previews.
"""

import argparse
import datetime
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from services.user_manager import get_all_users
from server import dispatch_slot_for_all_users

def detect_auto_slot():
    """Detects best slot based on current Indian Standard Time (IST) or day."""
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

def main():
    parser = argparse.ArgumentParser(description="AutoBrand Multi-User Scheduled Dispatcher")
    parser.add_argument("--slot", choices=["auto", "morning", "afternoon", "evening", "weekend"], default="auto",
                        help="Select slot (default auto-detects by time).")
    args = parser.parse_args()

    chosen_slot = detect_auto_slot() if args.slot == "auto" else args.slot
    print(f"🎯 Running Multi-User Auto Dispatch for Slot: {chosen_slot.upper()}")

    users = get_all_users()
    if not users:
        print("ℹ️ No registered users found in data/users/. Onboard via the website first.")
        sys.exit(0)

    dispatch_slot_for_all_users(chosen_slot)
    print("✅ Dispatched successfully to all active users!")

if __name__ == "__main__":
    main()

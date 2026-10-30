import os
from twilio.rest import Client

def get_twilio_client(sid: str = None, token: str = None):
    account_sid = sid or os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = token or os.getenv("TWILIO_AUTH_TOKEN")
    if not account_sid or not auth_token:
        return None
    return Client(account_sid, auth_token)

def format_whatsapp_number(number: str) -> str:
    if not number:
        return ""
    number = number.strip()
    if not number.startswith("whatsapp:"):
        if not number.startswith("+"):
            number = f"+{number}"
        number = f"whatsapp:{number}"
    return number

def send_whatsapp_message(to_number: str, body: str, media_url: str = None) -> dict:
    """Generic WhatsApp sender via Twilio."""
    from_number = format_whatsapp_number(os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886"))
    dest_number = format_whatsapp_number(to_number)

    client = get_twilio_client()
    if not client:
        return {"success": False, "error": "Twilio credentials not configured."}

    try:
        kwargs = {
            "body": body,
            "from_": from_number,
            "to": dest_number
        }
        if media_url:
            kwargs["media_url"] = [media_url]

        msg = client.messages.create(**kwargs)
        return {"success": True, "sid": msg.sid}
    except Exception as e:
        return {"success": False, "error": str(e)}

def notify_admin_new_user(user_data: dict) -> dict:
    """Alerts the admin on WhatsApp whenever someone uploads their resume & registers."""
    admin_phone = os.getenv("ADMIN_WHATSAPP_NUMBER")
    if not admin_phone:
        return {"success": False, "error": "ADMIN_WHATSAPP_NUMBER not set."}

    name = user_data.get("name", "New User")
    phone = user_data.get("phone", "")
    gh = user_data.get("github_username", "None")
    skills = user_data.get("skills_summary", "Extracted from resume")[:250]

    msg = (
        "🎉 *New User Registered on AutoBrand AI!*\n\n"
        f"👤 *Name:* {name}\n"
        f"📱 *WhatsApp:* {phone}\n"
        f"🐙 *GitHub:* @{gh}\n\n"
        f"🎯 *Skills Summary:*\n{skills}\n\n"
        "⚡ Automated daily 3x LinkedIn drafts are now activated for this user."
    )
    return send_whatsapp_message(admin_phone, msg)

def send_user_welcome_message(phone: str, name: str) -> dict:
    """Welcomes user on WhatsApp upon registration."""
    msg = (
        f"👋 *Hi {name}! Welcome to AutoBrand AI.*\n\n"
        "✅ Your resume has been parsed successfully!\n"
        "⏰ You will receive 3 daily high-traffic post drafts on this WhatsApp chat:\n"
        "• 09:00 AM — UI/UX & Design Short Trick\n"
        "• 01:00 PM — Frontend Code Shortcut (with your GitHub link)\n"
        "• 07:00 PM — Trending AI News & Breakdown\n\n"
        "👉 You won't need to open any website. Whenever a draft arrives, simply reply *APPROVE* to post, or reply with your changes to edit it!"
    )
    return send_whatsapp_message(phone, msg)

def send_whatsapp_draft_for_approval(to_number: str, post_content: str, slot_name: str, topic: str) -> dict:
    """Sends draft to user with 1-click text reply approval instructions."""
    msg = (
        f"🚀 *New Draft Ready: {slot_name}*\n"
        f"📌 *Topic:* {topic}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{post_content}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ *What would you like to do?*\n"
        "1️⃣ Reply *APPROVE* or *YES* to publish this directly to your LinkedIn.\n"
        "2️⃣ Reply with your changes (e.g., 'Make it shorter', 'Add Python snippet') to update the draft automatically!"
    )
    return send_whatsapp_message(to_number, msg)

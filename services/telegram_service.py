import os
import urllib.parse
import requests

def get_telegram_config():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    return token, admin_chat_id

def send_telegram_message(text: str, chat_id: str = None, reply_markup: dict = None) -> dict:
    """Sends message to Telegram user or admin."""
    token, default_chat_id = get_telegram_config()
    target_chat_id = chat_id or default_chat_id

    if not token or not target_chat_id:
        return {"success": False, "error": "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing."}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": target_chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        return {"success": data.get("ok", False), "result": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def notify_admin_telegram_new_user(user_data: dict) -> dict:
    """Alerts Sahil on Telegram whenever a user registers on the website."""
    name = user_data.get("name", "New User")
    phone = user_data.get("phone", "N/A")
    gh = user_data.get("github_username", "None")
    linkedin = user_data.get("linkedin_token", "None")
    skills = user_data.get("skills_summary", "Extracted from resume")[:350]

    msg = f"""<b>🎉 New User Registered on AutoBrand AI!</b>

👤 <b>Name:</b> {name}
📱 <b>Phone / Contact:</b> {phone}
🐙 <b>GitHub:</b> <a href="https://github.com/{gh}">@{gh}</a>
💼 <b>LinkedIn:</b> {linkedin}

🎯 <b>Skills Summary:</b>
<code>{skills}</code>

⚡ <i>Automated daily 3x posts are activated for this user.</i>"""

    return send_telegram_message(msg)

def send_post_draft_to_telegram(post_content: str, slot_name: str, topic: str, chat_id: str = None) -> dict:
    """Sends scheduled post draft to Telegram with 1-Tap LinkedIn Post Button."""
    encoded_text = urllib.parse.quote(post_content)
    linkedin_share_url = f"https://www.linkedin.com/feed/?shareActive=true&text={encoded_text}"

    text = f"""<b>🚀 New Post Draft: {slot_name}</b>
📌 <b>Topic:</b> {topic}
━━━━━━━━━━━━━━━━━━━━

{post_content}

━━━━━━━━━━━━━━━━━━━━
👉 <i>Tap the button below to publish on LinkedIn in 1 second!</i>"""

    # Inline interactive buttons
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "📲 1-Tap Post on LinkedIn", "url": linkedin_share_url}
            ]
        ]
    }

    return send_telegram_message(text, chat_id=chat_id, reply_markup=reply_markup)

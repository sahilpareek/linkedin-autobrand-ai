import os
import urllib.parse

APPROVE_KEYBOARD = {
    "inline_keyboard": [
        [
            {"text": "✅ Approve & post on LinkedIn", "callback_data": "approve"},
            {"text": "✏️ I will type changes", "callback_data": "edit_hint"},
        ]
    ]
}


def get_telegram_config():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot_username = (os.getenv("TELEGRAM_BOT_USERNAME") or "").lstrip("@")
    return token, admin_chat_id, bot_username


def bot_start_link(connect_code: str) -> str:
    _, _, bot_username = get_telegram_config()
    if bot_username:
        return f"https://t.me/{bot_username}?start={connect_code}"
    return ""


def _api(method: str, payload: dict = None, files=None) -> dict:
    import requests

    token, _, _ = get_telegram_config()
    if not token:
        return {"success": False, "error": "TELEGRAM_BOT_TOKEN missing."}
    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        if files:
            res = requests.post(url, data=payload or {}, files=files, timeout=30)
        else:
            res = requests.post(url, json=payload or {}, timeout=15)
        data = res.json()
        return {"success": bool(data.get("ok")), "result": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_telegram_message(text: str, chat_id: str = None, reply_markup: dict = None) -> dict:
    token, default_chat_id, _ = get_telegram_config()
    target = str(chat_id or default_chat_id or "")
    if not token or not target:
        return {"success": False, "error": "TELEGRAM_BOT_TOKEN or chat id missing."}
    payload = {
        "chat_id": target,
        "text": text[:3900],
        "disable_web_page_preview": False,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return _api("sendMessage", payload)


def send_telegram_photo(chat_id: str, photo_path: str, caption: str = "", reply_markup: dict = None) -> dict:
    if not photo_path or not os.path.isfile(photo_path):
        return send_telegram_message(caption, chat_id=chat_id, reply_markup=reply_markup)
    payload = {"chat_id": str(chat_id), "caption": (caption or "")[:1000]}
    if reply_markup:
        import json
        payload["reply_markup"] = json.dumps(reply_markup)
    with open(photo_path, "rb") as fh:
        return _api("sendPhoto", payload, files={"photo": fh})


def notify_admin_telegram_new_user(user_data: dict) -> dict:
    _, admin_chat_id, _ = get_telegram_config()
    name = user_data.get("name", "New User")
    tg = user_data.get("telegram_username", "N/A")
    gh = user_data.get("github_username", "None")
    linkedin = user_data.get("linkedin_url") or user_data.get("linkedin_token", "None")
    skills = (user_data.get("skills_summary") or "")[:350]
    msg = (
        f"New user on AutoBrand AI\n\n"
        f"Name: {name}\n"
        f"Telegram: @{tg}\n"
        f"GitHub: https://github.com/{gh}\n"
        f"LinkedIn: {linkedin}\n\n"
        f"Skills:\n{skills}\n\n"
        f"Daily 3 posts will follow this resume."
    )
    return send_telegram_message(msg, chat_id=admin_chat_id)


def send_user_welcome(chat_id: str, name: str) -> dict:
    return send_telegram_message(
        (
            f"Hi {name}! Your AutoBrand agent is on.\n\n"
            "Weekdays: 3 posts (UI design, website, AI/tech news).\n"
            "Sat & Sun: quiz or poll.\n\n"
            "Each draft comes here first.\n"
            "Tap Approve to post on LinkedIn, or type the change you want."
        ),
        chat_id=chat_id,
    )


def send_post_draft_to_telegram(
    post_content: str,
    slot_name: str,
    topic: str,
    chat_id: str = None,
    photo_path: str = None,
) -> dict:
    encoded = urllib.parse.quote(post_content[:1500])
    share_url = f"https://www.linkedin.com/feed/?shareActive=true&text={encoded}"
    markup = {
        "inline_keyboard": [
            [{"text": "✅ Approve & auto-post", "callback_data": "approve"}],
            [{"text": "📲 Open LinkedIn composer", "url": share_url}],
        ]
    }
    caption = (
        f"{slot_name}\nTopic: {topic}\n"
        "----------------\n\n"
        f"{post_content}\n\n"
        "----------------\n"
        "Tap Approve to publish on LinkedIn.\n"
        "Or send a message with the change you want."
    )
    _, default_chat_id, _ = get_telegram_config()
    target = str(chat_id or default_chat_id or "")
    if photo_path:
        return send_telegram_photo(target, photo_path, caption=caption, reply_markup=markup)
    return send_telegram_message(caption, chat_id=target, reply_markup=markup)


def send_callback_answer(callback_id: str, text: str = "OK") -> dict:
    return _api("answerCallbackQuery", {"callback_query_id": callback_id, "text": text})

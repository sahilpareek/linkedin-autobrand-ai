from services.user_manager import (
    resolve_user_from_telegram,
    bind_telegram_chat,
    get_pending_post,
    save_pending_post,
    clear_pending_post,
    log_user_post,
    is_approve_text,
    get_user_by_connect_code,
)
from services.telegram_service import (
    send_telegram_message,
    send_callback_answer,
    send_user_welcome,
)
from services.linkedin_service import publish_linkedin_post, resolve_publish_token, is_access_token


def _start_payload(text: str) -> str:
    raw = (text or "").strip()
    if raw.upper().startswith("/START"):
        parts = raw.split(maxsplit=1)
        return parts[1].strip() if len(parts) > 1 else ""
    if raw.upper().startswith("CONNECT"):
        parts = raw.split(maxsplit=1)
        return parts[1].strip() if len(parts) > 1 else ""
    return ""


def _publish_pending(user: dict) -> str:
    pending = get_pending_post(user)
    if not pending:
        return "You have no draft waiting. Next slot will send a new one."

    content = pending.get("content", "")
    token, urn, source = resolve_publish_token(user)
    if not is_access_token(token):
        return (
            "Draft is ready, but LinkedIn auto-post needs an access token.\n"
            "Use the Open LinkedIn composer button, or add your LinkedIn token in the website form.\n"
            "Owner: set LINKEDIN_ACCESS_TOKEN in .env and connect this same Telegram chat as TELEGRAM_CHAT_ID."
        )

    res = publish_linkedin_post(content, token=token, urn=urn)
    if res.get("success"):
        clear_pending_post(user)
        log_user_post(user, content, "PUBLISHED", res.get("post_id", ""))
        return f"Posted on LinkedIn. Source: {source}."
    return f"LinkedIn upload failed: {res.get('error')}"


def _apply_edits(user: dict, feedback: str) -> str:
    from services.post_generator import refine_post

    pending = get_pending_post(user)
    if not pending:
        return "No draft to edit. Wait for the next scheduled post."
    updated = refine_post(pending.get("content", ""), feedback)
    pending["content"] = updated
    save_pending_post(user, pending)
    return (
        "Draft updated:\n\n"
        f"{updated}\n\n"
        "Tap Approve to post, or send more changes."
    )


def handle_telegram_update(update: dict) -> dict:
    """Pure-ish handler. Returns {handled, reply, action} for tests."""
    callback = update.get("callback_query")
    message = update.get("message") or update.get("edited_message") or {}

    if callback:
        chat = (callback.get("message") or {}).get("chat") or {}
        from_user = callback.get("from") or {}
        chat_id = chat.get("id") or from_user.get("id")
        username = from_user.get("username")
        data = callback.get("data") or ""
        user = resolve_user_from_telegram(chat_id=chat_id, username=username)
        send_callback_answer(callback.get("id", ""), "Working...")
        if not user:
            send_telegram_message("Please register on the website first, then tap Start with your code.", chat_id=chat_id)
            return {"handled": True, "action": "unbound", "reply": "unbound"}
        bind_telegram_chat(user, chat_id, username)
        if data == "approve":
            reply = _publish_pending(user)
            send_telegram_message(reply, chat_id=chat_id)
            return {"handled": True, "action": "approve", "reply": reply}
        if data == "edit_hint":
            reply = "Type your change in this chat. I will update the draft."
            send_telegram_message(reply, chat_id=chat_id)
            return {"handled": True, "action": "edit_hint", "reply": reply}
        return {"handled": True, "action": "callback_other", "reply": ""}

    if not message:
        return {"handled": False, "action": "empty", "reply": ""}

    chat_id = (message.get("chat") or {}).get("id")
    username = (message.get("from") or {}).get("username")
    text = (message.get("text") or "").strip()
    if not chat_id:
        return {"handled": False, "action": "no_chat", "reply": ""}

    start_code = _start_payload(text)
    user = resolve_user_from_telegram(chat_id=chat_id, username=username, text=text)

    if start_code:
        found = get_user_by_connect_code(start_code)
        if found:
            bind_telegram_chat(found, chat_id, username)
            send_user_welcome(str(chat_id), found.get("name", "there"))
            return {"handled": True, "action": "bind", "reply": "bound"}
        send_telegram_message(
            "That code was not found. Open the website success screen and tap the bot link again.",
            chat_id=chat_id,
        )
        return {"handled": True, "action": "bad_code", "reply": "bad_code"}

    if not user:
        send_telegram_message(
            "I do not know this chat yet. Fill the website form, then open the bot link with your code.",
            chat_id=chat_id,
        )
        return {"handled": True, "action": "unbound", "reply": "unbound"}

    bind_telegram_chat(user, chat_id, username)

    if is_approve_text(text):
        reply = _publish_pending(user)
        send_telegram_message(reply, chat_id=chat_id)
        return {"handled": True, "action": "approve", "reply": reply}

    if get_pending_post(user) and text:
        try:
            reply = _apply_edits(user, text)  # refine_post is patched on telegram_bot in tests
        except Exception as e:
            reply = f"Could not update draft: {e}"
        send_telegram_message(reply, chat_id=chat_id)
        return {"handled": True, "action": "refine", "reply": reply}

    send_telegram_message(
        f"Hi {user.get('name')}! Your next draft will arrive at the next slot. "
        "If a draft is waiting, type APPROVE or send changes.",
        chat_id=chat_id,
    )
    return {"handled": True, "action": "idle", "reply": "idle"}

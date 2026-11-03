import os
import json
import re
import secrets
from datetime import datetime

USERS_DIR = os.getenv("USERS_DIR", "data/users")
APPROVE_WORDS = {
    "APPROVE", "YES", "OK", "POST", "HAAN", "PUBLISH",
    "THIK HAI", "SEND", "/APPROVE", "✅", "OKAY"
}


def sanitize_phone(phone: str) -> str:
    clean = re.sub(r"[^\d]", "", phone or "")
    return clean


def sanitize_telegram(username: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "", (username or "").lstrip("@")).lower()


def user_folder_key(user_data: dict) -> str:
    phone = sanitize_phone(user_data.get("phone", ""))
    if phone:
        return phone
    tg = sanitize_telegram(user_data.get("telegram_username", ""))
    if tg:
        return f"tg_{tg}"
    chat_id = str(user_data.get("telegram_chat_id") or "").strip()
    if chat_id:
        return f"chat_{chat_id}"
    return f"user_{secrets.token_hex(4)}"


def get_user_dir(key: str) -> str:
    folder = os.path.join(USERS_DIR, key)
    os.makedirs(folder, exist_ok=True)
    return folder


def _profile_path_for_key(key: str) -> str:
    return os.path.join(USERS_DIR, key, "profile.json")


def save_user(user_data: dict) -> dict:
    if not user_data.get("connect_code"):
        user_data["connect_code"] = secrets.token_hex(3).upper()
    user_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "registered_at" not in user_data:
        user_data["registered_at"] = user_data["updated_at"]
    user_data.setdefault("is_active", True)

    key = user_data.get("folder_key") or user_folder_key(user_data)
    user_data["folder_key"] = key
    folder = get_user_dir(key)
    with open(os.path.join(folder, "profile.json"), "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2, ensure_ascii=False)
    return user_data


def _load_profile(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_all_users(active_only: bool = True) -> list:
    users = []
    if not os.path.exists(USERS_DIR):
        return users
    for folder_name in os.listdir(USERS_DIR):
        path = _profile_path_for_key(folder_name)
        if not os.path.isfile(path):
            continue
        u = _load_profile(path)
        if not u:
            continue
        if active_only and not u.get("is_active", True):
            continue
        users.append(u)
    return users


def get_user_by_phone(phone: str):
    if not phone:
        return None
    digits = sanitize_phone(phone)
    path = _profile_path_for_key(digits)
    if os.path.isfile(path):
        return _load_profile(path)
    for user in get_all_users(active_only=False):
        if sanitize_phone(user.get("phone", "")) == digits:
            return user
    return None


def get_user_by_telegram_chat_id(chat_id) -> dict:
    if chat_id is None or chat_id == "":
        return None
    wanted = str(chat_id)
    for user in get_all_users(active_only=False):
        if str(user.get("telegram_chat_id") or "") == wanted:
            return user
    return None


def get_user_by_telegram_username(username: str):
    wanted = sanitize_telegram(username)
    if not wanted:
        return None
    path = _profile_path_for_key(f"tg_{wanted}")
    if os.path.isfile(path):
        return _load_profile(path)
    for user in get_all_users(active_only=False):
        if sanitize_telegram(user.get("telegram_username", "")) == wanted:
            return user
    return None


def get_user_by_connect_code(code: str):
    wanted = (code or "").strip().upper()
    if not wanted:
        return None
    for user in get_all_users(active_only=False):
        if str(user.get("connect_code", "")).upper() == wanted:
            return user
    return None


def resolve_user_from_telegram(chat_id=None, username: str = None, text: str = None):
    user = get_user_by_telegram_chat_id(chat_id)
    if user:
        return user
    user = get_user_by_telegram_username(username)
    if user:
        return user
    if text:
        parts = text.strip().split()
        if len(parts) >= 2 and parts[0].upper() in ("/START", "CONNECT", "/CONNECT"):
            return get_user_by_connect_code(parts[1])
        if len(parts) == 1 and len(parts[0]) == 6:
            found = get_user_by_connect_code(parts[0])
            if found:
                return found
    return None


def bind_telegram_chat(user: dict, chat_id, username: str = None) -> dict:
    user["telegram_chat_id"] = str(chat_id)
    if username:
        user["telegram_username"] = sanitize_telegram(username)
    return save_user(user)


def save_pending_post(user: dict, post_data: dict):
    key = user.get("folder_key") or user_folder_key(user)
    folder = get_user_dir(key)
    post_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(folder, "pending_post.json"), "w", encoding="utf-8") as f:
        json.dump(post_data, f, indent=2, ensure_ascii=False)


def get_pending_post(user: dict):
    key = user.get("folder_key") or user_folder_key(user)
    pending_path = os.path.join(USERS_DIR, key, "pending_post.json")
    if os.path.isfile(pending_path):
        return _load_profile(pending_path)
    return None


def clear_pending_post(user: dict):
    key = user.get("folder_key") or user_folder_key(user)
    pending_path = os.path.join(USERS_DIR, key, "pending_post.json")
    if os.path.exists(pending_path):
        os.remove(pending_path)


def log_user_post(user: dict, post_content: str, status: str, post_id: str = ""):
    key = user.get("folder_key") or user_folder_key(user)
    folder = get_user_dir(key)
    history_path = os.path.join(folder, "history.json")
    history = []
    if os.path.exists(history_path):
        loaded = _load_profile(history_path)
        if isinstance(loaded, list):
            history = loaded
    history.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "post_id": post_id,
        "content": post_content
    })
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history[:50], f, indent=2, ensure_ascii=False)


def is_approve_text(text: str) -> bool:
    clean = re.sub(r"[^A-Za-z0-9 /]", "", (text or "")).strip().upper()
    return clean in APPROVE_WORDS

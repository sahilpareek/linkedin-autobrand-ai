import os
import json
import re
from datetime import datetime

USERS_DIR = "data/users"

def sanitize_phone(phone: str) -> str:
    """Removes non-alphanumeric chars to make safe folder name (e.g. +919876543210 -> 919876543210)."""
    clean = re.sub(r"[^\d]", "", phone)
    return clean if clean else "unknown_user"

def get_user_dir(phone: str) -> str:
    folder = os.path.join(USERS_DIR, sanitize_phone(phone))
    os.makedirs(folder, exist_ok=True)
    return folder

def save_user(user_data: dict) -> dict:
    """
    Saves isolated user profile under data/users/<phone>/profile.json.
    """
    phone = user_data.get("phone", "")
    folder = get_user_dir(phone)
    profile_path = os.path.join(folder, "profile.json")

    user_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "registered_at" not in user_data:
        user_data["registered_at"] = user_data["updated_at"]

    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2, ensure_ascii=False)

    return user_data

def get_user_by_phone(phone: str) -> dict:
    folder = get_user_dir(phone)
    profile_path = os.path.join(folder, "profile.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def get_all_users() -> list:
    """Returns list of all active registered user profiles."""
    users = []
    if not os.path.exists(USERS_DIR):
        return users

    for folder_name in os.listdir(USERS_DIR):
        profile_path = os.path.join(USERS_DIR, folder_name, "profile.json")
        if os.path.isfile(profile_path):
            try:
                with open(profile_path, "r", encoding="utf-8") as f:
                    u = json.load(f)
                    if u.get("is_active", True):
                        users.append(u)
            except Exception:
                continue
    return users

def save_pending_post(phone: str, post_data: dict):
    """Saves post waiting for WhatsApp approval."""
    folder = get_user_dir(phone)
    pending_path = os.path.join(folder, "pending_post.json")
    post_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(pending_path, "w", encoding="utf-8") as f:
        json.dump(post_data, f, indent=2, ensure_ascii=False)

def get_pending_post(phone: str) -> dict:
    folder = get_user_dir(phone)
    pending_path = os.path.join(folder, "pending_post.json")
    if os.path.exists(pending_path):
        try:
            with open(pending_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def clear_pending_post(phone: str):
    folder = get_user_dir(phone)
    pending_path = os.path.join(folder, "pending_post.json")
    if os.path.exists(pending_path):
        os.remove(pending_path)

def log_user_post(phone: str, post_content: str, status: str, post_id: str = ""):
    folder = get_user_dir(phone)
    history_path = os.path.join(folder, "history.json")
    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "post_id": post_id,
        "content": post_content
    })

    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history[:50], f, indent=2, ensure_ascii=False)

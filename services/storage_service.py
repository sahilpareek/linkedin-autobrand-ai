import json
import os

DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
HISTORY_FILE = os.path.join(DATA_DIR, "posts_history.json")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_profile(data: dict):
    ensure_data_dir()
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_profile() -> dict:
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def add_post_to_history(post_text: str, status: str = "PUBLISHED", post_id: str = ""):
    ensure_data_dir()
    history = load_history()
    import datetime
    item = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "post_id": post_id,
        "preview": post_text[:120] + "...",
        "content": post_text
    }
    history.insert(0, item)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[:50], f, indent=2, ensure_ascii=False)

def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

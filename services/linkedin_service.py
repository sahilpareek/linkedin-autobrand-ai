import os


def get_linkedin_credentials(token: str = None, urn: str = None):
    access_token = token or os.getenv("LINKEDIN_ACCESS_TOKEN")
    person_urn = urn or os.getenv("LINKEDIN_PERSON_URN")
    return access_token, person_urn


def is_access_token(value: str) -> bool:
    if not value:
        return False
    text = value.strip()
    if text.startswith("http") or "linkedin.com" in text.lower():
        return False
    return len(text) > 40


def resolve_publish_token(user: dict = None) -> tuple:
    """Returns (token, urn, source). Never uses a profile URL as a token."""
    user = user or {}
    user_token = user.get("linkedin_token") or user.get("linkedin_access_token") or ""
    urn = user.get("linkedin_urn") or os.getenv("LINKEDIN_PERSON_URN") or "urn:li:person:me"

    if is_access_token(user_token):
        return user_token, urn, "user"

    admin_chat = str(os.getenv("TELEGRAM_CHAT_ID") or "")
    user_chat = str(user.get("telegram_chat_id") or "")
    env_token = os.getenv("LINKEDIN_ACCESS_TOKEN") or ""
    if is_access_token(env_token) and admin_chat and user_chat and admin_chat == user_chat:
        return env_token, os.getenv("LINKEDIN_PERSON_URN") or urn, "admin_env"

    if is_access_token(env_token) and user.get("use_owner_linkedin"):
        return env_token, os.getenv("LINKEDIN_PERSON_URN") or urn, "owner"

    return "", urn, "none"


def verify_linkedin_token(token: str = None) -> dict:
    access_token, _ = get_linkedin_credentials(token)
    if not is_access_token(access_token):
        return {"valid": False, "error": "LinkedIn Access Token is missing."}

    import requests

    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {"valid": True, "name": data.get("name", "LinkedIn User"), "sub": data.get("sub")}
        return {"valid": False, "error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def publish_linkedin_post(post_text: str, token: str = None, urn: str = None) -> dict:
    access_token, person_urn = get_linkedin_credentials(token, urn)

    if not is_access_token(access_token):
        return {"success": False, "error": "LinkedIn Access Token missing. Add a real token to auto-post."}
    if not person_urn:
        person_urn = "urn:li:person:me"

    if not str(person_urn).startswith("urn:li:person:"):
        person_urn = f"urn:li:person:{person_urn}"

    import requests

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=15, headers=headers)
        if response.status_code in (200, 201):
            data = response.json()
            return {"success": True, "post_id": data.get("id", "Unknown")}
        return {
            "success": False,
            "error": f"LinkedIn Error ({response.status_code}): {response.text}"
        }
    except Exception as e:
        return {"success": False, "error": f"Network exception: {str(e)}"}

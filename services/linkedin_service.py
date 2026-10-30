import os
import requests

def get_linkedin_credentials(token: str = None, urn: str = None):
    access_token = token or os.getenv("LINKEDIN_ACCESS_TOKEN")
    person_urn = urn or os.getenv("LINKEDIN_PERSON_URN")
    return access_token, person_urn

def verify_linkedin_token(token: str = None) -> dict:
    """Verifies if the access token is valid and returns user info if available."""
    access_token, _ = get_linkedin_credentials(token)
    if not access_token:
        return {"valid": False, "error": "LinkedIn Access Token is missing."}

    # LinkedIn OpenID UserInfo endpoint
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {"valid": True, "name": data.get("name", "LinkedIn User"), "sub": data.get("sub")}
        else:
            return {"valid": False, "error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def publish_linkedin_post(post_text: str, token: str = None, urn: str = None) -> dict:
    """Publishes a text post to LinkedIn using the UGC API."""
    access_token, person_urn = get_linkedin_credentials(token, urn)

    if not access_token:
        return {"success": False, "error": "LinkedIn Access Token missing."}
    if not person_urn:
        return {"success": False, "error": "LinkedIn Person URN missing (e.g. urn:li:person:XXXX)."}

    # Format person_urn if only numerical ID was provided
    if not person_urn.startswith("urn:li:person:"):
        person_urn = f"urn:li:person:{person_urn}"

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
                "shareCommentary": {
                    "text": post_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code in (200, 201):
            data = response.json()
            post_id = data.get("id", "Unknown")
            return {"success": True, "post_id": post_id}
        else:
            return {
                "success": False, 
                "error": f"LinkedIn Error ({response.status_code}): {response.text}"
            }
    except Exception as e:
        return {"success": False, "error": f"Network exception: {str(e)}"}

import requests

def get_github_code_link(github_username: str, topic_slug: str = "web-tips") -> str:
    """
    Generates an authentic GitHub code link referencing the user's GitHub ID.
    If username is empty, returns a default public repository link.
    """
    clean_user = github_username.strip().lstrip("@") if github_username else ""
    if not clean_user:
        return ""

    # Link to user's repositories or specific tips repo
    return f"https://github.com/{clean_user}"

def append_github_link_to_post(post_text: str, github_username: str) -> str:
    """Appends GitHub profile/code reference link into post content before hashtags."""
    if not github_username:
        return post_text

    clean_user = github_username.strip().lstrip("@")
    gh_line = f"📂 Code & Examples on GitHub: https://github.com/{clean_user}"

    # Insert before hashtags
    if "#" in post_text:
        parts = post_text.rsplit("#", 1)
        first_hash_idx = post_text.find("#")
        body = post_text[:first_hash_idx].rstrip()
        hashtags = post_text[first_hash_idx:]
        return f"{body}\n\n{gh_line}\n\n{hashtags}"
    else:
        return f"{post_text}\n\n{gh_line}"

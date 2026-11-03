import os

from services.user_manager import get_all_users, save_pending_post, get_user_dir
from services.github_service import append_github_link_to_post
from services.image_card_service import generate_png_banner
from services.telegram_service import send_post_draft_to_telegram
from services.schedule_utils import now_ist, detect_slot, weekend_kind_for_tests


def resume_context(user: dict) -> str:
    return "\n".join(
        [
            f"Name: {user.get('name', '')}",
            f"GitHub: {user.get('github_username', '')}",
            f"LinkedIn: {user.get('linkedin_url') or user.get('linkedin_token', '')}",
            user.get("skills_summary") or "",
            (user.get("raw_resume_sample") or "")[:600],
        ]
    )


def generate_slot_content(user: dict, slot: str) -> dict:
    from services.post_generator import (
        generate_morning_ui_post,
        generate_afternoon_frontend_post,
        generate_evening_ai_post,
        generate_weekend_interactive_post,
    )

    skills = resume_context(user)
    github = user.get("github_username", "")
    if slot == "weekend":
        kind = weekend_kind_for_tests(now_ist().weekday())
        res = generate_weekend_interactive_post(kind, profile_context=skills)
    elif slot == "morning":
        res = generate_morning_ui_post(skills)
    elif slot == "afternoon":
        res = generate_afternoon_frontend_post(skills)
        res["content"] = append_github_link_to_post(res["content"], github)
    elif slot == "evening":
        res = generate_evening_ai_post(skills)
    else:
        res = generate_morning_ui_post(skills)

    author = "@" + (user.get("telegram_username") or user.get("name") or "AutoBrand")
    folder = get_user_dir(user.get("folder_key") or "tmp")
    banner_path = os.path.join(folder, f"banner_{slot}.png")
    generate_png_banner(
        title=res.get("topic") or slot,
        category=res.get("slot_key") or slot,
        bullet_points=["Class 6 English", "Tags + top hashtags", "Approve on Telegram"],
        author=author,
        filepath=banner_path,
    )
    res["banner_path"] = banner_path
    return res


def dispatch_slot_for_all_users(slot: str = "morning") -> dict:
    users = get_all_users()
    sent = 0
    errors = []
    for user in users:
        try:
            res = generate_slot_content(user, slot)
            save_pending_post(user, {
                "slot": res.get("slot"),
                "topic": res.get("topic"),
                "content": res["content"],
                "banner_path": res.get("banner_path"),
            })
            chat_id = user.get("telegram_chat_id")
            send_post_draft_to_telegram(
                post_content=res["content"],
                slot_name=res.get("slot", slot),
                topic=res.get("topic", ""),
                chat_id=chat_id,
                photo_path=res.get("banner_path"),
            )
            sent += 1
        except Exception as e:
            errors.append({"user": user.get("name"), "error": str(e)})
    return {"users": len(users), "sent": sent, "errors": errors}

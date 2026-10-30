import os
import io
import asyncio
import threading
import time
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from services.user_manager import (
    save_user,
    get_user_by_phone,
    get_all_users,
    save_pending_post,
    get_pending_post,
    clear_pending_post,
    log_user_post
)
from services.resume_parser import extract_text_from_pdf_stream, analyze_resume_profile
from services.post_generator import (
    generate_morning_ui_post,
    generate_afternoon_frontend_post,
    generate_evening_ai_post,
    generate_weekend_interactive_post,
    refine_post
)
from services.image_card_service import generate_svg_banner
from services.github_service import append_github_link_to_post
from services.linkedin_service import publish_linkedin_post
from services.telegram_service import (
    notify_admin_telegram_new_user,
    send_post_draft_to_telegram
)
from services.whatsapp_service import (
    send_whatsapp_message,
    notify_admin_new_user,
    send_user_welcome_message,
    send_whatsapp_draft_for_approval,
    format_whatsapp_number
)

app = FastAPI(title="AutoBrand AI - Autonomous LinkedIn Branding")

# Serve Landing Page
@app.get("/", response_class=HTMLResponse)
async def serve_landing_page():
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>AutoBrand AI Running</h1>"


# ==========================================
# 1. User Registration / Resume Upload API
# ==========================================
@app.post("/api/register")
async def register_user(
    name: str = Form(...),
    phone: str = Form(...),
    github_username: str = Form(...),
    linkedin_token: str = Form(...),
    resume: UploadFile = File(...)
):
    try:
        # 1. Read & Parse PDF Resume
        pdf_bytes = await resume.read()
        resume_stream = io.BytesIO(pdf_bytes)
        raw_text = extract_text_from_pdf_stream(resume_stream)

        if not raw_text.strip():
            return JSONResponse(status_code=400, content={"success": False, "error": "Could not read text from uploaded PDF resume."})

        # 2. Extract Skills with Gemini AI
        analysis_result = analyze_resume_profile(raw_text)
        skills_summary = analysis_result.get("analysis", "")

        # 3. Save Isolated User Profile
        user_data = {
            "name": name.strip(),
            "phone": format_whatsapp_number(phone),
            "github_username": github_username.strip(),
            "linkedin_token": linkedin_token.strip(),
            "linkedin_urn": "urn:li:person:me",  # Will auto-resolve or format
            "skills_summary": skills_summary,
            "raw_resume_sample": raw_text[:800],
            "is_active": True
        }
        saved = save_user(user_data)

        # 4. Notify Admin on Telegram
        try:
            notify_admin_telegram_new_user(user_data)
        except Exception as e:
            print(f"Admin Telegram Notification Error: {e}")

        # 5. Send Welcome WhatsApp Message to User
        try:
            send_user_welcome_message(user_data["phone"], user_data["name"])
        except Exception as e:
            print(f"User WhatsApp Welcome Error: {e}")

        return JSONResponse(content={
            "success": True, 
            "message": f"Welcome {name}! Your automated LinkedIn agent is now active via WhatsApp."
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ==========================================
# 2. WhatsApp Two-Way Webhook (Twilio)
# User approvals & refinements happen HERE!
# ==========================================
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form_data = await request.form()
    from_number = form_data.get("From", "")
    incoming_msg = form_data.get("Body", "").strip()

    print(f"📩 Incoming WhatsApp from {from_number}: '{incoming_msg}'")

    if not from_number or not incoming_msg:
        return Response(content="<Response></Response>", media_type="application/xml")

    # Look up user
    user = get_user_by_phone(from_number)
    if not user:
        send_whatsapp_message(
            from_number,
            "👋 Hi! We couldn't find your profile. Please upload your resume at our portal to activate your account."
        )
        return Response(content="<Response></Response>", media_type="application/xml")

    # Check for pending draft
    pending = get_pending_post(from_number)
    clean_text = incoming_msg.upper()

    # Case A: User approves the post
    if clean_text in ["APPROVE", "YES", "OK", "POST", "HAAN", "PUBLISH", "THIK HAI", "SEND"]:
        if not pending:
            send_whatsapp_message(from_number, "ℹ️ You don't have any pending drafts to publish right now.")
            return Response(content="<Response></Response>", media_type="application/xml")

        # Publish to user's LinkedIn
        post_content = pending.get("content", "")
        token = user.get("linkedin_token")
        urn = user.get("linkedin_urn", "urn:li:person:me")

        res = publish_linkedin_post(post_content, token=token, urn=urn)
        if res.get("success"):
            clear_pending_post(from_number)
            log_user_post(from_number, post_content, "PUBLISHED", res.get("post_id", ""))
            reply = "🎉 *Congratulations!* Your approved post has been uploaded to LinkedIn! 🚀\nKeep an eye out for comments."
        else:
            reply = f"❌ LinkedIn upload failed: {res.get('error')}\nPlease check your LinkedIn token."

        send_whatsapp_message(from_number, reply)
        return Response(content="<Response></Response>", media_type="application/xml")

    # Case B: User requested changes/modifications to the draft
    if pending:
        send_whatsapp_message(from_number, "⚙️ Updating your post based on your feedback. One moment please...")
        try:
            current_draft = pending.get("content", "")
            updated_text = refine_post(current_draft, incoming_msg)

            # Update pending post
            pending["content"] = updated_text
            save_pending_post(from_number, pending)

            reply = (
                "🔄 *Draft Updated Successfully!*\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{updated_text}\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "⚡ *What would you like to do?*\n"
                "• Reply *APPROVE* to publish this on your LinkedIn.\n"
                "• Or reply with more changes!"
            )
            send_whatsapp_message(from_number, reply)
        except Exception as e:
            send_whatsapp_message(from_number, f"⚠️ Error updating draft: {str(e)}")

        return Response(content="<Response></Response>", media_type="application/xml")

    # Case C: General interaction / No pending draft
    send_whatsapp_message(
        from_number,
        f"👋 Hi {user.get('name')}! Your automated branding agent is active.\nYou will receive your next scheduled post draft at the upcoming traffic peak."
    )
    return Response(content="<Response></Response>", media_type="application/xml")


# ==========================================
# 3. Multi-User Scheduled Dispatcher
# ==========================================
def dispatch_slot_for_all_users(slot: str = "morning"):
    """Runs slot generation and sends WhatsApp approval draft to all active users."""
    users = get_all_users()
    print(f"🚀 Running Slot '{slot}' for {len(users)} registered users...")

    for user in users:
        phone = user.get("phone")
        name = user.get("name", "Creator")
        skills = user.get("skills_summary", "")
        github = user.get("github_username", "")

        try:
            # Generate slot-specific content
            if slot == "morning":
                res = generate_morning_ui_post(skills)
                slot_label = "🌅 Morning UI/UX Short Trick"
            elif slot == "afternoon":
                res = generate_afternoon_frontend_post(skills)
                slot_label = "☀️ Afternoon Frontend Trick"
                # Attach user's GitHub link!
                res["content"] = append_github_link_to_post(res["content"], github)
            elif slot == "evening":
                res = generate_evening_ai_post(skills)
                slot_label = "🌙 Evening Trending AI News"
            elif slot == "weekend":
                res = generate_weekend_interactive_post("poll")
                slot_label = "🎉 Weekend Interactive Challenge"
            else:
                res = generate_morning_ui_post(skills)
                slot_label = "🌅 Morning Post"

            # Save as pending approval
            pending_data = {
                "slot": slot_label,
                "topic": res.get("topic", "Tech Update"),
                "content": res["content"]
            }
            save_pending_post(phone, pending_data)

            # Send draft to Telegram with 1-Tap LinkedIn Post Button
            send_post_draft_to_telegram(
                post_content=res["content"],
                slot_name=slot_label,
                topic=res.get("topic", "")
            )
            print(f"✅ Draft dispatched to Telegram for {name}")

        except Exception as e:
            print(f"❌ Error dispatching to {name} ({phone}): {e}")


@app.get("/api/trigger-slot")
async def trigger_slot_manually(slot: str = "morning"):
    """Allows manual or cron trigger for a slot."""
    dispatch_slot_for_all_users(slot)
    return {"status": "dispatched", "slot": slot}


# ==========================================
# 4. Background Cron Scheduler (IST Timings)
# ==========================================
def background_scheduler_loop():
    import datetime
    import schedule

    def job_morning():
        dispatch_slot_for_all_users("morning")

    def job_afternoon():
        dispatch_slot_for_all_users("afternoon")

    def job_evening():
        dispatch_slot_for_all_users("evening")

    # Daily peak traffic schedules (in server local time or converted)
    schedule.every().day.at("09:00").do(job_morning)
    schedule.every().day.at("13:00").do(job_afternoon)
    schedule.every().day.at("19:00").do(job_evening)

    while True:
        schedule.run_pending()
        time.sleep(30)

# Start background thread on startup
@app.on_event("startup")
def startup_event():
    t = threading.Thread(target=background_scheduler_loop, daemon=True)
    t.start()
    print("🕒 Background multi-user scheduler thread started.")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)

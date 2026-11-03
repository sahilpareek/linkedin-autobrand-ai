import os
import io
import threading
import time
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()

from services.user_manager import save_user, sanitize_telegram
from services.resume_parser import extract_text_from_pdf_stream, analyze_resume_profile
from services.telegram_service import notify_admin_telegram_new_user, bot_start_link
from services.telegram_bot import handle_telegram_update
from services.slot_engine import dispatch_slot_for_all_users
from services.schedule_utils import detect_slot

app = FastAPI(title="AutoBrand AI - Resume LinkedIn Agent")


@app.get("/", response_class=HTMLResponse)
async def serve_landing_page():
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>AutoBrand AI Running</h1>"


@app.get("/health")
async def health():
    return {"ok": True, "service": "autobrand-ai"}


@app.post("/api/register")
async def register_user(
    name: str = Form(...),
    telegram_username: str = Form(...),
    github_username: str = Form(...),
    linkedin_url: str = Form(...),
    resume: UploadFile = File(...),
    phone: str = Form(""),
    linkedin_token: str = Form(""),
):
    try:
        pdf_bytes = await resume.read()
        raw_text = extract_text_from_pdf_stream(io.BytesIO(pdf_bytes))
        if not raw_text.strip():
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Could not read text from the PDF resume."},
            )

        analysis_result = analyze_resume_profile(raw_text)
        skills_summary = analysis_result.get("analysis", "")

        user_data = {
            "name": name.strip(),
            "telegram_username": sanitize_telegram(telegram_username),
            "phone": phone.strip(),
            "github_username": github_username.strip().lstrip("@"),
            "linkedin_url": linkedin_url.strip(),
            "linkedin_token": (linkedin_token or "").strip(),
            "linkedin_urn": "urn:li:person:me",
            "skills_summary": skills_summary,
            "raw_resume_sample": raw_text[:1200],
            "is_active": True,
        }
        saved = save_user(user_data)
        try:
            notify_admin_telegram_new_user(saved)
        except Exception as e:
            print(f"Admin Telegram Notification Error: {e}")

        start_link = bot_start_link(saved["connect_code"])
        return JSONResponse(content={
            "success": True,
            "message": f"Welcome {name}! Open Telegram and start the bot with your code.",
            "connect_code": saved["connect_code"],
            "bot_link": start_link,
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    update = await request.json()
    try:
        handle_telegram_update(update)
    except Exception as e:
        print(f"Telegram webhook error: {e}")
    return {"ok": True}


@app.get("/api/trigger-slot")
async def trigger_slot_manually(slot: str = "auto"):
    chosen = detect_slot() if slot == "auto" else slot
    result = dispatch_slot_for_all_users(chosen)
    return {"status": "dispatched", "slot": chosen, **result}


def background_scheduler_loop():
    import schedule

    schedule.every().monday.at("09:00").do(lambda: dispatch_slot_for_all_users("morning"))
    schedule.every().tuesday.at("09:00").do(lambda: dispatch_slot_for_all_users("morning"))
    schedule.every().wednesday.at("09:00").do(lambda: dispatch_slot_for_all_users("morning"))
    schedule.every().thursday.at("09:00").do(lambda: dispatch_slot_for_all_users("morning"))
    schedule.every().friday.at("09:00").do(lambda: dispatch_slot_for_all_users("morning"))

    schedule.every().monday.at("13:00").do(lambda: dispatch_slot_for_all_users("afternoon"))
    schedule.every().tuesday.at("13:00").do(lambda: dispatch_slot_for_all_users("afternoon"))
    schedule.every().wednesday.at("13:00").do(lambda: dispatch_slot_for_all_users("afternoon"))
    schedule.every().thursday.at("13:00").do(lambda: dispatch_slot_for_all_users("afternoon"))
    schedule.every().friday.at("13:00").do(lambda: dispatch_slot_for_all_users("afternoon"))

    schedule.every().monday.at("19:00").do(lambda: dispatch_slot_for_all_users("evening"))
    schedule.every().tuesday.at("19:00").do(lambda: dispatch_slot_for_all_users("evening"))
    schedule.every().wednesday.at("19:00").do(lambda: dispatch_slot_for_all_users("evening"))
    schedule.every().thursday.at("19:00").do(lambda: dispatch_slot_for_all_users("evening"))
    schedule.every().friday.at("19:00").do(lambda: dispatch_slot_for_all_users("evening"))

    schedule.every().saturday.at("11:00").do(lambda: dispatch_slot_for_all_users("weekend"))
    schedule.every().sunday.at("11:00").do(lambda: dispatch_slot_for_all_users("weekend"))
    schedule.every().saturday.at("17:00").do(lambda: dispatch_slot_for_all_users("weekend"))
    schedule.every().sunday.at("17:00").do(lambda: dispatch_slot_for_all_users("weekend"))

    while True:
        schedule.run_pending()
        time.sleep(30)


def telegram_polling_loop():
    import requests

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or os.getenv("TELEGRAM_POLLING", "1") != "1":
        return
    offset = 0
    print("Telegram long-polling started.")
    while True:
        try:
            res = requests.get(
                f"https://api.telegram.org/bot{token}/getUpdates",
                params={"offset": offset, "timeout": 25},
                timeout=35,
            )
            data = res.json()
            for update in data.get("result") or []:
                offset = update["update_id"] + 1
                handle_telegram_update(update)
        except Exception as e:
            print(f"Telegram poll error: {e}")
            time.sleep(3)


@app.on_event("startup")
def startup_event():
    threading.Thread(target=background_scheduler_loop, daemon=True).start()
    threading.Thread(target=telegram_polling_loop, daemon=True).start()
    print("Scheduler + Telegram polling threads started.")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)

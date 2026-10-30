import os
from twilio.rest import Client

def send_whatsapp_preview(post_text: str,
                          app_url: str = None,
                          account_sid: str = None, 
                          auth_token: str = None, 
                          from_whatsapp: str = None, 
                          to_whatsapp: str = None) -> dict:
    """
    Sends the generated post draft to user's WhatsApp using Twilio.
    """
    sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
    token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
    from_num = from_whatsapp or os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    to_num = to_whatsapp or os.getenv("USER_WHATSAPP_NUMBER")

    if not sid or not token:
        return {"success": False, "error": "Twilio Account SID or Auth Token missing."}
    if not to_num:
        return {"success": False, "error": "Recipient WhatsApp Number missing (USER_WHATSAPP_NUMBER)."}

    # Format numbers with whatsapp: prefix if missing
    if not from_num.startswith("whatsapp:"):
        from_num = f"whatsapp:{from_num}"
    if not to_num.startswith("whatsapp:"):
        to_num = f"whatsapp:{to_num}"

    link_info = f"\n\n📱 *Review/Approve in Dashboard:*\n{app_url}" if app_url else ""

    message_body = (
        "🚀 *New LinkedIn Post Draft Ready for Review!*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"{post_text}\n"
        "━━━━━━━━━━━━━━━━━━━━"
        f"{link_info}\n\n"
        "👉 You can approve or modify this draft in your Streamlit Mobile Dashboard."
    )

    try:
        client = Client(sid, token)
        msg = client.messages.create(
            body=message_body,
            from_=from_num,
            to=to_num
        )
        return {"success": True, "message_sid": msg.sid}
    except Exception as e:
        return {"success": False, "error": f"Twilio WhatsApp Error: {str(e)}"}

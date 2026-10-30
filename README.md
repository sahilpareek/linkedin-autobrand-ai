# 🚀 AutoBrand AI — Multi-User Autonomous LinkedIn Branding via WhatsApp

Ek fully automated system jisme **koi bhi user** website par jakar apna **Resume (PDF)**, **GitHub username**, aur **LinkedIn Token** enter karke register kar sakta hai. Iske baad user ko website kholne ki ya kuch bhi download karne ki bilkul zarurat nahi hai — **sab kuch 100% WhatsApp se handle hoga!**

---

## 🌟 Key Features

1. **🌐 Trending One-Page Responsive Website:**
   - Ultra-modern dark glassmorphism design (Tailwind CSS, clean glow aesthetics, mobile & desktop responsive).
   - Drag & Drop Resume PDF upload.
   - Clean onboarding form (Full Name, WhatsApp Number, GitHub Username, LinkedIn Access Token).

2. **🔒 Multi-User & Data Isolation (Zero Leakage):**
   - Har user ka data alag folder me isolate rehta hai (`data/users/<phone>/profile.json`).
   - Kisi bhi person ka data dusre person se mix nahi hota.

3. **🔔 Admin WhatsApp Notification:**
   - Jab bhi koi naya user website par resume upload karke register karega, **aapke personal WhatsApp par turant alert aayega**:
     - *User Name, Phone, GitHub handle, aur Resume Skills ka summary.*

4. **📱 100% WhatsApp-First Control (No Web / Zero Downloads Needed):**
   - Rozana 3 peak traffic times par bot user ke WhatsApp par draft bhejega.
   - **Approval:** User bas WhatsApp par **`APPROVE`** ya **`YES`** likhega -> Post turant LinkedIn par auto-upload ho jayegi!
   - **Modifications/Changes:** Agar user ko draft me koi change chahiye, toh wo seedhe WhatsApp par likhega (e.g. *"Python code add karo"*, *"Isse short karo"*). Bot AI se rewrite karke naya preview wapas WhatsApp par bhej dega!

5. **🐙 Real GitHub Code Link Integration:**
   - Afternoon Frontend tricks me user ke actual **GitHub profile/repository ka example code link** automatically post ke sath include hoga.

6. **🕒 3 Posts Per Day (Peak Traffic Timing):**
   - **09:00 AM IST (Morning):** UI/UX Design Short Tricks (Figma, XD, Mobile Button Sizes, 8pt Grid).
   - **01:00 PM IST (Afternoon):** Frontend Code Shortcuts (CSS, JS, React) + **User's GitHub Code Link**.
   - **07:00 PM IST (Evening):** Trending AI News & Tool Breakdown.
   - **Weekends:** Interactive Polls, Quizzes & A vs B Challenge.

7. **🗣️ Super Simple English & 10 to 15 Hashtags:**
   - Har post Grade 6 plain English me likhi hoti hai (No heavy words).
   - Niche curated 10-15 trending hashtags automatically aate hain.

---

## 📁 Project Architecture

```text
├── templates/
│   └── index.html            # Trending single-page responsive website
├── services/
│   ├── user_manager.py       # Isolated multi-user storage & state
│   ├── github_service.py     # User GitHub link generator
│   ├── whatsapp_service.py   # Twilio WhatsApp sender, Admin alert, User welcome
│   ├── resume_parser.py      # PDF extraction & Gemini skill analysis
│   ├── post_generator.py     # Simple English 3x daily post generator & refiner
│   ├── image_card_service.py # Auto visual banner card creator
│   └── linkedin_service.py   # LinkedIn official API publisher
├── server.py                 # FastAPI Web Server + WhatsApp Two-Way Webhook
├── cli_auto_runner.py        # Multi-user batch dispatcher for Cron / GitHub Actions
├── app.py                    # Optional Streamlit admin dashboard
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Setup & Run

### 1. Dependencies Install Karein
```bash
pip install -r requirements.txt
```

### 2. Environment Variables (.env) Setup
`.env.example` ko copy karke `.env` banayein:
```bash
cp .env.example .env
```
Aur keys enter karein:
```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_key

# WhatsApp Twilio Sandbox
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# AAPKA WhatsApp number jahan naye users ka alert aayega
ADMIN_WHATSAPP_NUMBER=whatsapp:+91XXXXXXXXXX
```

### 3. Server Start Karein
```bash
python server.py
# Ya uvicorn ke through:
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```
Ab browser me `http://localhost:8000` (ya aapke mobile me `http://<YOUR_IP>:8000`) kholein. Aapko trending single-page onboarding website dikhegi!

---

## 📲 Twilio WhatsApp Webhook Setup (Two-Way Interaction)

Aapke phone se reply aane par bot auto-response de sake, iske liye:
1. Local testing ke liye **ngrok** chalayein:
   ```bash
   ngrok http 8000
   ```
   (Aapko URL milega jaise: `https://abcd-1234.ngrok-free.app`)
2. [Twilio Console](https://console.twilio.com/) > **Messaging > WhatsApp Sandbox Settings** me jayein:
   - **"WHEN A MESSAGE COMES IN"** URL me paste karein:
     `https://abcd-1234.ngrok-free.app/webhook/whatsapp` (HTTP POST)
   - Save click karein.

Ab jab bhi koi WhatsApp par **APPROVE** likhega, bot uske LinkedIn par post upload kar dega! Agar koi edit maangega, bot AI se draft change kar dega.

---

## 📤 GitHub Par Push Karne Ke Commands

```bash
git add .
git commit -m "Add trending one-page website, multi-user isolation, admin WhatsApp alerts, GitHub code link, and two-way WhatsApp approval webhook"
git push origin main
```

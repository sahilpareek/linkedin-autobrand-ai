# 💼 LinkedIn AutoBrand AI Bot (Resume to LinkedIn with WhatsApp Review)

AI-powered tool jo aapke **Resume (PDF)** ko analyze karta hai, aapke actual skills aur projects ke related **engaging LinkedIn posts** generate karta hai, aur **WhatsApp par approval preview** bhejta hai taaki aap mobile se hi review karke direct post ya edits kar sakein!

---

## 🌟 Key Features

1. **🕒 3 Posts Per Day (Peak Traffic Timing):**
   - **🌅 Morning (08:30 - 09:30 AM IST):** UI/UX Design Short Tricks (Figma, Adobe XD, Mobile button sizes, 8pt grid, contrast rules). *Inspired by Behance, Dribbble & Pinterest principles but 100% original.*
   - **☀️ Afternoon (01:00 - 02:00 PM IST):** Frontend Development Short Tricks (CSS magic, JavaScript hacks, React optimization, clean one-liners).
   - **🌙 Evening (06:30 - 07:30 PM IST):** Trending AI News & Tool Breakdown (Major updates, breakthrough models, actionable summaries).
   - **🎉 Weekend Special (Sat & Sun):** Interactive Polls, Quizzes & "A vs B Design/Code Challenge" to get 5x more comments and algorithmic boost!
2. **🗣️ Super Simple English (No Hard Words):**
   - Prompts are strictly tuned for Grade 6 simple conversational English. No heavy vocabulary or hard-to-read academic jargon.
3. **📈 10 to 15 High-Traffic Hashtags:**
   - Every post includes 10-15 targeted hashtags tailored to that specific post topic to maximize reach.
4. **🖼️ Automated Visual Graphic Banner (1080x1080):**
   - Har post ke liye high-res visual card banner generate hota hai jise direct LinkedIn post ke sath attach kiya ja sakta hai.
5. **🛠️ AI On-Demand Refinement:**
   - Agar post me code snippet, tone, ya layout badalna ho, direct feedback dekar 1-click me rewrite karwayein.
6. **📱 WhatsApp Preview & Mobile Streamlit UI:**
   - Phone par WhatsApp message aayega preview ke liye aur mobile-friendly browser UI se approval/changes kar sakte hain.

---

## 📁 Project Structure

```text
├── .github/workflows/
│   └── daily_bot.yml         # GitHub Actions for daily automated run
├── services/
│   ├── __init__.py
│   ├── resume_parser.py      # PDF text extract & Gemini profile analysis
│   ├── post_generator.py     # AI LinkedIn post creation & refinement
│   ├── linkedin_service.py   # LinkedIn Official UGC API posting
│   ├── whatsapp_service.py   # Twilio WhatsApp preview messaging
│   └── storage_service.py    # Local storage for profile & post history
├── app.py                    # Streamlit Web UI (Mobile optimized)
├── cli_auto_runner.py        # CLI script for Cron / GitHub Actions
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

---

## 🚀 Quick Setup Guide

### 1. Repository Clone & Dependencies Install
```bash
# Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# Virtual environment create karein (optional but recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies install karein
pip install -r requirements.txt
```

### 2. Environment Variables (.env) Setup
`.env.example` ko copy karke `.env` banayein:
```bash
cp .env.example .env
```
Aur apni keys enter karein:

```env
# 1. Google Gemini API (https://aistudio.google.com/)
GEMINI_API_KEY=AIzaSy...

# 2. LinkedIn API (https://www.linkedin.com/developers/)
LINKEDIN_ACCESS_TOKEN=AQV...
LINKEDIN_PERSON_URN=urn:li:person:YOUR_ID

# 3. WhatsApp Twilio Sandbox (https://www.twilio.com/console)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
USER_WHATSAPP_NUMBER=whatsapp:+91XXXXXXXXXX
```

---

## 📱 Mobile se Streamlit Kaise Chalayein?

### Option A: Apne Ghar ke Wi-Fi / Hotspot par:
```bash
streamlit run app.py
```
Terminal me `Network URL` dikhega (e.g. `http://192.168.1.15:8501`).
Apne mobile me Wi-Fi on karke wahi URL browser me kholein. Aapka dashboard phone par open ho jayega!

### Option B: Streamlit Community Cloud (Free & 24/7 Mobile Access):
1. GitHub par code push karein.
2. [share.streamlit.io](https://share.streamlit.io/) par jakar repo select karein.
3. Settings me secrets (API keys) add karein.
4. Aapko ek permanent live web link mil jayega jisse aap duniya me kahin se bhi phone se chala sakte hain!

---

## 🔑 API Keys Kaise Milegi?

### 1. Google Gemini API (Free)
1. [Google AI Studio](https://aistudio.google.com/) par jayein.
2. **"Create API Key"** click karein aur copy karein.

### 2. LinkedIn API & Token
1. [LinkedIn Developer Portal](https://www.linkedin.com/developers/) par login karein.
2. **Create App** karein.
3. **Products** tab me jakar:
   - "Share on LinkedIn"
   - "Sign In with LinkedIn using OpenID Connect"
   dono ko add karein.
4. **Auth** tab me jakar Token Generator se access token generate karein with `w_member_social` permission.
5. Apni Person URN nikalne ke liye `https://api.linkedin.com/v2/userinfo` call karein (ya Streamlit app ke sidebar se direct test karein).

### 3. WhatsApp Preview (Twilio Free Sandbox)
1. [Twilio Console](https://www.twilio.com/console) par free account banayein.
2. **Messaging > Try SMS / WhatsApp Sandbox** me jayein.
3. Diye gaye WhatsApp number par sandbox code bhejein (e.g. `join <your-sandbox-word>`).
4. Account SID aur Auth Token copy karke `.env` me paste karein.

---

## ⚙️ GitHub Par Upload Kaise Karein?

Apne terminal me ye commands run karein:

```bash
git init
git add .
git commit -m "Initial commit: LinkedIn AutoBrand AI Bot with Mobile Streamlit UI & WhatsApp Review"

# GitHub par new repository banane ke baad:
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

---

## ⏰ Cloud Automated Daily Posting (GitHub Actions)

Agar aap laptop off hone par bhi rozana subah automated run chahte hain:
1. GitHub Repo ke **Settings > Secrets and variables > Actions** me jayein.
2. New Repository Secrets add karein:
   - `GEMINI_API_KEY`
   - `LINKEDIN_ACCESS_TOKEN`
   - `LINKEDIN_PERSON_URN`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_WHATSAPP_NUMBER`
   - `USER_WHATSAPP_NUMBER`
3. `.github/workflows/daily_bot.yml` har din subah automatically run hokar aapke WhatsApp par preview bhej dega!

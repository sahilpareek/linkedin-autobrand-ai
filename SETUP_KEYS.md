# Keys & deploy — exact steps (5–15 min each)

Copy values into `.env` (local) or Render **Environment** (live).

---

## 1. Gemini API key (posts generate karne ke liye)

1. Open: https://aistudio.google.com/apikey  
2. Google account se login  
3. **Create API key** → copy  
4. Paste:

```env
GEMINI_API_KEY=AIza...
```

---

## 2. Telegram bot (draft + Approve)

1. Telegram pe [@BotFather](https://t.me/BotFather) open karo  
2. `/newbot` → name do → username do (must end with `bot`)  
3. BotFather dega **token** → copy  
4. Bot ko open karke **Start** dabao (ek message bhejo)  
5. Browser mein yeh URL kholo (TOKEN replace karke):

```
https://api.telegram.org/bot<TOKEN>/getUpdates
```

6. JSON mein `"chat":{"id": 123456789` — yeh number `TELEGRAM_CHAT_ID` hai  

```env
TELEGRAM_BOT_TOKEN=123456:AA...
TELEGRAM_BOT_USERNAME=MyAutoBrandBot
TELEGRAM_CHAT_ID=123456789
```

---

## 3. LinkedIn token (auto post ke liye)

LinkedIn ab **Community Management API / Marketing Developer Platform** ke through token deta hai.

### Quick path (owner account)

1. https://www.linkedin.com/developers/apps → **Create app**  
2. Products: **Share on LinkedIn** + **Sign In with LinkedIn using OpenID Connect** request/approve  
3. Auth tab → redirect URL add (e.g. `http://localhost:8000/callback` or `https://your-app.onrender.com/callback`)  
4. OAuth 2.0 scopes: `openid`, `profile`, `w_member_social`  
5. Generate **Access token** (3-legged OAuth). Tools:
   - LinkedIn’s token generator in the app, or  
   - https://www.linkedin.com/developers/tools/oauth/token-generator (if available on your app)  
6. Person URN: call `https://api.linkedin.com/v2/userinfo` with Bearer token → `sub` field, then `urn:li:person:{sub}`

```env
LINKEDIN_ACCESS_TOKEN=AQX...
LINKEDIN_PERSON_URN=urn:li:person:XXXX
```

**Note:** Tokens expire. Multi-user ke liye har user form mein apna token paste kare; owner ke liye `.env` kaafi hai jab Telegram chat_id match kare.

Agar token nahi hai: system **draft Telegram pe bhejega**, Approve pe LinkedIn fail message aayega — post text copy-paste se manually post kar sakte ho.

---

## 4. Server deploy (Render — free tier possible)

1. Code GitHub pe push karo (repo public/private)  
2. https://render.com → **New → Web Service** → connect repo  
3. Settings match `render.yaml`:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. Environment variables add karo (same as `.env` keys above)  
5. Deploy → URL milegi: `https://linkedin-autobrand-ai.onrender.com`  
6. Form upload isi URL pe chalega  

**GitHub Actions** schedule already set hai (`workflows/daily_bot.yml`). Repo secrets mein same keys add karo:
`GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`, `TELEGRAM_CHAT_ID`, optional LinkedIn keys.

---

## 5. Mujhe kya bhejna hai (is chat mein paste)

Bina secrets ke public chat mein full token mat daalo agar concern ho — phir bhi testing ke liye yeh chahiye:

| Item | Example | Required? |
|------|---------|-----------|
| `GEMINI_API_KEY` | `AIza...` | Yes |
| `TELEGRAM_BOT_TOKEN` | `7123...:AA...` | Yes |
| `TELEGRAM_BOT_USERNAME` | `MyAutoBrandBot` | Yes |
| `TELEGRAM_CHAT_ID` | `987654321` | Yes (admin notify + your drafts) |
| `LINKEDIN_ACCESS_TOKEN` | `AQX...` | Optional for auto-post |
| `LINKEDIN_PERSON_URN` | `urn:li:person:...` | Optional with token |
| GitHub repo URL (agar deploy help chahiye) | `https://github.com/you/repo` | For deploy guide |
| Render account hai? | yes/no | Optional |

Keys milte hi main `.env` template fill / verify steps aur health-check bata dunga.

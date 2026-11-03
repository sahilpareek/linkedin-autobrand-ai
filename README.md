# AutoBrand AI

Upload a resume on the website. The bot writes **3 weekday posts** from that resume in **Class 6 English**, sends the draft on **Telegram**, and posts to LinkedIn only after **Approve**. Saturday and Sunday send a quiz or poll. Each user is isolated in their own folder — AI content is always from *their* resume.

## Website (form)

- **Local (full upload + API):** http://localhost:8000  
- **GitHub Pages (UI only; upload needs the Python server):** https://sahilpareek.github.io/linkedin-autobrand-ai/

Deploy the Python app (Render / any host) with `render.yaml`, then point the form `action` to that API if you use static Pages.

## Daily plan (IST)

| When | What |
|---|---|
| Mon–Fri 09:00 | **UI/UX** — button size, dashboard, app/web layout. Pinterest/Dribbble-style banner |
| Mon–Fri 13:00 | **Website** knowledge + GitHub link in the post |
| Mon–Fri 19:00 | **AI news / trending tech** |
| Sat & Sun 11:00 + 17:00 | **Quiz or poll** for comments |

Every post: related page tags (`@Figma`, `@GitHub`, …) + 12–15 top hashtags. Goal = comments/saves so the post can trend.

## Telegram approval flow (you + every user)

1. Fill website form → upload resume PDF.  
2. Open bot link / send `/start CODE`.  
3. Draft + banner arrives on Telegram.  
4. Type changes → draft updates in place.  
5. Tap **Approve** or send `YES` → LinkedIn publish (needs a real LinkedIn access token in the form or owner `.env`).

Same flow for every registered user; their posts never mix.

## Setup

**No Gemini / AI API needed.** Posts use Class-6 English templates + resume skills.

```bash
pip install -r requirements.txt
# .env:
#   TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_USERNAME, TELEGRAM_CHAT_ID
#   LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN
python server.py
```

Create a bot with [@BotFather](https://t.me/BotFather).

```bash
python -m unittest discover -s tests -v
```

## Production schedule

- **GitHub Actions** (`workflows/daily_bot.yml`): Mon–Fri 3 slots + Sat/Sun quiz/poll (UTC crons = IST times above).  
- **In-process** (`server.py` + `schedule`): same slots when the web process stays up (Render free tier may sleep — prefer Actions for reliability).

## Status (feature checklist)

| Feature | Status |
|---|---|
| 3 post types (UI / Website / AI) from resume | Done + tested |
| Class 6 English, tags, 12–15 hashtags | Done |
| Banner (Pinterest/Dribbble style idea) | Done (PNG) |
| Multi-user form + isolated folders | Done + tested |
| Telegram draft → edit → Approve → LinkedIn | Done + tested |
| Sat/Sun quiz & poll | Done + tested |
| GitHub Actions weekend crons | Done |
| IST slot detection | Done |
| Live LinkedIn token per user (real OAuth) | User must paste token in form |
| Always-on host without Actions | Needs paid always-on or external cron |

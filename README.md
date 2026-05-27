# 🤖 AutoFilterBot

A powerful Telegram bot that **indexes, searches, and delivers files** from your channels — with **no auto-deletion** and **24/7 uptime** on Railway / Render / Heroku.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📂 Auto-index | Indexes every file posted in your file channels automatically |
| 🔍 Smart Search | Full-text + regex fallback search |
| 📤 File Delivery | Sends files to users in DM on button tap |
| 🔒 No Auto-Delete | Files are **never** removed automatically |
| 24/7 Uptime | Keep-alive HTTP server prevents platform sleep |
| 👑 Admin Tools | `/index`, `/delete`, `/broadcast`, `/stats` |

---

## 🚀 Setup Guide

### Step 1 — Prerequisites

1. **Telegram API credentials** → [my.telegram.org](https://my.telegram.org)
   - `API_ID` and `API_HASH`

2. **Bot Token** → Talk to [@BotFather](https://t.me/BotFather)
   - Create a new bot → copy the token

3. **MongoDB Atlas** (free) → [cloud.mongodb.com](https://cloud.mongodb.com)
   - Create a free cluster → copy the connection URI

4. **Your User ID** → Talk to [@userinfobot](https://t.me/userinfobot)

---

### Step 2 — Channel Setup

1. Create a **private channel** where you'll post/store files
2. Add the bot as **Admin** with these permissions:
   - ✅ Post messages
   - ✅ Edit messages
   - ✅ Delete messages (for manual deletes)
3. Copy the channel ID (starts with `-100...`)

---

### Step 3 — Deploy to Railway (Recommended)

1. Fork or upload this repo to GitHub

2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**

3. Select your repo

4. In **Variables**, add all these:

```
API_ID          = 12345678
API_HASH        = your_api_hash
BOT_TOKEN       = 123456789:AAxxxxxxx
MONGO_URI       = mongodb+srv://...
DB_NAME         = autofilterbot
FILE_CHANNEL    = -1001234567890
LOG_CHANNEL     = -1009876543210
ADMINS          = 123456789
MAX_RESULTS     = 10
```

5. Railway auto-deploys. Your bot is live 24/7! ✅

---

### Deploy to Render

1. Go to [render.com](https://render.com) → **New Web Service**
2. Connect your GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python bot.py`
5. Add all environment variables from the table above

---

### Deploy to Heroku

```bash
heroku create your-autofilterbot
heroku config:set API_ID=... API_HASH=... BOT_TOKEN=... MONGO_URI=...
git push heroku main
heroku ps:scale web=1
```

---

## 📖 Bot Commands

### User Commands
| Command | Description |
|---|---|
| `/start` | Welcome message + help buttons |
| `/help` | Full command list |

### Admin Commands
| Command | Description |
|---|---|
| `/stats` | Total files, users, bot status |
| `/total` | Number of indexed files |
| `/index -100xxxxxxxxx` | Bulk-index all files from a channel |
| `/delete` | Reply to a result → removes from index |
| `/broadcast` | Reply to a message → sends to all users |

---

## 🔍 How Search Works

1. A user types a movie/file name in the group
2. The bot searches MongoDB (full-text first, then regex)
3. Results appear as inline buttons (up to 10)
4. User taps a button → file is sent to their DM instantly

---

## 🏗️ Project Structure

```
autofilterbot/
├── bot.py              ← Entry point, Pyrogram client
├── config.py           ← All configuration from env vars
├── requirements.txt
├── Procfile            ← Heroku/Railway process declaration
├── railway.toml        ← Railway-specific config
├── render.yaml         ← Render-specific config
├── database/
│   └── db.py           ← MongoDB operations (save, search, delete)
├── handlers/
│   ├── start.py        ← /start, /help, callbacks
│   ├── search.py       ← Auto-filter search + file delivery
│   ├── indexer.py      ← Auto-index channel files + /index
│   └── admin.py        ← Admin commands
└── utils/
    └── keep_alive.py   ← aiohttp server for 24/7 uptime
```

---

## ⚠️ Important Notes

- **AUTO_DELETE is set to `False`** — files are never deleted automatically
- The bot must be **admin** in your file channel(s)
- Users must **start the bot in DM** before receiving files
- For bulk indexing large channels, use `/index` once after setup

---

## 🛠️ Local Development

```bash
git clone <your-repo>
cd autofilterbot
pip install -r requirements.txt
cp .env.example .env
# Fill in your .env values
python bot.py
```

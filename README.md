# 🐯 Team Tigers Files Bot

A powerful Telegram AutoFilter Bot with premium features, built for 24/7 uptime.

---

## ⚙️ Environment Variables — Full Reference

### 📋 Complete Variable List

```env
# ── Telegram Credentials ──────────────────────────────────────
API_ID=20262762
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here

# ── MongoDB ───────────────────────────────────────────────────
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/autofilterbot?retryWrites=true&w=majority
DB_NAME=autofilterbot

# ── Admins (comma separated if multiple) ─────────────────────
# Single admin:
ADMINS=123456789
# Multiple admins:
ADMINS=123456789,987654321,456789123

# ── File Channel (comma separated if multiple) ────────────────
# Single channel:
FILE_CHANNEL=-1001234567890
# Multiple channels:
FILE_CHANNEL=-1001234567890,-1009876543210

# ── Log Channel ───────────────────────────────────────────────
LOG_CHANNEL=-1001234567890

# ── Force Subscribe Channels (comma separated) ────────────────
# Single fsub channel:
FORCE_SUB_CHANNELS=-1001234567890
# Multiple fsub channels:
FORCE_SUB_CHANNELS=-1001234567890,-1009876543210
# Disable fsub (leave empty):
FORCE_SUB_CHANNELS=

# ── URL Shortener ─────────────────────────────────────────────
SHORTENER_API=your_shortener_api_key
SHORTENER_SITE=mdisklink.com
# Disable shortener (leave empty):
SHORTENER_API=
SHORTENER_SITE=

# ── Stream Server ─────────────────────────────────────────────
STREAM_BASE_URL=https://stream.yoursite.com
# Disable streaming (leave empty):
STREAM_BASE_URL=

# ── UPI Payment ───────────────────────────────────────────────
UPI_ID=yourname@upi
UPI_NAME=Team Tigers

# ── Bot Settings ──────────────────────────────────────────────
MAX_RESULTS=10
DEPLOY_SERVER=Railway
```

---

## 🆔 How to Get Channel/Group IDs

### Method 1 — Forward to @userinfobot
1. Forward any message from your channel/group to [@userinfobot](https://t.me/userinfobot)
2. It will show the chat ID

### Method 2 — Add @RawDataBot
1. Add [@RawDataBot](https://t.me/RawDataBot) to your group/channel
2. It will show the chat ID automatically

### Method 3 — Telegram Web
1. Open [web.telegram.org](https://web.telegram.org)
2. Open your channel/group
3. The URL will show the ID: `https://web.telegram.org/k/#-1001234567890`
4. The ID is `-1001234567890`

> ⚠️ Channel/Group IDs always start with `-100`

---

## 🖼️ Start Image / Welcome Photo

To show a photo when users send `/start`, add this variable:

```env
START_IMAGE=https://telegra.ph/your-image-url.jpg
```

### How to get a Telegra.ph image URL:
1. Go to [telegra.ph](https://telegra.ph)
2. Click the photo icon → upload your image
3. Right-click the uploaded image → Copy image address
4. Use that URL as `START_IMAGE`

### Update start.py to use START_IMAGE:
```python
# In Config class (config.py):
START_IMAGE = os.environ.get("START_IMAGE", "")

# In start.py start_handler:
if Config.START_IMAGE:
    await message.reply_photo(
        photo=Config.START_IMAGE,
        caption=text,
        reply_markup=buttons
    )
else:
    await message.reply_text(text, reply_markup=buttons)
```

---

## 📢 Force Subscribe Setup

### In Environment Variables:
```env
# One channel:
FORCE_SUB_CHANNELS=-1001234567890

# Multiple channels:
FORCE_SUB_CHANNELS=-1001234567890,-1009876543210
```

### Requirements:
- Bot must be **Admin** in the fsub channel
- Bot needs **Invite Users via Link** permission
- Use the channel's numeric ID (starts with -100)

### Channel Link Formats:
```
# Public channel:
https://t.me/yourchannelusername

# Private channel (use invite link):
https://t.me/+AbCdEfGhIjKlMnOp
```

---

## 📊 Log Channel Setup

```env
LOG_CHANNEL=-1001234567890
```

- Create a private channel for logs
- Add bot as Admin
- Copy the channel ID

---

## 🚀 Deploy Guides

---

### 🟣 Deploy to Koyeb

1. Create account at [koyeb.com](https://koyeb.com)
2. New App → **GitHub** → select your repo
3. Configure:
   - **Builder:** Dockerfile
   - **Run command:** `python bot.py`
   - **Port:** `8080`
4. Add all environment variables
5. Deploy!

**koyeb.toml** (add to repo root):
```toml
[build]
builder = "docker"

[run]
command = "python bot.py"

[[services]]
name = "teamtigersbot"
ports = [{port = 8080, protocol = "http"}]
```

---

### 🔵 Deploy to Vercel

> ⚠️ Vercel is for web apps — NOT recommended for Telegram bots (no persistent process). Use only if you set up webhook mode.

**vercel.json:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "bot.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "bot.py"
    }
  ]
}
```

---

### 🟠 Deploy to Heroku

**Step 1 — Install Heroku CLI:**
```bash
# Download from: https://devcenter.heroku.com/articles/heroku-cli
```

**Step 2 — Login & Create App:**
```bash
heroku login
heroku create your-team-tigers-bot
```

**Step 3 — Set Environment Variables:**
```bash
heroku config:set API_ID=20262762
heroku config:set API_HASH=your_api_hash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set MONGO_URI=your_mongo_uri
heroku config:set DB_NAME=autofilterbot
heroku config:set FILE_CHANNEL=-1001234567890
heroku config:set ADMINS=123456789
heroku config:set MAX_RESULTS=10
heroku config:set DEPLOY_SERVER=Heroku
```

**Step 4 — Deploy:**
```bash
git init
git add .
git commit -m "Initial deploy"
git push heroku main
heroku ps:scale worker=1
```

**Procfile** (already in repo):
```
worker: python bot.py
```

---

### 🟡 Deploy to Railway

**Step 1:** Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub

**Step 2:** Add variables in Railway dashboard

**Step 3:** railway.toml (already in repo):
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python bot.py"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

---

### 🟢 Deploy to Render

**Step 1:** Go to [render.com](https://render.com) → New Web Service

**Step 2:** Connect GitHub repo

**Step 3:** Configure:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python bot.py`

**Step 4:** Add all environment variables

**render.yaml** (already in repo):
```yaml
services:
  - type: web
    name: autofilterbot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python bot.py
```

---

### 🐳 Deploy with Docker

```bash
# Build image
docker build -t teamtigersbot .

# Run container
docker run -d \
  -e API_ID=20262762 \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  -e MONGO_URI=your_mongo_uri \
  -e DB_NAME=autofilterbot \
  -e FILE_CHANNEL=-1001234567890 \
  -e ADMINS=123456789 \
  -e MAX_RESULTS=10 \
  --name teamtigersbot \
  teamtigersbot
```

---

### 💻 Run Locally

```bash
git clone https://github.com/yourusername/Team-Tigers-Files-Bot
cd Team-Tigers-Files-Bot
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
python bot.py
```

---

## 📖 Bot Commands

### User Commands
| Command | Description |
|---|---|
| `/start` | Welcome message |
| `/help` | Command list |
| `/premium` | View & buy premium plans |
| `/mystatus` | Check premium status |

### Admin Commands
| Command | Description |
|---|---|
| `/stats` | Bot statistics |
| `/index -100xxxxxxxxx` | Bulk-index a channel |
| `/total` | Total indexed files |
| `/delete` | Remove file from index |
| `/addpremium <user_id> <plan>` | Grant premium |
| `/rmpremium <user_id>` | Remove premium |
| `/approve <req_id>` | Approve payment |
| `/pending` | List pending payments |
| `/broadcast` | Broadcast to all users |
| `/premiumlist` | List premium users |

---

## 🏗️ Project Structure

```
Team-Tigers-Files-Bot/
├── bot.py              ← Entry point
├── config.py           ← Configuration
├── requirements.txt    ← Dependencies
├── Procfile            ← Heroku/Railway
├── railway.toml        ← Railway config
├── render.yaml         ← Render config
├── Dockerfile          ← Docker/Back4App
├── .env.example        ← Environment template
├── README.md
├── database/
│   ├── __init__.py
│   └── db.py           ← MongoDB operations
├── handlers/
│   ├── __init__.py
│   ├── start.py        ← /start, /help
│   ├── search.py       ← Auto-filter search
│   ├── admin.py        ← Admin commands
│   ├── premium.py      ← Premium system
│   └── indexer.py      ← File indexer
└── utils/
    ├── __init__.py
    ├── fsub.py         ← Force subscribe
    ├── keep_alive.py   ← 24/7 uptime
    └── shortener.py    ← URL shortener
```

---

## ⚠️ Important Notes

- Bot must be **Admin** in file channel(s) with Post/Edit/Delete permissions
- Bot must be **Admin** in fsub channel(s) with Invite Users permission
- Users must **start the bot in DM** before receiving files
- Files are **NEVER auto-deleted**
- Run `/index -100xxxxxxxxx` once after setup to bulk-index existing files

---

*🐯 Team Tigers — Your trusted source for Movies, Series & Entertainment*

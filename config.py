import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Telegram Credentials ──────────────────────────────────────
    API_ID       = int(os.environ.get("API_ID", 0))
    API_HASH     = os.environ.get("API_HASH", "")
    BOT_TOKEN    = os.environ.get("BOT_TOKEN", "")

    # ── Bot Identity ──────────────────────────────────────────────
    BOT_NAME         = "Team Tigers Files Bot"
    BOT_USERNAME     = "@Team_Tigerss_filessbot"
    CHANNEL_USERNAME = "@Team_Tigerss"
    CHANNEL_URL      = "https://t.me/Team_Tigerss"
    DEPLOY_SERVER    = os.environ.get("DEPLOY_SERVER", "Back4App")
    LANGUAGE         = "Python 3 + Pyrogram"

    # ── MongoDB ───────────────────────────────────────────────────
    MONGO_URI    = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME      = os.environ.get("DB_NAME", "autofilterbot")

    # ── Channels / Groups ─────────────────────────────────────────
    FILE_CHANNEL = [
        int(ch.strip())
        for ch in os.environ.get("FILE_CHANNEL", "").split(",")
        if ch.strip()
    ]
    LOG_CHANNEL  = int(os.environ.get("LOG_CHANNEL", 0))
    ADMINS       = [
        int(a.strip())
        for a in os.environ.get("ADMINS", "").split(",")
        if a.strip()
    ]

    # ── Force Subscribe ───────────────────────────────────────────
    FORCE_SUB_CHANNELS = [
        int(ch.strip())
        for ch in os.environ.get("FORCE_SUB_CHANNELS", "").split(",")
        if ch.strip()
    ]

    # ── URL Shortener (for non-premium users) ─────────────────────
    SHORTENER_API   = os.environ.get("SHORTENER_API", "")
    SHORTENER_SITE  = os.environ.get("SHORTENER_SITE", "")
    USE_SHORTENER   = bool(os.environ.get("SHORTENER_API", ""))

    # ── Online Watch / Stream ─────────────────────────────────────
    STREAM_BASE_URL = os.environ.get("STREAM_BASE_URL", "")

    # ── Premium Plans ─────────────────────────────────────────────
    PREMIUM_PLANS = {
        "weekly":  {"price": 25,  "days": 7,  "label": "Weekly  — ₹25"},
        "monthly": {"price": 350, "days": 30, "label": "Monthly — ₹350"},
    }
    UPI_ID       = os.environ.get("UPI_ID", "yourname@upi")
    UPI_NAME     = os.environ.get("UPI_NAME", "Team Tigers")

    # ── Behaviour ─────────────────────────────────────────────────
    MAX_RESULTS  = int(os.environ.get("MAX_RESULTS", 10))
    AUTO_DELETE  = False

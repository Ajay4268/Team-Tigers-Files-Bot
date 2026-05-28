import asyncio
import logging
import os
from pyrogram import Client, idle
from config import Config
from database.db import Database
from utils.keep_alive import keep_alive

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logger.info(f"🔍 API_ID      : {Config.API_ID}")
logger.info(f"🔍 API_HASH    : {Config.API_HASH[:6]}...")
logger.info(f"🔍 BOT_TOKEN   : {Config.BOT_TOKEN[:10]}...")
logger.info(f"🔍 MONGO_URI   : {Config.MONGO_URI[:30]}...")
logger.info(f"🔍 ADMINS      : {Config.ADMINS}")
logger.info(f"🔍 FILE_CHANNEL: {Config.FILE_CHANNEL}")

# Check handlers folder
handlers_path = os.path.join(os.path.dirname(__file__), "handlers")
logger.info(f"🔍 Handlers exists: {os.path.exists(handlers_path)}")
logger.info(f"🔍 Handlers files : {os.listdir(handlers_path) if os.path.exists(handlers_path) else 'NOT FOUND'}")

# Initialize Pyrogram client
app = Client(
    "AutoFilterBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="handlers")
)

async def main():
    try:
        keep_alive()
        logger.info("✅ Keep-alive web server started on port 8080")

        logger.info("⏳ Connecting to MongoDB...")
        db = Database()
        await db.connect()
        logger.info("✅ Database connected")

        logger.info("⏳ Starting Pyrogram client...")
        await app.start()
        me = await app.get_me()
        logger.info(f"✅ Bot started as @{me.username}")
        logger.info(f"✅ Bot ID: {me.id}")
        logger.info(f"✅ Listening for messages...")

        await idle()
        await app.stop()
        logger.info("Bot stopped.")

    except Exception as e:
        logger.error(f"❌ FATAL ERROR: {type(e).__name__}: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())

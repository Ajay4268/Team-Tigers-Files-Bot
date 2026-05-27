import asyncio
import logging
from pyrogram import Client, idle
from config import Config
from database.db import Database
from utils.keep_alive import keep_alive

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Pyrogram client
app = Client(
    "AutoFilterBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="handlers")
)

async def main():
    # Start the HTTP keep-alive server (required for Railway/Render/Heroku)
    keep_alive()
    logger.info("✅ Keep-alive web server started on port 8080")

    db = Database()
    await db.connect()
    logger.info("✅ Database connected")

    await app.start()
    me = await app.get_me()
    logger.info(f"✅ Bot started as @{me.username}")

    # Keep alive forever
    await idle()
    await app.stop()
    logger.info("Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main())

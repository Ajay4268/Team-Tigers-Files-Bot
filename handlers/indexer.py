import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import Database
from config import Config

logger = logging.getLogger(__name__)
db = Database()

# File types to index
FILE_FILTER = filters.document | filters.video | filters.audio | filters.photo

def channel_filter(_, __, message: Message) -> bool:
    """Accept messages only from configured file channels."""
    return message.chat.id in Config.FILE_CHANNEL

channel_files = filters.create(channel_filter)

@Client.on_message(channel_files & FILE_FILTER)
async def index_file(client: Client, message: Message):
    """Auto-index every file posted in the file channel(s)."""
    file_obj = (
        message.document or
        message.video    or
        message.audio    or
        message.photo
    )
    if not file_obj:
        return

    # Determine file name
    file_name = getattr(file_obj, "file_name", None) or \
                getattr(file_obj, "title", None) or \
                f"file_{file_obj.file_unique_id}"

    caption = message.caption or ""

    file_data = {
        "file_id"        : file_obj.file_id,
        "file_unique_id" : file_obj.file_unique_id,
        "file_name"      : file_name,
        "caption"        : caption,
        "file_type"      : message.media.value,
        "file_size"      : getattr(file_obj, "file_size", 0),
        "message_id"     : message.id,
        "channel_id"     : message.chat.id,
    }

    saved = await db.save_file(file_data)
    if saved:
        logger.info(f"✅ Indexed: {file_name}")
    else:
        logger.debug(f"⏩ Duplicate (skipped): {file_name}")


# ── Admin: /index command to manually bulk-index a channel ──────────────────

@Client.on_message(filters.command("index") & filters.user(Config.ADMINS))
async def manual_index(client: Client, message: Message):
    """
    Usage:
      /index <channel_id>    — bulk index all media from that channel
    """
    if len(message.command) < 2:
        return await message.reply("Usage: `/index -100xxxxxxxxxx`")

    try:
        channel_id = int(message.command[1])
    except ValueError:
        return await message.reply("❌ Invalid channel ID.")

    status_msg = await message.reply("⏳ Indexing... please wait.")
    count = 0
    skipped = 0

    async for msg in client.get_chat_history(channel_id):
        file_obj = msg.document or msg.video or msg.audio or msg.photo
        if not file_obj:
            continue

        file_name = getattr(file_obj, "file_name", None) or \
                    getattr(file_obj, "title", None) or \
                    f"file_{file_obj.file_unique_id}"

        file_data = {
            "file_id"        : file_obj.file_id,
            "file_unique_id" : file_obj.file_unique_id,
            "file_name"      : file_name,
            "caption"        : msg.caption or "",
            "file_type"      : msg.media.value,
            "file_size"      : getattr(file_obj, "file_size", 0),
            "message_id"     : msg.id,
            "channel_id"     : msg.chat.id,
        }

        saved = await db.save_file(file_data)
        if saved:
            count += 1
        else:
            skipped += 1

        # Update status every 100 files
        if (count + skipped) % 100 == 0:
            await status_msg.edit(
                f"⏳ Indexing...\n✅ Added: `{count}`\n⏩ Skipped: `{skipped}`"
            )

    await status_msg.edit(
        f"✅ **Indexing complete!**\n\n"
        f"📂 New files added : `{count}`\n"
        f"⏩ Already indexed : `{skipped}`"
    )

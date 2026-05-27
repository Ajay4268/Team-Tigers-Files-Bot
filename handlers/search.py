import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from config import Config
from utils.fsub import check_fsub
from utils.shortener import shorten_url

logger = logging.getLogger(__name__)
db = Database()

def is_group(_, __, message: Message) -> bool:
    return message.chat.type in ("group", "supergroup")

group_filter = filters.create(is_group)

SKIP_COMMANDS = ["start","help","stats","index","total","delete",
                 "premium","mystatus","addpremium","rmpremium","approve","pending","broadcast"]

@Client.on_message(group_filter & filters.text & ~filters.command(SKIP_COMMANDS))
async def auto_filter(client: Client, message: Message):
    query = message.text.strip()
    if len(query) < 3:
        return

    results = await db.search_files(query, max_results=Config.MAX_RESULTS)
    if not results:
        await message.reply_text(
            f"❌ No results for **{query}**\n\nTry different keywords.",
            quote=True
        )
        return

    buttons = []
    for file in results:
        name  = file["file_name"]
        label = f"📁 {name[:48]}{'…' if len(name) > 48 else ''}"
        buttons.append([
            InlineKeyboardButton(label, callback_data=f"send_{file['file_unique_id']}")
        ])

    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])

    await message.reply_text(
        f"🔍 **{Config.BOT_NAME}**\n\n"
        f"Found **{len(results)}** result(s) for `{query}`\n"
        f"👇 Tap a file to receive it in your DM:",
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )


@Client.on_callback_query(filters.regex(r"^send_(.+)$"))
async def send_file_callback(client: Client, callback_query):
    # ── Force Subscribe Gate ──
    if not await check_fsub(client, callback_query):
        return

    file_unique_id = callback_query.matches[0].group(1)
    user           = callback_query.from_user

    file_data = await db.get_file_by_id(file_unique_id)
    if not file_data:
        await callback_query.answer("❌ File not found in index!", show_alert=True)
        return

    is_premium_user = await db.is_premium(user.id)
    await callback_query.answer("📤 Sending to your DM...", show_alert=False)

    # ── Build inline keyboard for the sent file ──
    file_buttons = []

    # Online Watch button (if stream server configured)
    if Config.STREAM_BASE_URL:
        stream_url = f"{Config.STREAM_BASE_URL.rstrip('/')}/{file_data['file_unique_id']}"
        if not is_premium_user and Config.USE_SHORTENER:
            stream_url = await shorten_url(stream_url)
        file_buttons.append([
            InlineKeyboardButton("🎬 Watch Online", url=stream_url)
        ])

    # For non-premium: wrap a "get file" link through shortener
    if not is_premium_user and Config.USE_SHORTENER:
        # Create a deep link to the bot that delivers the file
        deep_link = f"https://t.me/{Config.BOT_USERNAME.lstrip('@')}?start=file_{file_unique_id}"
        short_link = await shorten_url(deep_link)
        file_buttons.append([
            InlineKeyboardButton("📥 Get File (via link)", url=short_link)
        ])
        file_buttons.append([
            InlineKeyboardButton("💎 Get Direct — Upgrade Premium", callback_data="premium_plans")
        ])

    kb = InlineKeyboardMarkup(file_buttons) if file_buttons else None

    try:
        await client.copy_message(
            chat_id      = user.id,
            from_chat_id = file_data["channel_id"],
            message_id   = file_data["message_id"],
            reply_markup = kb,
        )
        await db.add_user(user.id)

        # For non-premium without shortener, still nudge upgrade
        if not is_premium_user and not Config.USE_SHORTENER:
            await client.send_message(
                user.id,
                "💎 **Upgrade to Premium** for ad-free file delivery!\n"
                f"Weekly ₹25 | Monthly ₹350\n\n/premium",
            )

    except Exception as e:
        logger.warning(f"Could not send file to {user.id}: {e}")
        await callback_query.answer(
            "⚠️ Start me in DM first, then tap again.",
            show_alert=True
        )


@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()

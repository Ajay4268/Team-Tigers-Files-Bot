import logging
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from database.db import Database
from config import Config
from utils.fsub import check_fsub

logger = logging.getLogger(__name__)
db = Database()

# ── /start ────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    logger.info(f"📩 /start received from user {message.from_user.id}")

    if not await check_fsub(client, message):
        logger.info(f"❌ User {message.from_user.id} failed fsub check")
        return

    await db.add_user(message.from_user.id)
    user = message.from_user
    logger.info(f"✅ Sending welcome to {user.first_name}")

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 Online Watch", callback_data="watch_info"),
            InlineKeyboardButton("ℹ️ About",        callback_data="about"),
        ],
        [
            InlineKeyboardButton("💎 Premium Plans", callback_data="premium_plans"),
            InlineKeyboardButton("📊 Stats",          callback_data="stats"),
        ],
        [
            InlineKeyboardButton("📢 Our Channel", url=Config.CHANNEL_URL),
            InlineKeyboardButton("➕ Add to Group",
                url=f"https://t.me/{Config.BOT_USERNAME.lstrip('@')}?startgroup=true"),
        ],
    ])

    try:
        channel = await client.get_chat(Config.CHANNEL_USERNAME)
        photo   = channel.photo.big_file_id if channel.photo else None
    except Exception as e:
        logger.warning(f"Could not get channel photo: {e}")
        photo = None

    text = (
        f"👋 Hello **{user.first_name}**!\n\n"
        f"I am a 🐯 **Team Tigers** AutoFilter Bot with **advanced features**.\n"
        f"Add me to your group and get 🎬 Movies & 📺 Series instantly!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔍 **Search** any movie/series name in your group\n"
        f"📤 **Get files** delivered to your DM instantly\n"
        f"🎬 **Watch online** without downloading\n"
        f"💎 **Premium** — Ad-free experience\n"
        f"🔒 Files are **never deleted** — always available\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Use /help to see all commands."
    )

    if photo:
        await message.reply_photo(photo=photo, caption=text, reply_markup=buttons)
    else:
        await message.reply_text(text, reply_markup=buttons)


# ── fsub re-check after joining ───────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^fsub_check$"))
async def fsub_recheck(client: Client, callback_query: CallbackQuery):
    if not await check_fsub(client, callback_query):
        return

    user = callback_query.from_user
    await db.add_user(user.id)

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 Online Watch", callback_data="watch_info"),
            InlineKeyboardButton("ℹ️ About",        callback_data="about"),
        ],
        [
            InlineKeyboardButton("💎 Premium Plans", callback_data="premium_plans"),
            InlineKeyboardButton("📊 Stats",          callback_data="stats"),
        ],
        [
            InlineKeyboardButton("📢 Our Channel", url=Config.CHANNEL_URL),
            InlineKeyboardButton("➕ Add to Group",
                url=f"https://t.me/{Config.BOT_USERNAME.lstrip('@')}?startgroup=true"),
        ],
    ])

    text = (
        f"✅ **Verified!** Welcome, **{user.first_name}**!\n\n"
        f"I am a 🐯 **Team Tigers** AutoFilter Bot with **advanced features**.\n"
        f"Add me to your group and get 🎬 Movies & 📺 Series instantly!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔍 **Search** any movie/series name in your group\n"
        f"📤 **Get files** delivered to your DM instantly\n"
        f"🎬 **Watch online** without downloading\n"
        f"💎 **Premium** — Ad-free experience\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Use /help to see all commands."
    )

    try:
        await callback_query.message.edit_text(text, reply_markup=buttons)
    except Exception:
        await callback_query.message.reply_text(text, reply_markup=buttons)


# ── About button ──────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^about$"))
async def about_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Channel", url=Config.CHANNEL_URL)],
        [InlineKeyboardButton("🔙 Back",    callback_data="back_home")],
    ])
    await callback_query.message.edit_text(
        f"ℹ️ **About {Config.BOT_NAME}**\n\n"
        f"🤖 **Bot Name  :** {Config.BOT_NAME}\n"
        f"📛 **Username  :** {Config.BOT_USERNAME}\n"
        f"📢 **Channel   :** {Config.CHANNEL_USERNAME}\n"
        f"🖥️ **Server    :** {Config.DEPLOY_SERVER}\n"
        f"💻 **Language  :** {Config.LANGUAGE}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🐯 **Team Tigers** — Your trusted source for\n"
        f"Movies, Series & Entertainment 🎬\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔒 No auto-delete | 24/7 online | Fast delivery",
        reply_markup=buttons
    )


# ── Online Watch info ─────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^watch_info$"))
async def watch_info_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_home")],
    ])
    await callback_query.message.edit_text(
        "🎬 **Online Watch / Stream**\n\n"
        "You can watch movies & series **directly online** without downloading!\n\n"
        "**How it works:**\n"
        "• Search for any movie/series in the group\n"
        "• Tap the result button\n"
        "• A **🎬 Watch Online** button will appear alongside the file\n"
        "• Click it to stream instantly in your browser\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 **Tip:** Premium users get ad-free streaming!\n"
        "Use /premium to upgrade.",
        reply_markup=buttons
    )


# ── Stats button ──────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^stats$"))
async def cb_stats(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    total_files   = await db.total_files()
    total_users   = await db.total_users()
    total_premium = await db.total_premium_users()
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_home")],
    ])
    await callback_query.message.edit_text(
        f"📊 **{Config.BOT_NAME} — Stats**\n\n"
        f"📂 Indexed Files   : `{total_files}`\n"
        f"👥 Total Users     : `{total_users}`\n"
        f"💎 Premium Users   : `{total_premium}`\n"
        f"🖥️ Server          : {Config.DEPLOY_SERVER}\n"
        f"🤖 Status          : Running 24/7 ✅",
        reply_markup=buttons
    )


# ── How to Search button ──────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^help_search$"))
async def cb_help(client, callback_query):
    await callback_query.answer()
    await callback_query.message.reply_text(
        "🔍 **How to Search:**\n\n"
        "1. Add me to your group\n"
        "2. Type any movie/file name\n"
        "3. I'll show results as inline buttons\n"
        "4. Click a button — I'll send the file to your DM!\n\n"
        "Start me in DM first: /start"
    )


# ── Back to home ──────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^back_home$"))
async def back_home(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    user = callback_query.from_user
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 Online Watch", callback_data="watch_info"),
            InlineKeyboardButton("ℹ️ About",        callback_data="about"),
        ],
        [
            InlineKeyboardButton("💎 Premium Plans", callback_data="premium_plans"),
            InlineKeyboardButton("📊 Stats",          callback_data="stats"),
        ],
        [
            InlineKeyboardButton("📢 Our Channel", url=Config.CHANNEL_URL),
            InlineKeyboardButton("➕ Add to Group",
                url=f"https://t.me/{Config.BOT_USERNAME.lstrip('@')}?startgroup=true"),
        ],
    ])
    await callback_query.message.edit_text(
        f"👋 Welcome back, **{user.first_name}**!\n\n"
        f"I am a 🐯 **Team Tigers** AutoFilter Bot with **advanced features**.\n"
        f"Add me to your group and get 🎬 Movies & 📺 Series instantly!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔍 Search | 📤 Get files | 🎬 Watch online | 💎 Premium\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        reply_markup=buttons
    )


# ── /help command ─────────────────────────────────────────────────────────────

@Client.on_message(filters.command("help"))
async def help_handler(client: Client, message: Message):
    logger.info(f"📩 /help received from user {message.from_user.id}")
    if not await check_fsub(client, message):
        return
    await message.reply_text(
        f"📖 **{Config.BOT_NAME} — Commands**\n\n"
        "**User Commands:**\n"
        "/start   — Welcome message\n"
        "/help    — This help message\n"
        "/premium — View & buy premium plans\n"
        "/mystatus — Check your premium status\n\n"
        "**Admin Commands:**\n"
        "/stats   — Bot statistics\n"
        "/index   — Bulk-index a channel\n"
        "/total   — Total indexed files\n"
        "/delete  — Remove file from index\n"
        "/addpremium <user_id> <plan> — Grant premium\n"
        "/rmpremium <user_id>         — Remove premium\n"
        "/approve <req_id>            — Approve payment\n"
        "/pending                     — List pending payments\n"
        "/broadcast — Broadcast a message\n\n"
        "⚠️ Files are NEVER auto-deleted."
    )

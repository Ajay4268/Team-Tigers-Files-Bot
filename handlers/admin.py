from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from database.db import Database
from config import Config

db = Database()

@Client.on_message(filters.command("stats") & filters.user(Config.ADMINS))
async def stats_handler(client: Client, message: Message):
    total_files   = await db.total_files()
    total_users   = await db.total_users()
    total_premium = await db.total_premium_users()
    await message.reply_text(
        f"📊 **{Config.BOT_NAME} — Statistics**\n\n"
        f"📂 Indexed Files   : `{total_files}`\n"
        f"👥 Total Users     : `{total_users}`\n"
        f"💎 Premium Users   : `{total_premium}`\n"
        f"🖥️ Server          : {Config.DEPLOY_SERVER}\n"
        f"🤖 Status          : Running 24/7 ✅\n"
        f"🗑️ Auto Delete     : **Disabled** ✅"
    )

@Client.on_message(filters.command("total") & filters.user(Config.ADMINS))
async def total_files_handler(client: Client, message: Message):
    total = await db.total_files()
    await message.reply_text(f"📂 Total indexed files: `{total}`")

@Client.on_message(filters.command("delete") & filters.user(Config.ADMINS) & filters.reply)
async def delete_file_handler(client: Client, message: Message):
    replied = message.reply_to_message
    if not replied or not replied.reply_markup:
        return await message.reply("❌ Reply to a file result message.")
    try:
        cb_data        = replied.reply_markup.inline_keyboard[0][0].callback_data
        file_unique_id = cb_data.replace("send_", "")
    except (IndexError, AttributeError):
        return await message.reply("❌ Could not extract file ID.")
    deleted = await db.delete_file(file_unique_id)
    await message.reply("✅ Removed from index." if deleted else "❌ File not found.")

# ── Premium Management ────────────────────────────────────────────────────────

@Client.on_message(filters.command("addpremium") & filters.user(Config.ADMINS))
async def add_premium_cmd(client: Client, message: Message):
    """Usage: /addpremium <user_id> <weekly|monthly>"""
    parts = message.command
    if len(parts) != 3:
        return await message.reply("Usage: `/addpremium <user_id> <weekly|monthly>`")
    try:
        user_id = int(parts[1])
        plan    = parts[2].lower()
    except ValueError:
        return await message.reply("❌ Invalid user ID.")
    if plan not in Config.PREMIUM_PLANS:
        return await message.reply("❌ Invalid plan. Use `weekly` or `monthly`.")

    doc = await db.add_premium(user_id, plan)
    exp = doc["expires_at"].strftime("%d %b %Y")
    await message.reply(
        f"✅ **Premium Granted!**\n\n"
        f"👤 User  : `{user_id}`\n"
        f"📦 Plan  : **{plan.capitalize()}**\n"
        f"📅 Expires: **{exp}**"
    )
    # Notify the user
    try:
        await client.send_message(
            user_id,
            f"🎉 **Congratulations!** Your premium is now active!\n\n"
            f"📦 Plan    : **{plan.capitalize()}**\n"
            f"📅 Expires : **{exp}**\n\n"
            f"✅ You now enjoy **ad-free** file delivery!\n"
            f"Thank you for supporting {Config.BOT_NAME} 🐯"
        )
    except Exception:
        pass

@Client.on_message(filters.command("rmpremium") & filters.user(Config.ADMINS))
async def rm_premium_cmd(client: Client, message: Message):
    """Usage: /rmpremium <user_id>"""
    parts = message.command
    if len(parts) != 2:
        return await message.reply("Usage: `/rmpremium <user_id>`")
    try:
        user_id = int(parts[1])
    except ValueError:
        return await message.reply("❌ Invalid user ID.")
    await db.remove_premium(user_id)
    await message.reply(f"✅ Premium removed for user `{user_id}`.")

# ── Payment Approval ──────────────────────────────────────────────────────────

@Client.on_message(filters.command("approve") & filters.user(Config.ADMINS))
async def approve_payment(client: Client, message: Message):
    """Usage: /approve <req_id>"""
    parts = message.command
    if len(parts) != 2:
        return await message.reply("Usage: `/approve <REQ_ID>`")
    req_id = parts[1].upper()
    doc    = await db.approve_payment(req_id)
    if not doc:
        return await message.reply("❌ Request ID not found or already processed.")

    req     = await db.get_payment_request(req_id)
    user_id = req["user_id"] if req else doc.get("user_id")
    plan    = req["plan"]    if req else doc.get("plan", "")
    exp     = doc["expires_at"].strftime("%d %b %Y")

    await message.reply(
        f"✅ **Approved!**\n\n"
        f"🆔 Req ID : `{req_id}`\n"
        f"👤 User   : `{user_id}`\n"
        f"📦 Plan   : **{plan.capitalize()}**\n"
        f"📅 Expires: **{exp}**"
    )
    # Notify user
    try:
        await client.send_message(
            user_id,
            f"🎉 **Your payment has been approved!**\n\n"
            f"📦 Plan    : **{plan.capitalize()}**\n"
            f"📅 Expires : **{exp}**\n\n"
            f"✅ You now enjoy **ad-free** file delivery!\n"
            f"Thank you for supporting {Config.BOT_NAME} 🐯\n\n"
            f"Use /mystatus to check your premium status."
        )
    except Exception:
        pass

@Client.on_message(filters.command("pending") & filters.user(Config.ADMINS))
async def list_pending(client: Client, message: Message):
    pending = await db.list_pending_payments()
    if not pending:
        return await message.reply("✅ No pending payment requests.")
    text = "📋 **Pending Payment Requests:**\n\n"
    for req in pending:
        created = req["created_at"].strftime("%d %b %Y %H:%M")
        text += (
            f"🆔 `{req['req_id']}` | 👤 `{req['user_id']}` | "
            f"📦 {req['plan'].capitalize()} | 🕐 {created}\n"
        )
    text += f"\nTo approve: `/approve <req_id>`"
    await message.reply(text)

# ── Broadcast ─────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMINS) & filters.reply)
async def broadcast_handler(client: Client, message: Message):
    replied = message.reply_to_message
    if not replied:
        return await message.reply("Reply to a message to broadcast it.")
    status_msg = await message.reply("📣 Broadcasting...")
    success, failed = 0, 0
    async for user_doc in db.users.find({}):
        try:
            await replied.copy(user_doc["user_id"])
            success += 1
        except Exception:
            failed += 1
    await status_msg.edit(
        f"✅ **Broadcast complete!**\n\n"
        f"✅ Sent   : `{success}`\n"
        f"❌ Failed : `{failed}`"
    )

# ── List all premium users ────────────────────────────────────────────────────

@Client.on_message(filters.command("premiumlist") & filters.user(Config.ADMINS))
async def premium_list(client: Client, message: Message):
    all_prem = await db.get_all_premium()
    if not all_prem:
        return await message.reply("No active premium users.")
    text = "💎 **Active Premium Users:**\n\n"
    for p in all_prem:
        exp = p["expires_at"].strftime("%d %b %Y")
        text += f"👤 `{p['user_id']}` | {p['plan'].capitalize()} | Expires: {exp}\n"
    await message.reply(text)

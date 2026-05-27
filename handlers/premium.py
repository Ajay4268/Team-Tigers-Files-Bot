"""
Premium Plans Handler
---------------------
Plans:
  Weekly  — ₹25  / 7 days
  Monthly — ₹350 / 30 days

Flow (Manual payment):
  1. User taps plan → sees UPI ID + amount + unique request ID
  2. User pays and sends screenshot to admin
  3. Admin runs /approve <req_id> → premium is activated
  4. User gets notified automatically
"""
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from database.db import Database
from config import Config
from utils.fsub import check_fsub

db = Database()

# ── /premium command ──────────────────────────────────────────────────────────

@Client.on_message(filters.command("premium") & filters.private)
async def premium_cmd(client: Client, message: Message):
    if not await check_fsub(client, message):
        return
    await show_premium_plans(client, message)

@Client.on_callback_query(filters.regex("^premium_plans$"))
async def premium_plans_cb(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    await show_premium_plans(client, callback_query.message, edit=True)

async def show_premium_plans(client, message, edit=False):
    user_id    = message.chat.id if not edit else message.chat.id
    is_premium = await db.is_premium(user_id)
    prem_info  = await db.get_premium_info(user_id)

    status_text = ""
    if is_premium and prem_info and user_id not in Config.ADMINS:
        exp = prem_info["expires_at"].strftime("%d %b %Y")
        status_text = f"✅ **Your Premium:** {prem_info['plan'].capitalize()} (expires {exp})\n\n"
    elif user_id in Config.ADMINS:
        status_text = "👑 **You are an Admin — Premium forever!**\n\n"

    text = (
        f"💎 **{Config.BOT_NAME} — Premium Plans**\n\n"
        f"{status_text}"
        f"🚀 **Benefits of Premium:**\n"
        f"• ✅ No URL shortener / ads\n"
        f"• ✅ Direct file links instantly\n"
        f"• ✅ Priority support\n"
        f"• ✅ Ad-free online streaming\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 **Available Plans:**\n\n"
        f"⏱ **Weekly Plan**\n"
        f"   💰 Price : ₹25\n"
        f"   📅 Valid : 7 Days\n\n"
        f"📅 **Monthly Plan**\n"
        f"   💰 Price : ₹350\n"
        f"   📅 Valid : 30 Days\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 Choose a plan to proceed with payment:"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱ Weekly — ₹25",   callback_data="buy_weekly"),
            InlineKeyboardButton("📅 Monthly — ₹350", callback_data="buy_monthly"),
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="back_home")],
    ])

    if edit:
        await message.edit_text(text, reply_markup=buttons)
    else:
        await message.reply_text(text, reply_markup=buttons)


# ── Buy plan callbacks ────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r"^buy_(weekly|monthly)$"))
async def buy_plan(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    plan    = callback_query.matches[0].group(1)
    user_id = callback_query.from_user.id
    info    = Config.PREMIUM_PLANS[plan]

    # Create a pending payment request
    req_id = await db.create_payment_request(user_id, plan)

    text = (
        f"💳 **Payment Details — {info['label']}**\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 **Amount   :** ₹{info['price']}\n"
        f"📅 **Duration :** {info['days']} Days\n"
        f"🆔 **Request ID:** `{req_id}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"**Step 1:** Pay ₹{info['price']} to the UPI ID below\n\n"
        f"🏦 **UPI ID:** `{Config.UPI_ID}`\n"
        f"👤 **Name  :** {Config.UPI_NAME}\n\n"
        f"**Step 2:** After payment, send the **screenshot** + your "
        f"**Request ID `{req_id}`** to our channel/admin:\n"
        f"📢 {Config.CHANNEL_URL}\n\n"
        f"**Step 3:** Admin will approve and your premium activates instantly! ✅\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ Do NOT pay without saving your Request ID!"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Send Screenshot to Channel", url=Config.CHANNEL_URL)],
        [InlineKeyboardButton("🔄 Check My Status", callback_data="my_status")],
        [InlineKeyboardButton("🔙 Back to Plans",   callback_data="premium_plans")],
    ])

    await callback_query.message.edit_text(text, reply_markup=buttons)

    # Notify admins
    for admin_id in Config.ADMINS:
        try:
            await client.send_message(
                admin_id,
                f"🔔 **New Payment Request**\n\n"
                f"👤 User  : [{callback_query.from_user.first_name}](tg://user?id={user_id})\n"
                f"🆔 ID    : `{user_id}`\n"
                f"📦 Plan  : **{plan.capitalize()}** — ₹{info['price']}\n"
                f"🎫 Req ID: `{req_id}`\n\n"
                f"To approve: `/approve {req_id}`"
            )
        except Exception:
            pass


# ── /mystatus command ─────────────────────────────────────────────────────────

@Client.on_message(filters.command("mystatus") & filters.private)
async def my_status_cmd(client: Client, message: Message):
    await show_my_status(client, message.from_user.id, message=message)

@Client.on_callback_query(filters.regex("^my_status$"))
async def my_status_cb(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    await show_my_status(client, callback_query.from_user.id, callback_query=callback_query)

async def show_my_status(client, user_id, message=None, callback_query=None):
    info = await db.get_premium_info(user_id)

    if user_id in Config.ADMINS:
        text = "👑 You are an **Admin** — you have **lifetime premium** access!"
    elif info:
        exp      = info["expires_at"]
        days_left = (exp - datetime.utcnow()).days
        text = (
            f"💎 **Your Premium Status**\n\n"
            f"📦 Plan      : **{info['plan'].capitalize()}**\n"
            f"📅 Expires   : `{exp.strftime('%d %b %Y %H:%M')} UTC`\n"
            f"⏳ Days Left : **{days_left} day(s)**\n\n"
            f"✅ You enjoy **ad-free** experience!"
        )
    else:
        text = (
            f"❌ **No Active Premium**\n\n"
            f"You are currently on the **Free plan**.\n"
            f"Files will be delivered via URL shortener.\n\n"
            f"Upgrade to Premium for ad-free experience!\n"
            f"Use /premium to see plans."
        )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 View Plans", callback_data="premium_plans")],
        [InlineKeyboardButton("🔙 Back",       callback_data="back_home")],
    ])

    if callback_query:
        await callback_query.message.edit_text(text, reply_markup=buttons)
    else:
        await message.reply_text(text, reply_markup=buttons)

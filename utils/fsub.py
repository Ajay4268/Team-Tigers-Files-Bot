"""
Force Subscribe Utility
-----------------------
Checks whether a user has joined all channels listed in Config.FORCE_SUB_CHANNELS.
If not, sends a "Join to continue" message with Join buttons and returns False.
All user-facing handlers call `await check_fsub(client, message_or_query)` first.
"""

import logging
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, ChannelPrivate
from config import Config

logger = logging.getLogger(__name__)


async def get_channel_info(client: Client, channel_id: int) -> dict:
    """Return {'title': ..., 'username': ..., 'invite_link': ...} for a channel."""
    try:
        chat = await client.get_chat(channel_id)
        username = chat.username
        invite_link = None

        if not username:
            # Private channel — generate/fetch invite link
            try:
                invite_link = chat.invite_link
                if not invite_link:
                    invite_link = (await client.create_chat_invite_link(channel_id)).invite_link
            except Exception as e:
                logger.warning(f"Could not get invite link for {channel_id}: {e}")

        return {
            "title"      : chat.title or f"Channel {channel_id}",
            "username"   : username,
            "invite_link": invite_link,
        }
    except Exception as e:
        logger.error(f"get_channel_info failed for {channel_id}: {e}")
        return {
            "title"      : f"Channel {channel_id}",
            "username"   : None,
            "invite_link": None,
        }


async def is_subscribed(client: Client, user_id: int, channel_id: int) -> bool:
    """Return True if the user is a member of the channel."""
    try:
        member = await client.get_chat_member(channel_id, user_id)
        # Banned / left counts as not subscribed
        return member.status.value not in ("banned", "left", "restricted")
    except UserNotParticipant:
        return False
    except (ChatAdminRequired, ChannelPrivate) as e:
        logger.warning(f"Bot lacks permission to check {channel_id}: {e}")
        return True   # Fail open so the bot doesn't block everyone
    except Exception as e:
        logger.error(f"is_subscribed error for user {user_id} in {channel_id}: {e}")
        return True   # Fail open on unexpected errors


async def check_fsub(client: Client, update: Message | CallbackQuery) -> bool:
    """
    Check all FORCE_SUB_CHANNELS.
    • Returns True  → user is subscribed to all, allow the action.
    • Returns False → user is missing at least one channel; sends join prompt.

    Admins always pass.
    If FORCE_SUB_CHANNELS is empty, always returns True.
    """
    if not Config.FORCE_SUB_CHANNELS:
        return True

    # Determine user and reply target
    if isinstance(update, CallbackQuery):
        user    = update.from_user
        message = update.message
        is_cb   = True
    else:
        user    = update.from_user
        message = update
        is_cb   = False

    # Admins bypass force subscribe
    if user.id in Config.ADMINS:
        return True

    # Find channels the user hasn't joined
    missing = []
    for channel_id in Config.FORCE_SUB_CHANNELS:
        if not await is_subscribed(client, user.id, channel_id):
            info = await get_channel_info(client, channel_id)
            missing.append((channel_id, info))

    if not missing:
        return True

    # Build join buttons
    buttons = []
    for idx, (channel_id, info) in enumerate(missing, start=1):
        if info["username"]:
            url = f"https://t.me/{info['username']}"
        elif info["invite_link"]:
            url = info["invite_link"]
        else:
            continue   # Can't generate a link — skip

        buttons.append([
            InlineKeyboardButton(
                f"✅ Join {info['title']}",
                url=url
            )
        ])

    # Add a "I've Joined" refresh button
    buttons.append([
        InlineKeyboardButton("🔄 I've Joined — Try Again", callback_data="fsub_check")
    ])

    text = (
        "🔒 **Access Restricted!**\n\n"
        "You must join the following channel(s) to use this bot:\n\n"
        + "\n".join(f"• **{info['title']}**" for _, info in missing)
        + "\n\n👆 Tap the button(s) above to join, then press **I've Joined**."
    )

    if is_cb:
        await update.answer("⚠️ Please join our channel(s) first!", show_alert=True)
        try:
            await message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception:
            await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), quote=True)

    return False

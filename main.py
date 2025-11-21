import os
import re
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN not set. Put your bot token in TELEGRAM_TOKEN env var or .env file.")

# Config
MAX_LINKS = int(os.getenv("MAX_LINKS", "2"))
STOPWORDS = os.getenv("STOPWORDS", "gcast,broadcast,promo,join,iklan,iklanchannel").split(",")
MIN_ACCOUNT_AGE_DAYS = int(os.getenv("MIN_ACCOUNT_AGE_DAYS", "3"))

link_pattern = re.compile(r'https?://|t\.me/|telegram\.me/|www\.')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("GCI AntiGcast Bot aktif. Mode: KILL EVERYTHING ✅")

async def handle_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    now = datetime.utcnow()
    for member in msg.new_chat_members:
        try:
            # Auto-ban obvious bots
            if member.is_bot:
                await msg.chat.ban_member(member.id)
                continue

            # If username missing or suspicious first name
            if not member.username:
                await msg.chat.ban_member(member.id)
                continue

            # If account age available and too new, ban
            # Telegram API does not provide account creation date directly; this is best-effort placeholder.
            # If member.id is small (<1e9) it might be older — we cannot reliably check account age via Bot API.
            # We keep this block for future compatibility if such info becomes available.
            # For now, ban accounts with username containing http/www/@ patterns
            if member.first_name and (member.first_name.startswith("http") or member.first_name.startswith("@") or member.first_name.startswith("www")):
                await msg.chat.ban_member(member.id)
                continue
        except Exception as e:
            print("Error handling new member:", e)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # Ignore messages from chat admins or the bot itself
    try:
        member_status = await message.chat.get_member(message.from_user.id)
        if member_status.status in ("administrator", "creator"):
            return
    except Exception:
        # If we can't fetch member status, continue checks (safer to act)
        pass

    # 1) Detect forwarded messages
    if message.forward_date or message.forward_from or message.forward_from_chat:
        try:
            await message.delete()
            await message.chat.ban_member(message.from_user.id)
            print(f"Banned for forwarding: {message.from_user.id}")
        except Exception as e:
            print("Error banning forwarder:", e)
        return

    text = (message.text or message.caption or "") or ""
    text_lower = text.lower()

    # 2) Stopwords check
    if any(word.strip() and word.strip() in text_lower for word in STOPWORDS):
        try:
            await message.delete()
            await message.chat.ban_member(message.from_user.id)
            print(f"Banned for stopword: {message.from_user.id}")
        except Exception as e:
            print("Error banning stopword sender:", e)
        return

    # 3) Link count check
    links_found = len(link_pattern.findall(text))
    if links_found > MAX_LINKS:
        try:
            await message.delete()
            await message.chat.ban_member(message.from_user.id)
            print(f"Banned for too many links ({links_found}): {message.from_user.id}")
        except Exception as e:
            print("Error banning for links:", e)
        return

async def healthcheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive ✅")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('health', healthcheck))
    # New members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))
    # All messages
    app.add_handler(MessageHandler(filters.ALL & (~filters.StatusUpdate.NEW_CHAT_MEMBERS), handle_message))
    print("Starting GCI AntiGcast Bot...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())

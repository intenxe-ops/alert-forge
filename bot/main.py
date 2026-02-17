import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application, CommandHandler
from supabase import create_client, Client

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start_command(update, context):
    chat_id = update.effective_chat.id
    try:
        supabase.table('users').upsert({
            'telegram_chat_id': str(chat_id),
            'subscription_tier': 'free'
        }).execute()
        await update.message.reply_text(
            f"⚡ *Alert Forge*\n\n"
            f"✅ Connected + Registered\n"
            f"📋 Chat ID: `{chat_id}`\n"
            f"🎯 Tier: Free\n\n"
            f"You're ready to receive alerts.",
            parse_mode='Markdown'
        )
        print(f"✅ User {chat_id} registered in Supabase")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
        print(f"❌ Supabase error: {e}")

async def send_test_alert():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text="⚡ *ALERT FORGE*\n\n✅ Telegram connected\n✅ Supabase connected\n✅ Monitoring ready",
        parse_mode='Markdown'
    )
    print("✅ Test alert sent")

def main():
    print("🚀 Alert Forge starting...")
    print(f"📡 Supabase: {SUPABASE_URL}")
    asyncio.get_event_loop().run_until_complete(send_test_alert())
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    print("✅ Bot running.")
    app.run_polling()

if __name__ == "__main__":
    main()
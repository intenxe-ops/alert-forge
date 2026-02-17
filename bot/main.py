import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application, CommandHandler
from supabase import create_client, Client
from wallet_monitor import get_wallet_transactions, format_transaction_alert

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Track seen transactions (prevent duplicates)
seen_signatures = set()

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
        print(f"✅ User {chat_id} registered")
    except Exception as e:
        print(f"❌ Error: {e}")

async def check_wallets(bot: Bot):
    """Check all active wallets and send alerts for new transactions"""
    
    # TEST WALLET - replace with dynamic from Supabase later
    TEST_WALLET = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
    
    try:
        txs = get_wallet_transactions(TEST_WALLET, limit=5)
        
        for tx in txs:
            sig = tx.get('signature', '')
            
            # Skip if already seen
            if sig in seen_signatures:
                continue
            
            # New transaction detected
            seen_signatures.add(sig)
            
            # Format and send alert
            alert = format_transaction_alert(tx, TEST_WALLET)
            
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=alert,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            print(f"✅ Alert sent for tx: {sig[:20]}...")
            
    except Exception as e:
        print(f"❌ Wallet check error: {e}")

async def monitoring_loop(bot: Bot):
    """Run wallet monitoring every 60 seconds"""
    print("👁 Wallet monitoring started...")
    
    # Load existing signatures on startup (prevent spam)
    TEST_WALLET = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
    existing = get_wallet_transactions(TEST_WALLET, limit=10)
    for tx in existing:
        seen_signatures.add(tx.get('signature', ''))
    print(f"📋 Loaded {len(seen_signatures)} existing transactions")
    
    while True:
        await check_wallets(bot)
        await asyncio.sleep(60)

async def post_init(application):
    """Start monitoring loop after bot initializes"""
    asyncio.create_task(
        monitoring_loop(application.bot)
    )

def main():
    print("🚀 Alert Forge starting...")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_command))
    
    print("✅ Bot running. Monitoring wallets...")
    app.run_polling()

if __name__ == "__main__":
    main()
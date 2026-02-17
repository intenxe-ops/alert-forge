import os
import requests
from dotenv import load_dotenv

load_dotenv()

HELIUS_API_KEY = os.getenv('HELIUS_API_KEY')

def get_wallet_transactions(wallet_address: str, limit: int = 5):
    """Fetch latest transactions for a wallet"""
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions"
    
    params = {
        "api-key": HELIUS_API_KEY,
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Helius API error: {e}")
        return []

def format_transaction_alert(tx: dict, wallet_address: str) -> str:
    """Format transaction into readable Telegram message"""
    
    tx_type = tx.get('type', 'UNKNOWN')
    signature = tx.get('signature', '')[:20]
    fee = tx.get('fee', 0) / 1e9  # Convert lamports to SOL
    
    # Get SOL balance change
    account_changes = tx.get('accountData', [])
    sol_change = 0
    for account in account_changes:
        if account.get('account') == wallet_address:
            sol_change = account.get('nativeBalanceChange', 0) / 1e9
    
    # Format direction
    direction = "📈 RECEIVED" if sol_change > 0 else "📉 SENT"
    amount = abs(sol_change)
    
    message = (
        f"⚡ *ALERT FORGE - Wallet Alert*\n\n"
        f"👛 Wallet: `{wallet_address[:8]}...{wallet_address[-8:]}`\n"
        f"🔔 Type: {tx_type}\n"
        f"{direction}: {amount:.4f} SOL\n"
        f"⛽ Fee: {fee:.6f} SOL\n"
        f"🔗 Sig: `{signature}...`\n\n"
        f"[View on Solscan](https://solscan.io/tx/{tx.get('signature', '')})"
    )
    
    return message

def test_wallet_fetch(wallet_address: str):
    """Test fetching transactions for a wallet"""
    print(f"🔍 Fetching transactions for {wallet_address[:8]}...")
    
    txs = get_wallet_transactions(wallet_address, limit=3)
    
    if not txs:
        print("❌ No transactions found or API error")
        return
    
    print(f"✅ Found {len(txs)} transactions")
    
    for tx in txs:
        print(f"  - {tx.get('type', 'UNKNOWN')} | {tx.get('signature', '')[:20]}...")
    
    # Format first transaction as alert
    if txs:
        alert = format_transaction_alert(txs[0], wallet_address)
        print(f"\n📱 SAMPLE ALERT:\n{alert}")

if __name__ == "__main__":
    # Test with a known active Solana wallet (Binance hot wallet)
    TEST_WALLET = "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
    test_wallet_fetch(TEST_WALLET)
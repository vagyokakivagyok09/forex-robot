�"""
Helper script to get your Telegram Chat ID

Run this after sending a message to your bot
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

if not bot_token:
    print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file")
    exit(1)

print("🔍 Fetching recent messages...\n")

url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if not data.get('ok'):
        print(f"❌ Error: {data.get('description', 'Unknown error')}")
        exit(1)
    
    results = data.get('result', [])
    
    if not results:
        print("⚠️ No messages found!")
        print("\n📝 Steps to get your Chat ID:")
        print("   1. Open Telegram")
        print("   2. Search for your bot")
        print("   3. Send any message to it (e.g., 'Hello')")
        print("   4. Run this script again")
        exit(0)
    
    # Get the latest message
    latest = results[-1]
    
    if 'message' in latest:
        chat_id = latest['message']['chat']['id']
        chat_type = latest['message']['chat']['type']
        
        print("✅ Chat ID found!\n")
        print(f"📱 Chat ID: {chat_id}")
        print(f"📊 Chat Type: {chat_type}")
        
        # Show first name if available
        if 'first_name' in latest['message']['chat']:
            first_name = latest['message']['chat']['first_name']
            print(f"👤 Name: {first_name}")
        
        print("\n" + "="*60)
        print("📋 Next step:")
        print(f"\nAdd this to your .env file:\n")
        print(f"TELEGRAM_CHAT_ID={chat_id}")
        print("\n" + "="*60)
        
    else:
        print("⚠️ No message found in the latest update")
        print("Please send a message to your bot and try again")

except Exception as e:
    print(f"❌ Error: {e}")
�*cascade082*file:///c:/Users/Tomi/FOREX/get_chat_id.py
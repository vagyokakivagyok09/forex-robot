�."""
Telegram Notification Module

Sends formatted trading alerts via Telegram Bot API
"""

import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TelegramNotifier:
    """Handles Telegram notifications for trading signals"""
    
    def __init__(self, bot_token=None, chat_id=None):
        """
        Initialize Telegram Notifier
        
        Args:
            bot_token: Telegram bot token (or use TELEGRAM_BOT_TOKEN env var / Streamlit secret)
            chat_id: Telegram chat ID (or use TELEGRAM_CHAT_ID env var / Streamlit secret)
        """
        # Try Streamlit secrets first (for cloud deployment)
        if bot_token is None:
            try:
                import streamlit as st
                if hasattr(st, 'secrets') and 'TELEGRAM' in st.secrets:
                    bot_token = st.secrets["TELEGRAM"].get("TELEGRAM_BOT_TOKEN")
                    chat_id = st.secrets["TELEGRAM"].get("TELEGRAM_CHAT_ID")
            except:
                pass
        
        # Fallback to environment variables or parameters
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if not self.enabled:
            print("⚠️ Telegram notifications disabled (missing BOT_TOKEN or CHAT_ID)")
    
    def send_message(self, message, parse_mode='HTML'):
        """
        Send a message via Telegram
        
        Args:
            message: Message text
            parse_mode: 'HTML' or 'Markdown'
        
        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            print(f"📱 [Telegram Disabled] Would send: {message}")
            return False
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Telegram message sent successfully")
                return True
            else:
                print(f"❌ Telegram error: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")
            return False
    
    def send_signal_alert(self, signal_type, symbol, price, momentum, squeeze_on=False):
        """
        Send formatted trading signal alert
        
        Args:
            signal_type: 'BUY', 'SELL', or 'WAIT'
            symbol: Currency pair name (e.g., 'EURUSD')
            price: Current price
            momentum: Momentum value
            squeeze_on: Current squeeze status
        
        Returns:
            bool: True if sent successfully
        """
        # Emoji selection
        if signal_type == 'BUY':
            emoji = '🚀'
            direction = '↗️ LONG'
            color = '🟢'
        elif signal_type == 'SELL':
            emoji = '🔻'
            direction = '↘️ SHORT'
            color = '🔴'
        else:
            return False  # Don't send WAIT signals
        
        # Squeeze status emoji
        squeeze_emoji = '🟢 ON' if squeeze_on else '🔴 FIRE'
        
        # Format message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"""
{emoji} <b>TTM SQUEEZE SIGNAL</b> {emoji}

{color} <b>{signal_type}</b> | {symbol}
{direction}

💰 <b>Price:</b> {price:.5f}
📊 <b>Momentum:</b> {momentum:.5f}
🎯 <b>Squeeze:</b> {squeeze_emoji}

🕒 {timestamp}
        """.strip()
        
        return self.send_message(message)
    
    def send_daily_summary(self, summary_data):
        """
        Send daily trading summary
        
        Args:
            summary_data: Dictionary with summary statistics
        
        Returns:
            bool: True if sent successfully
        """
        message = f"""
📊 <b>Daily TTM Squeeze Summary</b>

🔍 <b>Pairs Monitored:</b> {summary_data.get('total_pairs', 0)}
🟢 <b>Squeeze ON:</b> {summary_data.get('squeeze_on_count', 0)}
🔴 <b>Signals:</b> {summary_data.get('signal_count', 0)}

🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        return self.send_message(message)
    
    def test_connection(self):
        """
        Test Telegram connection
        
        Returns:
            bool: True if connection successful
        """
        message = "✅ TTM Squeeze Bot - Connection Test Successful!"
        return self.send_message(message)


# Example usage
if __name__ == "__main__":
    print("🔍 Testing Telegram Notifier\n")
    
    notifier = TelegramNotifier()
    
    # Test connection
    print("Test 1: Connection test")
    notifier.test_connection()
    print()
    
    # Test BUY signal
    print("Test 2: BUY signal")
    notifier.send_signal_alert(
        signal_type='BUY',
        symbol='EURUSD',
        price=1.08543,
        momentum=0.00125,
        squeeze_on=False
    )
    print()
    
    # Test SELL signal
    print("Test 3: SELL signal")
    notifier.send_signal_alert(
        signal_type='SELL',
        symbol='GBPUSD',
        price=1.25678,
        momentum=-0.00098,
        squeeze_on=False
    )
    print()
    
    # Test daily summary
    print("Test 4: Daily summary")
    notifier.send_daily_summary({
        'total_pairs': 5,
        'squeeze_on_count': 2,
        'signal_count': 3
    })
� *cascade08��*cascade08��. *cascade0820file:///c:/Users/Tomi/FOREX/telegram_notifier.py
import requests
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import re

# 1. Extract Credentials from app.py
try:
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    token_match = re.search(r'TELEGRAM_BOT_TOKEN\s*=\s*"([^"]+)"', content)
    chat_id_match = re.search(r'TELEGRAM_CHAT_ID\s*=\s*"([^"]+)"', content)

    if token_match and chat_id_match:
        TOKEN = token_match.group(1)
        CHAT_ID = chat_id_match.group(1)
        print(f"Credentials found: TOKEN=...{TOKEN[-5:]}, CHAT_ID={CHAT_ID}")
    else:
        print("ERROR: Could not find credentials in app.py")
        exit(1)
except Exception as e:
    print(f"ERROR reading app.py: {e}")
    exit(1)

# 2. Test Telegram
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Telegram message sent successfully.")
            return True
        else:
            print(f"❌ Telegram failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

print("\n--- Testing Telegram ---")
send_telegram("🧪 <b>Rendszerellenőrzés</b>\nEz egy teszt üzenet a Python scriptből.")

# 3. Test Data Fetching
print("\n--- Testing Data Fetching (GBPUSD=X) ---")
try:
    df = yf.download("GBPUSD=X", period="5d", interval="15m", progress=False)
    if not df.empty:
        print(f"✅ Data fetched successfully. Shape: {df.shape}")
        # Handle MultiIndex if present (common in new yfinance)
        if isinstance(df.columns, pd.MultiIndex):
             try:
                 close_val = df.xs('GBPUSD=X', axis=1, level=1)['Close'].iloc[-1]
             except:
                 close_val = df['Close'].iloc[-1]
        else:
            close_val = df['Close'].iloc[-1]
            
        print(f"Last close: {close_val}")
    else:
        print("❌ Data fetched but empty.")
except Exception as e:
    print(f"❌ Data fetch error: {e}")

# 4. Test Plotly
print("\n--- Testing Plotly Figure Generation ---")
try:
    if 'df' in locals() and not df.empty:
        # Simple check, ignoring complex multiindex handling for the graph just to see if import works
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        print("✅ Plotly figure created successfully.")
    else:
        print("⚠️ Skipping Plotly test due to missing data.")
except Exception as e:
    print(f"❌ Plotly error: {e}")

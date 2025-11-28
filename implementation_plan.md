# Twelve Data API Integration - Implementation Plan

## Goal Description

Replace yfinance data source with Twelve Data API to eliminate pricing discrepancies between webapp and XTB broker. 

**Problem:** yfinance uses delayed Yahoo Finance data causing:
- ❌ Incorrect London Box calculations
- ❌ False TP/SL detections (e.g., GBP/JPY showing profit when actually loss)
- ❌ Wrong entry prices sent via Telegram

**Solution:** Twelve Data free tier provides broker-quality real-time forex data compatible with cloud deployment.

---

## User Review Required

> [!IMPORTANT]
> **Twelve Data Free Tier Setup Required**
> 1. Register at https://twelvedata.com/pricing (Free plan)
> 2. Generate API key from dashboard
> 3. Provide API key for Streamlit secrets configuration

**Rate Limit Strategy:**
- Free tier: 8 API calls/minute, 800/day
- Our usage: **1 batch call every 15 seconds = 4 calls/min** ✅
- Daily: ~960 calls (London hours only 07:00-17:00 GMT = ~240 calls) ✅

---

## Proposed Changes

### Core Components

#### [NEW] [twelve_data_connector.py](file:///c:/Users/Tomi/.gemini/twelve_data_connector.py)

Batch request connector with fallback logic:

```python
import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

# Twelve Data symbols (different format than yfinance)
SYMBOL_MAP = {
    'GBPUSD=X': 'GBP/USD',
    'GBPJPY=X': 'GBP/JPY', 
    'EURUSD=X': 'EUR/USD'
}

BATCH_SYMBOLS = "GBP/USD,GBP/JPY,EUR/USD"

def get_batch_prices(api_key):
    """
    Fetch current prices for all 3 pairs in single API call.
    Returns: dict with symbol keys and price values
    """
    url = f"https://api.twelvedata.com/price?symbol={BATCH_SYMBOLS}&apikey={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Check for API errors
        if 'code' in data and data['code'] >= 400:
            st.error(f"Twelve Data API error: {data.get('message', 'Unknown')}")
            return None
            
        return data
        
    except Exception as e:
        st.error(f"Network error: {e}")
        return None

def get_historical_data(symbol, api_key, interval='15m', outputsize=5000):
    """
    Fetch historical OHLC data for single symbol.
    interval: 1min, 5min, 15min, 30min, 1h, etc.
    outputsize: max 5000 for free tier
    """
    td_symbol = SYMBOL_MAP.get(symbol, symbol)
    url = f"https://api.twelvedata.com/time_series?symbol={td_symbol}&interval={interval}&outputsize={outputsize}&apikey={api_key}"
    
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
        
        if 'code' in data and data['code'] >= 400:
            return None
            
        # Convert to pandas DataFrame
        values = data.get('values', [])
        if not values:
            return None
            
        df = pd.DataFrame(values)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        
        # Convert to numeric
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col])
            
        # Rename columns to match yfinance format
        df.rename(columns={
            'open': 'Open',
            'high': 'High', 
            'low': 'Low',
            'close': 'Close'
        }, inplace=True)
        
        # Sort ascending (oldest first)
        df = df.sort_index()
        
        # Handle timezone (Twelve Data returns UTC)
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
            
        return df
        
    except Exception as e:
        st.error(f"Error fetching {symbol}: {e}")
        return None
```

---

#### [MODIFY] [app.py](file:///c:/Users/Tomi/.gemini/app.py)

**Line 10-14:** Import connector
```python
import twelve_data_connector as td

# Get API key from Streamlit secrets
TWELVE_DATA_API_KEY = st.secrets.get("TWELVE_DATA_API_KEY", None)
```

**Line 105-146:** Replace `get_data()` function
```python
@st.cache_data(ttl=60)
def get_data(ticker):
    """Fetch data from Twelve Data with yfinance fallback."""
    
    # Try Twelve Data first
    if TWELVE_DATA_API_KEY:
        try:
            df = td.get_historical_data(ticker, TWELVE_DATA_API_KEY, interval='15min', outputsize=5000)
            if df is not None and not df.empty:
                return df
        except Exception as e:
            st.warning(f"Twelve Data failed for {ticker}, falling back to yfinance: {e}")
    
    # Fallback to yfinance (original code)
    try:
        df = yf.download(ticker, period="59d", interval="15m", progress=False)
        # ... original yfinance processing code ...
        return df
    except Exception as e:
        st.error(f"Both APIs failed for {ticker}: {e}")
        return None
```

**Line 310-326:** Add API status indicator
```python
st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 Data Source")

if TWELVE_DATA_API_KEY:
    st.sidebar.success("✅ Twelve Data API (Accurate)")
else:
    st.sidebar.warning("⚠️ Using yfinance (May differ from XTB)")
```

---

#### [MODIFY] [.streamlit/secrets.toml](file:///c:/Users/Tomi/.gemini/.streamlit/secrets.toml)

```toml
TWELVE_DATA_API_KEY = "YOUR_API_KEY_HERE"
TELEGRAM_BOT_TOKEN = "7487229026:AAH51YJ4atFsvqHKfQj9l_QU7ytJMIwo0w0"
TELEGRAM_CHAT_ID = "1736205722"
```

> [!NOTE]
> User must add this to Streamlit Cloud dashboard: Settings → Secrets

---

## Verification Plan

### Test 1: Local API Test

```bash
python -c "import twelve_data_connector as td; print(td.get_batch_prices('YOUR_API_KEY'))"
```

Expected output:
```json
{
  "GBP/USD": {"price": "1.27345"},
  "GBP/JPY": {"price": "191.234"},
  "EUR/USD": {"price": "1.05678"}
}
```

---

### Test 2: Historical Data Comparison

Compare London Box calculation:
1. Run app with Twelve Data
2. Note 07:00-08:00 GMT High/Low
3. Open XTB platform, check same period
4. **Expected:** Values match within 1-2 pips

---

### Test 3: Rate Limit Monitoring

Monitor API usage:
```python
# Add to twelve_data_connector.py
call_count = 0
last_reset = datetime.now()

def get_historical_data(...):
    global call_count
    call_count += 1
    print(f"API calls this minute: {call_count}")
    # Reset counter every minute
```

Run for 1 hour, verify:
- Calls/minute < 8 ✅
- No 429 errors (rate limit exceeded)

---

### Test 4: 24h Cloud Deployment

Deploy to Streamlit Cloud:
1. Add API key to secrets
2. Monitor for 24 hours
3. Check trade_history.json for correct TP/SL detections
4. **Expected:** No false positives like GBP/JPY bug

---

## Rollback Plan

If Twelve Data fails:

```bash
git checkout HEAD~1  # Restore backup commit
```

Or remove Twelve Data code:
1. Delete `twelve_data_connector.py`
2. Restore original `get_data()` function from `app_backup_before_mt5.py`
3. Remove Twelve Data import from `app.py`

---

## Next Steps

1. **User:** Register Twelve Data free account
2. **User:** Generate API key
3. **Agent:** Create `twelve_data_connector.py`
4. **Agent:** Modify `app.py` with fallback logic
5. **Agent:** Test locally
6. **User:** Add API key to Streamlit Cloud secrets
7. **Agent:** Deploy and verify

---

**Status:** ⏸️ Awaiting Twelve Data API key from user

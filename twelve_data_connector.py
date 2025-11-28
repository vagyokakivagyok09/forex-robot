"""
Twelve Data API Connector for London Breakout Pro
--------------------------------------------------
Provides real-time forex data with batch request optimization for free tier.

Free Tier Limits:
- 8 API calls/minute
- 800 API calls/day

Our Strategy:
- Batch request: 1 call for 3 symbols = 1 API call
- Refresh: every 15 seconds = 4 calls/minute (50% of limit)
- Daily usage: ~240 calls during London hours (07:00-17:00 GMT)
"""

import requests
import pandas as pd
from datetime import datetime
import streamlit as st

# Symbol mapping: yfinance format → Twelve Data format
SYMBOL_MAP = {
    'GBPUSD=X': 'GBP/USD',
    'GBPJPY=X': 'GBP/JPY',
    'EURUSD=X': 'EUR/USD'
}

# Batch symbols (comma-separated for single API call)
BATCH_SYMBOLS = "GBP/USD,GBP/JPY,EUR/USD"

# API call counter (for monitoring)
api_call_count = 0
last_reset_time = datetime.now()


def reset_counter_if_needed():
    """Reset counter every minute for monitoring."""
    global api_call_count, last_reset_time
    now = datetime.now()
    if (now - last_reset_time).seconds >= 60:
        api_call_count = 0
        last_reset_time = now


def get_batch_prices(api_key):
    """
    Fetch current prices for all 3 forex pairs in a single API call.
    
    Args:
        api_key: Twelve Data API key
        
    Returns:
        dict: {symbol: {price: value}} or None on error
        
    Example:
        {
            'GBP/USD': {'price': '1.27345'},
            'GBP/JPY': {'price': '191.234'},
            'EUR/USD': {'price': '1.05678'}
        }
    """
    global api_call_count
    reset_counter_if_needed()
    
    url = f"https://api.twelvedata.com/price?symbol={BATCH_SYMBOLS}&apikey={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        api_call_count += 1
        
        # Check for API errors
        if isinstance(data, dict) and 'code' in data and data['code'] >= 400:
            st.error(f"Twelve Data API error: {data.get('message', 'Unknown error')}")
            return None
        
        # Validate response structure
        if not isinstance(data, dict):
            st.error(f"Unexpected API response format: {data}")
            return None
            
        return data
        
    except requests.exceptions.Timeout:
        st.warning("Twelve Data API timeout (10s)")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"Network error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error in get_batch_prices: {e}")
        return None


def get_historical_data(symbol, api_key, interval='15min', outputsize=5000):
    """
    Fetch historical OHLC candlestick data for a single symbol.
    
    Args:
        symbol: yfinance-style symbol (e.g., 'GBPUSD=X')
        api_key: Twelve Data API key
        interval: Timeframe (1min, 5min, 15min, 30min, 1h, 4h, 1day)
        outputsize: Number of candles (max 5000 for free tier)
        
    Returns:
        pandas.DataFrame: OHLC data with DateTimeIndex (UTC)
                         Columns: Open, High, Low, Close
        None: On error
    """
    global api_call_count
    reset_counter_if_needed()
    
    # Convert symbol to Twelve Data format
    td_symbol = SYMBOL_MAP.get(symbol, symbol)
    
    url = (
        f"https://api.twelvedata.com/time_series?"
        f"symbol={td_symbol}&interval={interval}&outputsize={outputsize}&apikey={api_key}"
    )
    
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
        
        api_call_count += 1
        
        # Check for API errors
        if 'code' in data and data['code'] >= 400:
            error_msg = data.get('message', 'Unknown error')
            st.warning(f"Twelve Data error for {symbol}: {error_msg}")
            return None
        
        # Extract time series values
        values = data.get('values', [])
        if not values:
            st.warning(f"No data returned for {symbol}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(values)
        
        # Parse datetime and set as index
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        
        # Convert OHLC columns to numeric
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Rename to match yfinance format (capitalized)
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close'
        }, inplace=True)
        
        # Sort by datetime (oldest first)
        df = df.sort_index()
        
        # Ensure UTC timezone (Twelve Data returns UTC by default)
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        else:
            df.index = df.index.tz_convert('UTC')
        
        return df
        
    except requests.exceptions.Timeout:
        st.warning(f"Timeout fetching {symbol} (30s limit)")
        return None
    except requests.exceptions.RequestException as e:
        st.warning(f"Network error fetching {symbol}: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing {symbol} data: {e}")
        return None


def get_api_call_stats():
    """
    Get current API call statistics for monitoring.
    
    Returns:
        dict: {'calls_this_minute': int, 'last_reset': datetime}
    """
    return {
        'calls_this_minute': api_call_count,
        'last_reset': last_reset_time
    }


def is_api_available(api_key):
    """
    Test if Twelve Data API is accessible with given key.
    
    Args:
        api_key: API key to test
        
    Returns:
        bool: True if API is working, False otherwise
    """
    if not api_key:
        return False
    
    try:
        # Quick test with minimal request
        url = f"https://api.twelvedata.com/price?symbol=EUR/USD&apikey={api_key}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # Check if we got valid response (not error)
        if 'price' in data or ('EUR/USD' in data and 'price' in data['EUR/USD']):
            return True
        return False
        
    except Exception:
        return False

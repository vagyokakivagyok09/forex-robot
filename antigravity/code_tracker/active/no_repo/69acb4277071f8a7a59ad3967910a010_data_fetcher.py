�&"""
Forex Data Fetcher Module

Fetches forex data using yfinance library
Supports multiple currency pairs with configurable timeframes
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


# Supported forex pairs (Yahoo Finance format)
FOREX_PAIRS = {
    'EURUSD': 'EURUSD=X',
    'GBPUSD': 'GBPUSD=X',
    'USDJPY': 'USDJPY=X',
    'GBPJPY': 'GBPJPY=X',
    'AUDUSD': 'AUDUSD=X',
    'USDCHF': 'USDCHF=X',
    'NZDUSD': 'NZDUSD=X',
    'EURGBP': 'EURGBP=X'
}


def fetch_forex_data(symbol, period='1mo', interval='1h'):
    """
    Fetch forex data from Yahoo Finance
    
    Args:
        symbol: Forex pair symbol (e.g., 'EURUSD=X')
        period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y')
        interval: Candle interval ('1m', '5m', '15m', '1h', '1d')
    
    Returns:
        DataFrame with OHLC data
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            print(f"⚠️ No data returned for {symbol}")
            return pd.DataFrame()
        
        # Clean up the data
        df = df.reset_index()
        
        # Remove timezone info if present
        if 'Datetime' in df.columns:
            df['Datetime'] = pd.to_datetime(df['Datetime']).dt.tz_localize(None)
        elif 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        
        return df
    
    except Exception as e:
        print(f"❌ Error fetching data for {symbol}: {e}")
        return pd.DataFrame()


def get_latest_candles(symbol, count=100, interval='1h'):
    """
    Get the latest N candles for a symbol
    
    Args:
        symbol: Forex pair symbol
        count: Number of candles to fetch
        interval: Candle interval
    
    Returns:
        DataFrame with latest candles
    """
    # Determine period based on count and interval
    if interval == '1h':
        period = '1mo' if count <= 500 else '3mo'
    elif interval == '1d':
        period = '6mo' if count <= 100 else '1y'
    elif interval in ['5m', '15m', '30m']:
        period = '5d' if count <= 100 else '1mo'
    else:
        period = '1mo'
    
    df = fetch_forex_data(symbol, period=period, interval=interval)
    
    if df.empty:
        return df
    
    # Return last N candles
    return df.tail(count).reset_index(drop=True)


def get_all_pairs_data(pairs=None, interval='1h', candles=100):
    """
    Fetch data for multiple forex pairs
    
    Args:
        pairs: List of pair names (e.g., ['EURUSD', 'GBPUSD'])
               If None, fetches all supported pairs
        interval: Candle interval
        candles: Number of candles to fetch
    
    Returns:
        Dictionary: {pair_name: DataFrame}
    """
    if pairs is None:
        pairs = list(FOREX_PAIRS.keys())
    
    data = {}
    
    for pair in pairs:
        if pair not in FOREX_PAIRS:
            print(f"⚠️ Unknown pair: {pair}, skipping...")
            continue
        
        symbol = FOREX_PAIRS[pair]
        print(f"📊 Fetching {pair} ({symbol})...")
        
        df = get_latest_candles(symbol, count=candles, interval=interval)
        
        if not df.empty:
            data[pair] = df
            print(f"✅ {pair}: {len(df)} candles fetched")
        else:
            print(f"❌ {pair}: No data available")
    
    return data


def get_current_price(symbol):
    """
    Get current price for a forex pair
    
    Args:
        symbol: Forex pair symbol (e.g., 'EURUSD=X')
    
    Returns:
        float: Current price, or None if error
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d', interval='1m')
        
        if data.empty:
            return None
        
        return float(data['Close'].iloc[-1])
    
    except Exception as e:
        print(f"❌ Error getting current price for {symbol}: {e}")
        return None


# Example usage
if __name__ == "__main__":
    print("🔍 Testing Forex Data Fetcher\n")
    
    # Test single pair
    print("Test 1: Fetch EURUSD data")
    df = get_latest_candles('EURUSD=X', count=50, interval='1h')
    print(f"Fetched {len(df)} candles")
    print(df.tail())
    print()
    
    # Test multiple pairs
    print("Test 2: Fetch multiple pairs")
    data = get_all_pairs_data(['EURUSD', 'GBPUSD', 'USDJPY'], interval='1h', candles=50)
    print(f"\nFetched {len(data)} pairs:")
    for pair, df in data.items():
        print(f"  {pair}: {len(df)} candles")
    print()
    
    # Test current price
    print("Test 3: Get current price")
    price = get_current_price('EURUSD=X')
    print(f"EURUSD current price: {price}")
�&*cascade082+file:///c:/Users/Tomi/FOREX/data_fetcher.py
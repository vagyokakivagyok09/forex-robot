"""
Test script for Twelve Data API connection
"""

import twelve_data_connector as td

# API key (from secrets)
API_KEY = "8a2d0c5109674185b728ad95eea02436"

print("=" * 50)
print("TWELVE DATA API CONNECTION TEST")
print("=" * 50)

# Test 1: API availability
print("\n1. Testing API availability...")
if td.is_api_available(API_KEY):
    print("✅ API is accessible!")
else:
    print("❌ API failed to respond")
    exit(1)

# Test 2: Batch price request
print("\n2. Testing batch price request (GBP/USD, GBP/JPY, EUR/USD)...")
prices = td.get_batch_prices(API_KEY)

if prices:
    print("✅ Batch request successful!")
    for symbol, data in prices.items():
        if isinstance(data, dict) and 'price' in data:
            print(f"   {symbol}: {data['price']}")
else:
    print("❌ Batch request failed")
    exit(1)

# Test 3: Historical data (15min OHLC)
print("\n3. Testing historical data retrieval for GBPUSD=X...")
df = td.get_historical_data('GBPUSD=X', API_KEY, interval='15min', outputsize=100)

if df is not None and not df.empty:
    print(f"✅ Historical data retrieved: {len(df)} candles")
    print(f"   Latest candle: {df.index[-1]}")
    print(f"   Close: {df['Close'].iloc[-1]}")
    print(f"   Columns: {list(df.columns)}")
else:
    print("❌ Historical data retrieval failed")
    exit(1)

# Test 4: API call statistics
print("\n4. API call statistics...")
stats = td.get_api_call_stats()
print(f"✅ Calls this minute: {stats['calls_this_minute']}")
print(f"   Last reset: {stats['last_reset'].strftime('%H:%M:%S')}")

print("\n" + "=" * 50)
print("ALL TESTS PASSED! ✅")
print("=" * 50)
print("\nYou can now run the Streamlit app:")
print("  streamlit run app.py")

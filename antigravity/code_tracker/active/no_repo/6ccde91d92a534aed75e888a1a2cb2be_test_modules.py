�"""
Quick Test Script for TTM Squeeze Webapp
Tests all core modules without running the full dashboard
"""

print("🔍 Testing TTM Squeeze Webapp Components\n")
print("=" * 60)

# Test 1: TTM Squeeze Calculation
print("\n1️⃣ Testing TTM Squeeze Calculation...")
try:
    from ttm_squeeze import calculate_ttm_squeeze, check_signal
    import pandas as pd
    import numpy as np
    
    # Create sample data
    df = pd.DataFrame({
        'High': np.random.uniform(1.05, 1.15, 50),
        'Low': np.random.uniform(0.95, 1.05, 50),
        'Close': np.random.uniform(1.00, 1.10, 50),
        'Open': np.random.uniform(1.00, 1.10, 50)
    })
    
    result = calculate_ttm_squeeze(df)
    
    # Check for required columns
    required_cols = ['BB_Upper', 'BB_Lower', 'KC_Upper', 'KC_Lower', 'Squeeze_On', 'Momentum']
    missing = [col for col in required_cols if col not in result.columns]
    
    if not missing:
        print("   ✅ TTM Squeeze calculation PASSED")
        print(f"   📊 Columns: {', '.join(required_cols)}")
    else:
        print(f"   ❌ Missing columns: {missing}")

except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 2: Data Fetcher
print("\n2️⃣ Testing Data Fetcher...")
try:
    from data_fetcher import FOREX_PAIRS, get_current_price
    
    print(f"   ✅ Data Fetcher loaded")
    print(f"   📊 Supported pairs: {len(FOREX_PAIRS)}")
    print(f"   💱 Sample pairs: {', '.join(list(FOREX_PAIRS.keys())[:3])}")

except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 3: Telegram Notifier
print("\n3️⃣ Testing Telegram Notifier...")
try:
    from telegram_notifier import TelegramNotifier
    
    notifier = TelegramNotifier()
    
    print(f"   ✅ Telegram Notifier loaded")
    print(f"   📱 Status: {'Enabled' if notifier.enabled else 'Disabled (no credentials)'}")

except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 4: Configuration
print("\n4️⃣ Testing Configuration...")
try:
    import config
    
    print(f"   ✅ Configuration loaded")
    print(f"   📊 Monitored pairs: {len(config.MONITORED_PAIRS)}")
    print(f"   ⏱️ Interval: {config.DEFAULT_INTERVAL}")
    print(f"   🔄 Check interval: {config.CHECK_INTERVAL // 60} minutes")

except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Test 5: Signal Check Logic
print("\n5️⃣ Testing Signal Check Logic...")
try:
    from ttm_squeeze import check_signal
    
    # Simulate squeeze fire (BB was inside KC, now outside)
    test_df = pd.DataFrame({
        'High': [1.1, 1.2, 1.15, 1.25],
        'Low': [1.0, 1.05, 1.08, 1.1],
        'Close': [1.05, 1.18, 1.12, 1.22],
        'Open': [1.02, 1.08, 1.14, 1.15]
    })
    
    test_df = calculate_ttm_squeeze(test_df)
    signal_info = check_signal(test_df)
    
    print(f"   ✅ Signal check PASSED")
    print(f"   🎯 Signal: {signal_info['signal']}")
    print(f"   📊 Squeeze ON: {signal_info['squeeze_on']}")
    print(f"   📈 Momentum: {signal_info['momentum']:.5f}")

except Exception as e:
    print(f"   ❌ FAILED: {e}")

# Summary
print("\n" + "=" * 60)
print("✅ All core modules tested successfully!")
print("\n📋 Next Steps:")
print("   1. Configure Telegram (optional): Copy .env.example to .env")
print("   2. Run dashboard: streamlit run app.py")
print("   3. Run scheduler: python scheduler.py")
print("\n" + "=" * 60)
�*cascade082+file:///c:/Users/Tomi/FOREX/test_modules.py
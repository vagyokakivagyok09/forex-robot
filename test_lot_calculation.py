"""
Test script for validating the enhanced lot sizing calculation logic.
Tests various scenarios including normal breakouts, narrow SLs, and edge cases.
"""

# Test configuration matching app.py
ACCOUNT_BALANCE = 1_000_000  # HUF
RISK_PERCENT = 0.01  # 1%
MIN_SL_PIPS = 10.0
MAX_MARGIN_PERCENT = 0.20
LEVERAGE = 30
CONTRACT_SIZE = 100000

# Mock HUF rates (approximate)
USD_HUF = 360.0
GBP_HUF = 460.0
EUR_HUF = 390.0

def calculate_lot_size(symbol, box_height, base_huf_rate, usd_huf_rate):
    """Replicated lot calculation logic from app.py"""
    
    # Extract currencies
    base_currency = symbol[:3]
    quote_currency = symbol[3:6]
    
    # Calculate pips risked
    pips_risked = box_height * (100 if "JPY" in symbol else 10000)
    
    # 🛡️ MINIMUM SL PROTECTION
    pips_risked = max(pips_risked, MIN_SL_PIPS)
    
    # Pip value calculation
    pip_value_per_lot = 0
    if quote_currency == 'USD':
        pip_value_per_lot = 10 * usd_huf_rate
    elif quote_currency == 'JPY':
        pip_value_per_lot = 1000 * (usd_huf_rate / 153.0)
    
    # Lot size calculation
    risk_amount = ACCOUNT_BALANCE * RISK_PERCENT
    
    if pip_value_per_lot > 0 and pips_risked > 0:
        lot_size = risk_amount / (pips_risked * pip_value_per_lot)
        lot_size = round(lot_size, 2)
        
        # ✨ DYNAMIC MAXIMUM
        max_lot = min(ACCOUNT_BALANCE / 200_000, 5.0)
        lot_size = max(0.01, min(lot_size, max_lot))
    else:
        lot_size = 0.01
    
    # Calculate pip value for this lot
    pip_value_huf = pip_value_per_lot * lot_size
    
    # Margin calculation
    margin_huf = (CONTRACT_SIZE * lot_size * base_huf_rate) / LEVERAGE
    
    # 📊 MARGIN LIMIT PROTECTION
    max_allowed_margin = ACCOUNT_BALANCE * MAX_MARGIN_PERCENT
    
    if margin_huf > max_allowed_margin:
        lot_size = (max_allowed_margin * LEVERAGE) / (CONTRACT_SIZE * base_huf_rate)
        lot_size = round(lot_size, 2)
        lot_size = max(0.01, lot_size)
        
        # Recalculate
        pip_value_huf = pip_value_per_lot * lot_size
        margin_huf = (CONTRACT_SIZE * lot_size * base_huf_rate) / LEVERAGE
    
    # Expected profit/loss
    pips_gained = pips_risked
    profit_huf = pips_gained * pip_value_huf
    loss_huf = pips_risked * pip_value_huf
    margin_percent = (margin_huf / ACCOUNT_BALANCE) * 100
    
    return {
        'lot_size': lot_size,
        'pips_risked': pips_risked,
        'pip_value_huf': pip_value_huf,
        'margin_huf': margin_huf,
        'margin_percent': margin_percent,
        'profit_huf': profit_huf,
        'loss_huf': loss_huf,
        'risk_amount': risk_amount
    }

def run_tests():
    """Run test scenarios"""
    
    print("=" * 80)
    print("LOT SIZING CALCULATION TESTS - 1M HUF Account")
    print("=" * 80)
    print(f"Account Balance: {ACCOUNT_BALANCE:,} HUF")
    print(f"Risk per Trade: {RISK_PERCENT*100}% = {int(ACCOUNT_BALANCE * RISK_PERCENT):,} HUF")
    print(f"Min SL Protection: {MIN_SL_PIPS} pips")
    print(f"Max Lot Limit: {ACCOUNT_BALANCE / 200_000:.1f} lot")
    print(f"Max Margin: {MAX_MARGIN_PERCENT*100}% = {int(ACCOUNT_BALANCE * MAX_MARGIN_PERCENT):,} HUF")
    print("=" * 80)
    print()
    
    test_cases = [
        # (symbol, box_height, description)
        ("GBPUSD=X", 0.0030, "Normal London breakout"),
        ("GBPJPY=X", 0.50, "JPY pair normal"),
        ("EURUSD=X", 0.0015, "Narrow SL (15 pips)"),
        ("GBPUSD=X", 0.0005, "Extreme narrow SL (5 pips - should use MIN 10)"),
        ("GBPUSD=X", 0.0100, "Wide SL (100 pips)"),
    ]
    
    for symbol, box_height, description in test_cases:
        base_currency = symbol[:3]
        
        # Get base HUF rate
        if base_currency == 'GBP':
            base_huf_rate = GBP_HUF
        elif base_currency == 'EUR':
            base_huf_rate = EUR_HUF
        else:
            base_huf_rate = USD_HUF
        
        result = calculate_lot_size(symbol, box_height, base_huf_rate, USD_HUF)
        
        print(f"TEST: {description}")
        print(f"Symbol: {symbol} | Box Height: {box_height:.4f}")
        print(f"-" * 80)
        print(f"  📊 Lot Size: {result['lot_size']:.2f}")
        print(f"  🛡️ Pips Risked: {result['pips_risked']:.1f} (original: {box_height * (100 if 'JPY' in symbol else 10000):.1f})")
        print(f"  💵 Kockáztatott: {int(result['risk_amount']):,} HUF")
        print(f"  🏦 Margin: {int(result['margin_huf']):,} HUF ({result['margin_percent']:.1f}%)")
        print(f"  🎯 Várható Nyerő: +{int(result['profit_huf']):,} HUF")
        print(f"  🔴 Max Bukó: -{int(result['loss_huf']):,} HUF")
        
        # Validation checks
        checks = []
        if result['lot_size'] >= 0.01 and result['lot_size'] <= 5.0:
            checks.append("✅ Lot within limits (0.01-5.0)")
        else:
            checks.append("❌ Lot OUT OF RANGE!")
        
        if result['margin_percent'] <= 20.0:
            checks.append("✅ Margin ≤ 20%")
        else:
            checks.append("❌ Margin EXCEEDED 20%!")
        
        if result['pips_risked'] >= MIN_SL_PIPS:
            checks.append("✅ Min SL protection active")
        else:
            checks.append("❌ Min SL not applied!")
        
        if abs(result['loss_huf'] - result['risk_amount']) < 1000:  # Allow 1000 HUF tolerance
            checks.append("✅ Loss matches risk amount")
        else:
            checks.append(f"⚠️  Loss ({int(result['loss_huf']):,}) differs from risk ({int(result['risk_amount']):,})")
        
        print(f"\n  Validations:")
        for check in checks:
            print(f"    {check}")
        
        print()
        print("=" * 80)
        print()

if __name__ == "__main__":
    run_tests()
    
    print("\n🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Review the test results above")
    print("2. Verify lot sizes make sense for each scenario")
    print("3. Run the actual Streamlit app: streamlit run app.py")
    print("4. Wait for a real breakout signal to test live")

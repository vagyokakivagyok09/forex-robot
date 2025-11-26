�,"""
Automated Scheduler for TTM Squeeze Monitoring

Periodically checks for signals and sends Telegram notifications
Can run as a background process for 24/7 monitoring
"""

import time
import schedule
from datetime import datetime

# Import custom modules
from ttm_squeeze import calculate_ttm_squeeze, check_signal
from data_fetcher import get_all_pairs_data
from telegram_notifier import TelegramNotifier
import config


# Initialize Telegram notifier
notifier = TelegramNotifier()


# Track sent signals to avoid duplicates
sent_signals = {}


def check_and_notify():
    """
    Check all pairs for signals and send Telegram notifications
    """
    print(f"\n{'='*60}")
    print(f"🔍 Checking for signals at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Fetch data for all monitored pairs
    data = get_all_pairs_data(
        pairs=config.MONITORED_PAIRS,
        interval=config.DEFAULT_INTERVAL,
        candles=config.CANDLES_TO_FETCH
    )
    
    if not data:
        print("❌ Failed to fetch data")
        return
    
    signals_found = 0
    
    for pair, df in data.items():
        if df.empty:
            continue
        
        # Calculate TTM Squeeze
        df_with_indicators = calculate_ttm_squeeze(
            df,
            bb_period=config.BB_PERIOD,
            bb_std=config.BB_STD_DEV,
            kc_period=config.KC_PERIOD,
            kc_atr_mult=config.KC_ATR_MULTIPLIER
        )
        
        # Check for signal
        signal_info = check_signal(df_with_indicators)
        
        signal = signal_info['signal']
        price = signal_info['price']
        momentum = signal_info['momentum']
        squeeze_on = signal_info['squeeze_on']
        
        # Create unique key for this signal
        signal_key = f"{pair}_{signal}_{datetime.now().strftime('%Y-%m-%d')}"
        
        # Only send notification if signal is BUY or SELL and we haven't sent it today
        if signal in ['BUY', 'SELL']:
            if signal_key not in sent_signals:
                print(f"🚨 {signal} SIGNAL: {pair} @ {price:.5f}")
                
                # Send Telegram notification
                if config.ENABLE_NOTIFICATIONS:
                    success = notifier.send_signal_alert(
                        signal_type=signal,
                        symbol=pair,
                        price=price,
                        momentum=momentum,
                        squeeze_on=squeeze_on
                    )
                    
                    if success:
                        sent_signals[signal_key] = datetime.now()
                        print(f"✅ Telegram notification sent")
                    else:
                        print(f"❌ Failed to send notification")
                
                signals_found += 1
            else:
                print(f"⏭️ {pair}: {signal} signal already sent today")
        else:
            squeeze_status = "ON" if squeeze_on else "OFF"
            print(f"⏸️ {pair}: WAIT (Squeeze: {squeeze_status}, Momentum: {momentum:.5f})")
    
    print(f"\n📊 Summary: {signals_found} new signals found")
    print(f"{'='*60}\n")


def cleanup_old_signals():
    """
    Clean up sent_signals dictionary to prevent memory buildup
    Removes signals older than 24 hours
    """
    global sent_signals
    
    now = datetime.now()
    to_remove = []
    
    for key, timestamp in sent_signals.items():
        # Remove signals older than 24 hours
        if (now - timestamp).total_seconds() > 86400:
            to_remove.append(key)
    
    for key in to_remove:
        del sent_signals[key]
    
    if to_remove:
        print(f"🧹 Cleaned up {len(to_remove)} old signals")


def send_startup_notification():
    """Send notification when scheduler starts"""
    if config.TELEGRAM_ENABLED:
        notifier.send_message(
            f"🤖 TTM Squeeze Bot Started\n\n"
            f"Monitoring {len(config.MONITORED_PAIRS)} pairs\n"
            f"Check interval: {config.CHECK_INTERVAL // 60} minutes\n"
            f"Timeframe: {config.DEFAULT_INTERVAL}\n\n"
            f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )


def run_scheduler():
    """
    Main scheduler function
    Runs checks at configured intervals
    """
    print("🚀 TTM Squeeze Scheduler Started")
    print(f"📊 Monitoring {len(config.MONITORED_PAIRS)} pairs")
    print(f"⏰ Check interval: {config.CHECK_INTERVAL // 60} minutes")
    print(f"📈 Timeframe: {config.DEFAULT_INTERVAL}")
    print(f"{'='*60}\n")
    
    # Send startup notification
    send_startup_notification()
    
    # Schedule checks
    schedule.every(config.CHECK_INTERVAL // 60).minutes.do(check_and_notify)
    
    # Schedule daily cleanup (runs at midnight)
    schedule.every().day.at("00:00").do(cleanup_old_signals)
    
    # Run first check immediately
    check_and_notify()
    
    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute if any scheduled task should run
    
    except KeyboardInterrupt:
        print("\n⚠️ Scheduler stopped by user")
        
        if config.TELEGRAM_ENABLED:
            notifier.send_message(
                f"🛑 TTM Squeeze Bot Stopped\n\n"
                f"Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )


if __name__ == "__main__":
    run_scheduler()
�,*cascade082(file:///c:/Users/Tomi/FOREX/scheduler.py
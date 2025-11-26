ÿ!"""
Application Configuration

Central configuration file for TTM Squeeze trading app
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to load from Streamlit secrets (for cloud deployment)
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'TELEGRAM' in st.secrets:
        # Running on Streamlit Cloud - read from secrets
        TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM"]["TELEGRAM_BOT_TOKEN"]
        TELEGRAM_CHAT_ID = st.secrets["TELEGRAM"]["TELEGRAM_CHAT_ID"]
    else:
        # Local environment - read from .env
        TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
        TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
except Exception as e:
    # Fallback to environment variables
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Enable Telegram if credentials are present
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)


# ============================================================================
# TRADING CONFIGURATION
# ============================================================================

# Forex pairs to monitor
MONITORED_PAIRS = [
    'EURUSD',
    'GBPUSD',
    'USDJPY',
    'GBPJPY',
    'AUDUSD'
]

# Timeframe settings
DEFAULT_INTERVAL = '1h'  # Options: '5m', '15m', '30m', '1h', '4h', '1d'
CANDLES_TO_FETCH = 100   # Number of historical candles


# ============================================================================
# TTM SQUEEZE INDICATOR PARAMETERS
# ============================================================================

# Bollinger Bands settings
BB_PERIOD = 20
BB_STD_DEV = 2.0

# Keltner Channels settings
KC_PERIOD = 20
KC_ATR_MULTIPLIER = 1.5

# Momentum settings
MOMENTUM_PERIOD = 20


# ============================================================================
# SCHEDULER CONFIGURATION
# ============================================================================

# How often to check for signals (in seconds)
CHECK_INTERVAL = 900  # 15 minutes (900 seconds)

# Enable/disable notifications
ENABLE_NOTIFICATIONS = True


# ============================================================================
# UI CONFIGURATION
# ============================================================================

# Streamlit refresh interval (seconds)
STREAMLIT_REFRESH_INTERVAL = 15

# Chart settings
SHOW_TRADINGVIEW_CHARTS = True


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True
LOG_FILE_PATH = 'ttm_squeeze.log'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_config_summary():
    """Get a summary of current configuration"""
    return {
        'pairs': MONITORED_PAIRS,
        'interval': DEFAULT_INTERVAL,
        'bb_period': BB_PERIOD,
        'kc_period': KC_PERIOD,
        'telegram_enabled': TELEGRAM_ENABLED,
        'check_interval': CHECK_INTERVAL
    }


def validate_config():
    """Validate configuration and warn about missing settings"""
    warnings = []
    
    if not MONITORED_PAIRS:
        warnings.append("‚ö†Ô∏è No forex pairs configured for monitoring")
    
    if not TELEGRAM_ENABLED:
        warnings.append("‚ö†Ô∏è Telegram notifications disabled (missing credentials)")
    
    if CHECK_INTERVAL < 60:
        warnings.append("‚ö†Ô∏è Check interval is very short (<1 min), may cause API rate limits")
    
    return warnings


# Print configuration on import
if __name__ == "__main__":
    print("üìã TTM Squeeze Configuration\n")
    
    config = get_config_summary()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print("\nüîç Validation:")
    warnings = validate_config()
    if warnings:
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("  ‚úÖ Configuration valid")
Ω *cascade08Ωπ *cascade08π÷*cascade08÷˝ *cascade08˝ë*cascade08ë∫ *cascade08∫ª*cascade08ª≈ *cascade08≈«*cascade08«€ *cascade08€‹*cascade08‹É *cascade08ÉÑ*cascade08Ñé *cascade08éê*cascade08ê¢ *cascade08¢£*cascade08£À *cascade08À‹*cascade08‹‰ *cascade08‰Û*cascade08Ûô *cascade08ôú *cascade08ú°*cascade08°£ *cascade08£•*cascade08•¶ *cascade08¶ß*cascade08ßØ *cascade08Ø±*cascade08±∫ *cascade08∫º*cascade08ºæ *cascade08æ¿*cascade08¿ﬂ *cascade08ﬂ≤*cascade08≤ÿ! *cascade082%file:///c:/Users/Tomi/FOREX/config.py
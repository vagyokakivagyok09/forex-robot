£-"""
TTM Squeeze Indicator Calculation Module

Implements the TTM Squeeze strategy logic:
- Bollinger Bands (20, 2.0)
- Keltner Channels (20, 1.5 ATR)
- Squeeze Detection (BB inside KC)
- Momentum Oscillator
- Signal Generation (BUY/SELL/WAIT)
"""

import pandas as pd
import numpy as np


def calculate_bollinger_bands(df, period=20, std_dev=2.0):
    """
    Calculate Bollinger Bands
    
    Args:
        df: DataFrame with 'Close' column
        period: SMA period (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
    
    Returns:
        DataFrame with BB_Upper, BB_Lower, BB_Middle columns
    """
    df['BB_Middle'] = df['Close'].rolling(window=period).mean()
    std = df['Close'].rolling(window=period).std()
    df['BB_Upper'] = df['BB_Middle'] + (std_dev * std)
    df['BB_Lower'] = df['BB_Middle'] - (std_dev * std)
    
    return df


def calculate_keltner_channels(df, period=20, atr_multiplier=1.5):
    """
    Calculate Keltner Channels
    
    Args:
        df: DataFrame with 'High', 'Low', 'Close' columns
        period: EMA period (default: 20)
        atr_multiplier: ATR multiplier (default: 1.5)
    
    Returns:
        DataFrame with KC_Upper, KC_Lower, KC_Middle columns
    """
    # Calculate True Range
    df['TR'] = np.maximum(
        df['High'] - df['Low'],
        np.maximum(
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        )
    )
    
    # Calculate ATR (Average True Range)
    df['ATR'] = df['TR'].rolling(window=period).mean()
    
    # Calculate Keltner Channels
    df['KC_Middle'] = df['Close'].rolling(window=period).mean()
    df['KC_Upper'] = df['KC_Middle'] + (atr_multiplier * df['ATR'])
    df['KC_Lower'] = df['KC_Middle'] - (atr_multiplier * df['ATR'])
    
    return df


def calculate_momentum(df, period=20):
    """
    Calculate Momentum Oscillator
    
    Uses linear regression based approach to measure momentum
    
    Args:
        df: DataFrame with 'Close' column
        period: Lookback period (default: 20)
    
    Returns:
        DataFrame with 'Momentum' column
    """
    # Simplified momentum: Close vs SMA
    sma = df['Close'].rolling(window=period).mean()
    df['Momentum'] = df['Close'] - sma
    
    return df


def calculate_ttm_squeeze(df, bb_period=20, bb_std=2.0, kc_period=20, kc_atr_mult=1.5):
    """
    Calculate complete TTM Squeeze indicator
    
    Args:
        df: DataFrame with OHLC data
        bb_period: Bollinger Bands period
        bb_std: Bollinger Bands standard deviation
        kc_period: Keltner Channels period
        kc_atr_mult: Keltner Channels ATR multiplier
    
    Returns:
        DataFrame with all TTM Squeeze indicators
    """
    # Calculate Bollinger Bands
    df = calculate_bollinger_bands(df, period=bb_period, std_dev=bb_std)
    
    # Calculate Keltner Channels
    df = calculate_keltner_channels(df, period=kc_period, atr_multiplier=kc_atr_mult)
    
    # Calculate Momentum
    df = calculate_momentum(df, period=20)
    
    # Detect Squeeze: BB inside KC
    df['Squeeze_On'] = (df['BB_Upper'] < df['KC_Upper']) & (df['BB_Lower'] > df['KC_Lower'])
    
    return df


def check_signal(df):
    """
    Check for BUY/SELL signals based on TTM Squeeze
    
    Signal conditions:
    - Squeeze FIRE: Previous candle had Squeeze ON, current candle has Squeeze OFF
    - Direction: Determined by Momentum
      - BUY: Momentum > 0 (positive)
      - SELL: Momentum < 0 (negative)
    
    Args:
        df: DataFrame with TTM Squeeze indicators
    
    Returns:
        dict with signal info: {
            'signal': 'BUY' | 'SELL' | 'WAIT',
            'squeeze_on': bool,
            'momentum': float,
            'price': float
        }
    """
    if len(df) < 2:
        return {
            'signal': 'WAIT',
            'squeeze_on': False,
            'momentum': 0,
            'price': 0
        }
    
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    # Check for Squeeze FIRE (transition from ON to OFF)
    squeeze_fire = prev_row['Squeeze_On'] and not last_row['Squeeze_On']
    
    signal = 'WAIT'
    
    if squeeze_fire:
        # Determine direction based on momentum
        if last_row['Momentum'] > 0:
            signal = 'BUY'
        elif last_row['Momentum'] < 0:
            signal = 'SELL'
    
    return {
        'signal': signal,
        'squeeze_on': bool(last_row['Squeeze_On']),
        'momentum': float(last_row['Momentum']),
        'price': float(last_row['Close']),
        'bb_upper': float(last_row['BB_Upper']),
        'bb_lower': float(last_row['BB_Lower']),
        'kc_upper': float(last_row['KC_Upper']),
        'kc_lower': float(last_row['KC_Lower'])
    }


def get_squeeze_status(df):
    """
    Get current squeeze status without signal generation
    
    Args:
        df: DataFrame with TTM Squeeze indicators
    
    Returns:
        dict with current status
    """
    if len(df) < 1:
        return {
            'squeeze_on': False,
            'momentum': 0,
            'momentum_direction': 'NEUTRAL',
            'price': 0
        }
    
    last_row = df.iloc[-1]
    
    momentum_direction = 'NEUTRAL'
    if last_row['Momentum'] > 0:
        momentum_direction = 'POSITIVE'
    elif last_row['Momentum'] < 0:
        momentum_direction = 'NEGATIVE'
    
    return {
        'squeeze_on': bool(last_row['Squeeze_On']),
        'momentum': float(last_row['Momentum']),
        'momentum_direction': momentum_direction,
        'price': float(last_row['Close'])
    }
£-*cascade082*file:///c:/Users/Tomi/FOREX/ttm_squeeze.py
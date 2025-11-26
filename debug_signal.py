
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- KONSTANSOK ---
TARGET_PAIRS = ['GBPUSD=X', 'GBPJPY=X', 'EURUSD=X']
BUFFER_PIPS = 0.0003

def get_data(ticker):
    """Adatok letöltése (15 perces, 5 napra)."""
    try:
        # 5 nap elég a debugoláshoz
        df = yf.download(ticker, period="5d", interval="15m", progress=False)
        if df.empty:
            return None
        
        # --- FIX: Flatten MultiIndex (yfinance update compatibility) ---
        if isinstance(df.columns, pd.MultiIndex):
            # Try to extract the specific ticker level
            if ticker in df.columns.get_level_values(1):
                df = df.xs(ticker, axis=1, level=1)
            # Or just take the first level if 'Close' is there
            elif 'Close' in df.columns.get_level_values(0):
                 pass 

        # If still MultiIndex, try to just get 'Close'
        if isinstance(df.columns, pd.MultiIndex):
             try: 
                 df = df['Close']
                 if isinstance(df, pd.Series):
                     df = df.to_frame(name='Close')
             except KeyError: pass
        
        # Ensure we have a simple DataFrame with 'Close'
        if isinstance(df, pd.Series):
            df = df.to_frame(name='Close')
            
        if 'Close' not in df.columns and df.shape[1] == 1:
            df.columns = ['Close']

        # Időzóna kezelés (Yfinance néha UTC-t ad, néha mást - normalizáljuk)
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        else:
            df.index = df.index.tz_convert('UTC')
            
        return df
    except Exception as e:
        print(f"Hiba az adatok letöltésekor ({ticker}): {e}")
        return None

def calculate_ema(df, span=50):
    """Exponenciális Mozgóátlag számítása."""
    return df['Close'].ewm(span=span, adjust=False).mean()

def analyze_london_breakout(df, symbol):
    """
    A London Breakout stratégia logikája.
    """
    print(f"\n--- Elemzés: {symbol} ---")
    
    # Aktuális dátum meghatározása
    last_candle_time = df.index[-1]
    today_str = last_candle_time.strftime('%Y-%m-%d')
    print(f"Utolsó gyertya: {last_candle_time}")
    
    # Szűrés a mai napra és a 07:00-08:00 GMT időszakra
    # Megjegyzés: A pandas szeletelésnél az óra a kezdést jelöli
    # Fontos: Ellenőrizzük a dátumot is, hogy biztosan MAI adatot nézünk
    target_date = datetime.utcnow().date()
    # Debug: Force target date to match data if needed, but for now use UTC now
    print(f"Cél dátum (UTC): {target_date}")

    morning_mask = (df.index.date == target_date) & (df.index.hour == 7) 
    morning_candles = df[morning_mask]

    if morning_candles.empty:
        print("NINCS adat a mai reggelről (07:00-08:00 GMT).")
        # Nézzük meg mi van helyette
        today_data = df[df.index.date == target_date]
        if not today_data.empty:
            print("Mai adatok elérhető órái:", today_data.index.hour.unique().tolist())
        else:
            print("Egyáltalán nincs mai adat.")
        return None 

    print(f"Reggeli gyertyák száma: {len(morning_candles)}")

    # Doboz meghatározása (Wick-to-Wick)
    box_high = float(morning_candles['High'].max())
    box_low = float(morning_candles['Low'].min())
    box_height = box_high - box_low
    
    print(f"Box High: {box_high:.5f}")
    print(f"Box Low: {box_low:.5f}")
    
    # Aktuális ár és EMA
    current_price = df['Close'].iloc[-1]
    if isinstance(current_price, pd.Series):
        current_price = current_price.iloc[0]
    current_price = float(current_price)

    ema_50 = df['EMA_50'].iloc[-1]
    if isinstance(ema_50, pd.Series):
        ema_50 = ema_50.iloc[0]
    ema_50 = float(ema_50)
    
    print(f"Jelenlegi ár: {current_price:.5f}")
    print(f"EMA 50: {ema_50:.5f}")
    
    # Trend meghatározása
    trend = "BULLISH" if current_price > ema_50 else "BEARISH"
    print(f"Trend: {trend}")
    
    # Trigger logika
    if trend == "BULLISH":
        entry_price = box_high + BUFFER_PIPS
        print(f"Long Belépő lenne: {entry_price:.5f}")
        if current_price > entry_price:
            print(">>> JELZÉS: LONG")
        else:
            print(f"Nincs jelzés. Ár ({current_price:.5f}) <= Belépő ({entry_price:.5f})")
            
    elif trend == "BEARISH":
        entry_price = box_low - BUFFER_PIPS
        print(f"Short Belépő lenne: {entry_price:.5f}")
        if current_price < entry_price:
            print(">>> JELZÉS: SHORT")
        else:
            print(f"Nincs jelzés. Ár ({current_price:.5f}) >= Belépő ({entry_price:.5f})")

def main():
    print("Debug Script Indítása...")
    for symbol in TARGET_PAIRS:
        df = get_data(symbol)
        if df is not None:
            df['EMA_50'] = calculate_ema(df)
            analyze_london_breakout(df, symbol)
        else:
            print(f"Nem sikerült letölteni: {symbol}")

if __name__ == "__main__":
    main()

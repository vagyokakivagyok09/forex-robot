’Ãimport streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import time
import requests
import json
import os

# --- FELHASZNÃLÃ“I KONFIGURÃCIÃ“ ---
# CserÃ©ld le a sajÃ¡todra, ha szÃ¼ksÃ©ges!
TELEGRAM_BOT_TOKEN = "7487229026:AAH51YJ4atFsvqHKfQj9l_QU7ytJMIwo0w0" 
TELEGRAM_CHAT_ID = "1736205722"

# --- KONSTANSOK Ã‰S BEÃLLÃTÃSOK ---
TARGET_PAIRS = ['GBPUSD=X', 'GBPJPY=X', 'EURUSD=X']
BUFFER_PIPS = 0.0003 # Kb. 3 pip puffer a doboz szÃ©leihez
RISK_PER_TRADE = 0.005 # 0.5% kockÃ¡zat (pÃ©lda)
HISTORY_FILE = os.path.join(os.getcwd(), "trade_history.json")

# Az oldal beÃ¡llÃ­tÃ¡sa
st.set_page_config(page_title="London Breakout Pro", layout="wide")

# --- SEGÃ‰DFÃœGGVÃ‰NYEK ---

def load_history():
    """BetÃ¶lti a korÃ¡bbi jelzÃ©seket a JSON fÃ¡jlbÃ³l."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Hiba a betÃ¶ltÃ©skor: {e}")
            return {}
    return {}

def save_history(history):
    """Elmenti a jelzÃ©seket a JSON fÃ¡jlba."""
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    except Exception as e:
        st.error(f"Hiba a mentÃ©skor: {e}")

def send_telegram(message):
    """Ãœzenet kÃ¼ldÃ©se a Telegram Bot API-n keresztÃ¼l."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Telegram hiba: {e}")
        return False

@st.cache_data(ttl=3600) # Ã“rÃ¡nkÃ©nt elÃ©g frissÃ­teni az Ã¡rfolyamokat
def get_huf_rate(base_currency):
    """
    LekÃ©ri az aktuÃ¡lis HUF Ã¡rfolyamot a megadott devizÃ¡hoz.
    TÃ¡mogatott: EUR, USD, GBP.
    """
    ticker_map = {
        'EUR': 'EURHUF=X',
        'USD': 'USDHUF=X',
        'GBP': 'GBPHUF=X'
    }
    
    ticker = ticker_map.get(base_currency)
    if not ticker:
        return None
        
    try:
        df = yf.download(ticker, period="1d", interval="1d", progress=False)
        if not df.empty:
            # Flatten MultiIndex if present
            if isinstance(df.columns, pd.MultiIndex):
                try:
                    df = df.xs(ticker, axis=1, level=1)
                except KeyError:
                    pass
            
            if 'Close' in df.columns:
                val = df['Close'].iloc[-1]
                if isinstance(val, pd.Series):
                    val = val.iloc[0]
                return float(val)
    except Exception:
        pass
    return None

@st.cache_data(ttl=60) # GyorsÃ­tÃ³tÃ¡r 60 mÃ¡sodpercig
def get_data(ticker):
    """Adatok letÃ¶ltÃ©se (15 perces, 59 napra)."""
    try:
        df = yf.download(ticker, period="59d", interval="15m", progress=False)
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

        # IdÅ‘zÃ³na kezelÃ©s (Yfinance nÃ©ha UTC-t ad, nÃ©ha mÃ¡st - normalizÃ¡ljuk)
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        else:
            df.index = df.index.tz_convert('UTC')
            
        return df
    except Exception as e:
        st.error(f"Hiba az adatok letÃ¶ltÃ©sekor ({ticker}): {e}")
        return None

def calculate_ema(df, span=50):
    """ExponenciÃ¡lis MozgÃ³Ã¡tlag szÃ¡mÃ­tÃ¡sa."""
    return df['Close'].ewm(span=span, adjust=False).mean()

def analyze_london_breakout(df, symbol):
    """
    A London Breakout stratÃ©gia logikÃ¡ja.
    1. Megkeresi a mai 07:00-08:00 GMT sÃ¡vot.
    2. MeghatÃ¡rozza a trendet (EMA 50).
    3. KiszÃ¡molja a belÃ©pÅ‘t, stopot, cÃ©lt.
    """
    # AktuÃ¡lis dÃ¡tum meghatÃ¡rozÃ¡sa
    last_candle_time = df.index[-1]
    today_str = last_candle_time.strftime('%Y-%m-%d')
    
    # SzÅ±rÃ©s a mai napra Ã©s a 07:00-08:00 GMT idÅ‘szakra
    # MegjegyzÃ©s: A pandas szeletelÃ©snÃ©l az Ã³ra a kezdÃ©st jelÃ¶li
    morning_mask = (df.index.date == last_candle_time.date()) & (df.index.hour == 7) 
    morning_candles = df[morning_mask]

    if morning_candles.empty:
        return None # MÃ©g nincs adat a mai reggelrÅ‘l (pl. Ã©jfÃ©l van)

    # Doboz meghatÃ¡rozÃ¡sa (Wick-to-Wick)
    # --- FIX: Ensure scalar values (float) ---
    box_high = float(morning_candles['High'].max())
    box_low = float(morning_candles['Low'].min())
    box_height = box_high - box_low
    
    # AktuÃ¡lis Ã¡r Ã©s EMA
    # --- FIX: Ensure scalar values using .item() or float() ---
    current_price = df['Close'].iloc[-1]
    if isinstance(current_price, pd.Series):
        current_price = current_price.iloc[0]
    current_price = float(current_price)

    ema_50 = df['EMA_50'].iloc[-1]
    if isinstance(ema_50, pd.Series):
        ema_50 = ema_50.iloc[0]
    ema_50 = float(ema_50)
    
    # Trend meghatÃ¡rozÃ¡sa
    trend = "BULLISH" if current_price > ema_50 else "BEARISH"
    
    # Szintek szÃ¡mÃ­tÃ¡sa
    result = {
        "box_high": box_high,
        "box_low": box_low,
        "box_height": box_height,
        "trend": trend,
        "current_price": current_price,
        "entry": None,
        "sl": None,
        "tp": None,
        "signal_type": None # LONG vagy SHORT
    }
    
    # Trigger logika (Hougaard-fÃ©le trendszÅ±rÃ©s)
    if trend == "BULLISH":
        # Csak LONG lehet
        entry_price = box_high + BUFFER_PIPS
        if current_price > entry_price:
            result["signal_type"] = "LONG"
            result["entry"] = entry_price
            result["sl"] = box_low
            result["tp"] = entry_price + box_height # 1:1 CÃ©lÃ¡r
            
    elif trend == "BEARISH":
        # Csak SHORT lehet
        entry_price = box_low - BUFFER_PIPS
        if current_price < entry_price:
            result["signal_type"] = "SHORT"
            result["entry"] = entry_price
            result["sl"] = box_high
            result["tp"] = entry_price - box_height # 1:1 CÃ©lÃ¡r

    return result

# --- FÅ ALKALMAZÃS ---

def main():
    # Logo megjelenÃ­tÃ©se
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
    
    st.title("ğŸ‡¬ğŸ‡§ London Breakout Pro Dashboard")
    st.caption("3 EszkÃ¶z SzimultÃ¡n FigyelÃ©se (07:00-08:00 GMT + EMA 50)")
    
    # Session State inicializÃ¡lÃ¡sa (VÃ©di az automatikus frissÃ­tÃ©st)
    # AlapbÃ³l mindig auto_refresh mÃ³dban vagyunk - NEM kÃ¼ld Ãºj jelzÃ©seket napkÃ¶zben
    if 'auto_refresh_mode' not in st.session_state:
        st.session_state.auto_refresh_mode = True
    
    # Automatikus frissÃ­tÃ©s idÅ‘zÃ­tÅ‘ megjelenÃ­tÃ©se
    placeholder = st.empty()
    refresh_interval = 30  # mÃ¡sodperc

    # MemÃ³ria inicializÃ¡lÃ¡sa (FÃ¡jlbÃ³l)
    daily_signals = load_history()
    # StruktÃºra: {'GBPUSD=X': {'date': '2025-11-24', 'timestamp': '2025-11-24 10:30:00', 'direction': 'LONG', 'entry': 1.25, 'tp': 1.26, 'sl': 1.24, 'status': 'open'}, ..., '_meta': {'last_weekly_report': '2025-11-24'}}
    
    # --- TELJESÃTMÃ‰NYSTATISZTIKÃK (Dashboard) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("ğŸ“Š TeljesÃ­tmÃ©ny Ã–sszegzÅ‘")
    
    # Helper function to get week start (Monday) and end (Sunday)
    def get_week_range(date):
        """MeghatÃ¡rozza a hÃ©t kezdetÃ©t (hÃ©tfÅ‘) Ã©s vÃ©gÃ©t (vasÃ¡rnap) egy adott dÃ¡tumhoz."""
        weekday = date.weekday()  # 0=HÃ©tfÅ‘, 6=VasÃ¡rnap
        week_start = date - timedelta(days=weekday)
        week_end = week_start + timedelta(days=6)
        return week_start, week_end
    
    # AktuÃ¡lis hÃ©t hatÃ¡rainak meghatÃ¡rozÃ¡sa
    now = datetime.utcnow()
    current_week_start, current_week_end = get_week_range(now.date())
    
    # StatisztikÃ¡k szÃ¡mÃ­tÃ¡sa (ALL TIME)
    total_trades = 0
    wins = 0
    losses = 0
    open_trades = 0
    total_pips = 0.0
    total_huf = 0.0
    
    # Heti statisztikÃ¡k (Current Week Only)
    weekly_trades = 0
    weekly_wins = 0
    weekly_losses = 0
    weekly_pips = 0.0
    weekly_huf = 0.0
    
    for symbol, data in daily_signals.items():
        if symbol.startswith('_'):  # Skip metadata
            continue
        status = data.get('status')
        
        # EllenÅ‘rizzÃ¼k, hogy az aktuÃ¡lis hÃ©ten zÃ¡rult-e le
        trade_date_str = data.get('date')
        is_current_week = False
        if trade_date_str:
            try:
                trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d').date()
                is_current_week = current_week_start <= trade_date <= current_week_end
            except:
                pass
        
        # ALL TIME stats
        if status == 'tp_hit':
            wins += 1
            total_trades += 1
            total_pips += data.get('pips_result', 0)
            total_huf += data.get('huf_result', 0)
            
            # Weekly stats
            if is_current_week:
                weekly_wins += 1
                weekly_trades += 1
                weekly_pips += data.get('pips_result', 0)
                weekly_huf += data.get('huf_result', 0)
                
        elif status == 'sl_hit':
            losses += 1
            total_trades += 1
            total_pips += data.get('pips_result', 0)  # mÃ¡r negatÃ­v
            total_huf += data.get('huf_result', 0)  # mÃ¡r negatÃ­v
            
            # Weekly stats
            if is_current_week:
                weekly_losses += 1
                weekly_trades += 1
                weekly_pips += data.get('pips_result', 0)
                weekly_huf += data.get('huf_result', 0)
                
        elif status == 'open':
            open_trades += 1
    
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    weekly_win_rate = (weekly_wins / weekly_trades * 100) if weekly_trades > 0 else 0
    
    # Napi aktuÃ¡lis P/L szÃ¡mÃ­tÃ¡s (nyitott pozÃ­ciÃ³k)
    daily_current_pips = 0.0
    daily_current_huf = 0.0
    
    for symbol, data in daily_signals.items():
        if symbol.startswith('_'):  # Skip metadata
            continue
        if data.get('status') == 'open':
            # Friss Ã¡r lekÃ©rÃ©se
            df_current = get_data(symbol)
            if df_current is not None and not df_current.empty:
                current_price = float(df_current['Close'].iloc[-1])
                
                direction = data.get('direction')
                entry_price = data.get('entry')
                pip_value_huf = data.get('pip_value_huf', 0)
                
                # SzÃ¡mÃ­tsuk ki a jelenlegi P/L-t
                pip_multiplier = 100 if "JPY" in symbol else 10000
                
                if direction == 'LONG':
                    pips_current = (current_price - entry_price) * pip_multiplier
                else:  # SHORT
                    pips_current = (entry_price - current_price) * pip_multiplier
                
                huf_current = pips_current * pip_value_huf
                
                daily_current_pips += pips_current
                daily_current_huf += huf_current
    
    # MegjelenÃ­tÃ©s
    st.sidebar.metric("Ã–sszes Trade", total_trades)
    col1, col2 = st.sidebar.columns(2)
    col1.metric("NyerÅ‘ âœ…", wins)
    col2.metric("VesztÅ‘ âŒ", losses)
    st.sidebar.metric("NyerÃ©si ArÃ¡ny", f"{win_rate:.1f}%")
    
    # Pip Ã©s HUF Ã¶sszegzÃ©s (All Time)
    pip_color = "normal" if total_pips >= 0 else "inverse"
    huf_color = "normal" if total_huf >= 0 else "inverse"
    st.sidebar.metric("Ã–sszes Pip", f"{total_pips:+.1f}", delta=None)
    st.sidebar.metric("Ã–sszes Profit/Loss", f"{int(total_huf):+,} Ft", delta=None)
    
    # Napi aktuÃ¡lis P/L (csak ha van nyitott pozÃ­ciÃ³)
    if open_trades > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ğŸ“Š Mai Napi AktuÃ¡lis ÃllÃ¡s")
        current_pl_delta_style = "normal" if daily_current_huf >= 0 else "inverse"
        st.sidebar.metric(
            "ğŸ’° Napi AktuÃ¡lis P/L", 
            f"{int(daily_current_huf):+,} Ft",
            delta=f"{daily_current_pips:+.1f} pip"
        )
    
    # Nyitott pozÃ­ciÃ³k rÃ©szletes megjelenÃ­tÃ©se
    if open_trades > 0:
        with st.sidebar.expander(f"ğŸ”„ {open_trades} nyitott pozÃ­ciÃ³ - Kattints a rÃ©szletekÃ©rt!", expanded=False):
            for symbol, data in daily_signals.items():
                if symbol.startswith('_'):  # Skip metadata
                    continue
                if data.get('status') == 'open':
                    # Friss Ã¡r lekÃ©rÃ©se
                    df_current = get_data(symbol)
                    if df_current is not None and not df_current.empty:
                        current_price = float(df_current['Close'].iloc[-1])
                        
                        direction = data.get('direction')
                        entry_price = data.get('entry')
                        tp_price = data.get('tp')
                        sl_price = data.get('sl')
                        pip_value_huf = data.get('pip_value_huf', 0)
                        
                        # SzÃ¡mÃ­tsuk ki a jelenlegi P/L-t
                        pip_multiplier = 100 if "JPY" in symbol else 10000
                        
                        if direction == 'LONG':
                            pips_current = (current_price - entry_price) * pip_multiplier
                        else:  # SHORT
                            pips_current = (entry_price - current_price) * pip_multiplier
                        
                        huf_current = pips_current * pip_value_huf
                        
                        # SzÃ­nes megjelenÃ­tÃ©s profit/loss alapjÃ¡n
                        color = "ğŸŸ¢" if pips_current >= 0 else "ğŸ”´"
                        direction_label = "LONG/vÃ©tel" if direction == "LONG" else "SHORT/eladÃ¡s"
                        
                        st.markdown(f"**{color} {symbol}** - {direction_label}")
                        st.caption(f"BelÃ©pÅ‘: {entry_price:.5f}")
                        st.caption(f"AktuÃ¡lis: {current_price:.5f}")
                        st.caption(f"TP: {tp_price:.5f} | SL: {sl_price:.5f}")
                        
                        # P/L metrika
                        pl_color = "normal" if huf_current >= 0 else "inverse"
                        st.metric("Jelenlegi P/L", 
                                f"{int(huf_current):+,} Ft", 
                                delta=f"{pips_current:+.1f} pip")
                        st.markdown("---")
    st.sidebar.markdown("---")
    # --- STATISZTIKÃK VÃ‰GE ---
    
    # --- HETI Ã–SSZEGZÅ TELEGRAM REPORT ---
    # EllenÅ‘rizzÃ¼k, hogy pÃ©ntek este 20:00-e
    meta = daily_signals.get('_meta', {})
    last_report_str = meta.get('last_weekly_report')
    
    # Helyi idÅ‘ (GMT+1)
    local_now = now + timedelta(hours=1)  # UTC -> GMT+1
    is_friday = local_now.weekday() == 4  # 4 = PÃ©ntek
    is_8pm = local_now.hour == 20
    
    send_weekly = False
    
    # KÃ¼ldjÃ¼nk reportot ha:
    # 1. PÃ©ntek este 20:00 Ã³ra van
    # 2. MÃ©g nem kÃ¼ldtÃ¼nk ezen a hÃ©ten
    if is_friday and is_8pm:
        if last_report_str:
            last_report_date = datetime.strptime(last_report_str, '%Y-%m-%d').date()
            # EllenÅ‘rizzÃ¼k, hogy nem ugyanezen a hÃ©ten volt-e mÃ¡r report
            last_week_start, last_week_end = get_week_range(last_report_date)
            if not (current_week_start <= last_report_date <= current_week_end):
                send_weekly = True
        else:
            # ElsÅ‘ futtatÃ¡s - kÃ¼ldjÃ¼nk reportot
            send_weekly = True
    
    if send_weekly:
        # Heti report Ã¼zenet (csak az aktuÃ¡lis hÃ©t statisztikÃ¡ival)
        weekly_msg = (
            f"ğŸ¯ **LONDON BREAKOUT**\n"
            f"ğŸ“ˆ **HETI TELJESÃTMÃ‰NY Ã–SSZEGZÅ**\n"
            f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
            f"ğŸ“… IdÅ‘szak: {current_week_start.strftime('%Y-%m-%d')} - {current_week_end.strftime('%Y-%m-%d')}\n\n"
            f"ğŸ“Š **StatisztikÃ¡k:**\n"
            f"Ã–sszes Trade: {weekly_trades}\n"
            f"âœ… NyerÅ‘: {weekly_wins}\n"
            f"âŒ VesztÅ‘: {weekly_losses}\n"
            f"ğŸ“ˆ NyerÃ©si ArÃ¡ny: {weekly_win_rate:.1f}%\n\n"
            f"ğŸ’° **PÃ©nzÃ¼gyek:**\n"
            f"Ã–sszes Pip: {weekly_pips:+.1f} pip\n"
            f"Ã–sszes Profit/Loss: {int(weekly_huf):+,} Ft\n\n"
        )
        
        if open_trades > 0:
            weekly_msg += f"ğŸ”„ Nyitott pozÃ­ciÃ³k: {open_trades}\n\n"
        
        # KÃ¶vetkezÅ‘ pÃ©ntek kiszÃ¡mÃ­tÃ¡sa
        next_friday = local_now.date() + timedelta(days=7)
        
        weekly_msg += (
            f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
            f"KÃ¶vetkezÅ‘ report: {next_friday.strftime('%Y-%m-%d')} 20:00\n\n"
            f"ğŸ’ª KitartÃ¡s! Minden trade tapasztalat!"
        )
        
        if send_telegram(weekly_msg):
            # FrissÃ­tjÃ¼k az utolsÃ³ report dÃ¡tumÃ¡t
            if '_meta' not in daily_signals:
                daily_signals['_meta'] = {}
            daily_signals['_meta']['last_weekly_report'] = local_now.date().strftime('%Y-%m-%d')
            save_history(daily_signals)
    # --- HETI REPORT VÃ‰GE ---

    # --- NAPI ZÃRÃS EMLÃ‰KEZTETÅ (17:25-KOR) ---
    # EllenÅ‘rizzÃ¼k, hogy 17:25-e (GMT+1)
    meta = daily_signals.get('_meta', {})
    last_close_reminder_str = meta.get('last_close_reminder')
    
    # Helyi idÅ‘ (GMT+1)
    local_now = now + timedelta(hours=1)  # UTC -> GMT+1
    is_1725 = local_now.hour == 17 and local_now.minute == 25
    
    send_close_reminder = False
    
    # KÃ¼ldjÃ¼nk emlÃ©keztetÅ‘t ha:
    # 1. 17:25 Ã³ra van
    # 2. MÃ©g nem kÃ¼ldtÃ¼nk MA emlÃ©keztetÅ‘t
    # 3. Van legalÃ¡bb 1 nyitott pozÃ­ciÃ³
    if is_1725 and open_trades > 0:
        today_str_local = local_now.date().strftime('%Y-%m-%d')
        if last_close_reminder_str != today_str_local:
            send_close_reminder = True
    
    if send_close_reminder:
        # EmlÃ©keztetÅ‘ Ã¼zenet Ã¶sszeÃ¡llÃ­tÃ¡sa
        reminder_msg = (
            f"ğŸ¯ **LONDON BREAKOUT**\n"
            f"â° **NAPI ZÃRÃS EMLÃ‰KEZTETÅ**\n"
            f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
            f"ğŸ“… DÃ¡tum: {local_now.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"ğŸ”” **{open_trades} nyitott pozÃ­ciÃ³ van!**\n"
            f"KÃ©rlek, zÃ¡rd be manuÃ¡lisan a pozÃ­ciÃ³kat!\n\n"
        )
        
        # Minden nyitott pozÃ­ciÃ³ rÃ©szletei
        for symbol, data in daily_signals.items():
            if symbol.startswith('_'):  # Skip metadata
                continue
            if data.get('status') == 'open':
                # Friss Ã¡r lekÃ©rÃ©se
                df_current = get_data(symbol)
                if df_current is not None and not df_current.empty:
                    current_price = float(df_current['Close'].iloc[-1])
                    
                    direction = data.get('direction')
                    entry_price = data.get('entry')
                    tp_price = data.get('tp')
                    sl_price = data.get('sl')
                    pip_value_huf = data.get('pip_value_huf', 0)
                    
                    # SzÃ¡mÃ­tsuk ki a jelenlegi P/L-t
                    pip_multiplier = 100 if "JPY" in symbol else 10000
                    
                    if direction == 'LONG':
                        pips_current = (current_price - entry_price) * pip_multiplier
                    else:  # SHORT
                        pips_current = (entry_price - current_price) * pip_multiplier
                    
                    huf_current = pips_current * pip_value_huf
                    
                    # EredmÃ©ny jelÃ¶lÃ©s
                    result_icon = "ğŸ“ˆ" if pips_current >= 0 else "ğŸ“‰"
                    result_text = "PROFIT" if pips_current >= 0 else "LOSS"
                    direction_label = "LONG/vÃ©tel" if direction == "LONG" else "SHORT/eladÃ¡s"
                    
                    reminder_msg += (
                        f"{result_icon} **{symbol}** - {direction_label}\n"
                        f"BelÃ©pÅ‘: {entry_price:.5f}\n"
                        f"AktuÃ¡lis: {current_price:.5f}\n"
                        f"VÃ¡rhatÃ³ {result_text}: {int(huf_current):+,} Ft ({pips_current:+.1f} pip)\n\n"
                    )
        
        reminder_msg += (
            f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
            f"âš ï¸ Ne feledd: A pozÃ­ciÃ³kat manuÃ¡lisan kell lezÃ¡rni a webappon!\n"
            f"Holnap Ãºj lehetÅ‘sÃ©gek vÃ¡rnak! ğŸ’ª"
        )
        
        if send_telegram(reminder_msg):
            # FrissÃ­tjÃ¼k az utolsÃ³ emlÃ©keztetÅ‘ dÃ¡tumÃ¡t
            if '_meta' not in daily_signals:
                daily_signals['_meta'] = {}
            daily_signals['_meta']['last_close_reminder'] = local_now.date().strftime('%Y-%m-%d')
            save_history(daily_signals)
    # --- NAPI ZÃRÃS EMLÃ‰KEZTETÅ VÃ‰GE ---



    # Adatok frissÃ­tÃ©se Ã¡llapotjelzÅ‘vel
    with st.spinner('Piacok elemzÃ©se...'):
        
        # --- TRADE KÃ–VETÃ‰S Ã‰S UTÃNKÃœLDÃ‰S ---
        # EllenÅ‘rizzÃ¼k az 'open' stÃ¡tuszÃº tradeket
        for symbol in TARGET_PAIRS:
            if symbol in daily_signals and daily_signals[symbol].get('status') == 'open':
                # Friss adat lekÃ©rÃ©se
                df_check = get_data(symbol)
                if df_check is not None and not df_check.empty:
                    current_price = float(df_check['Close'].iloc[-1])
                    trade_info = daily_signals[symbol]
                    
                    tp_price = trade_info.get('tp')
                    sl_price = trade_info.get('sl')
                    direction = trade_info.get('direction')
                    
                    # TP vagy SL ellenÅ‘rzÃ©se
                    hit_tp = False
                    hit_sl = False
                    
                    if direction == 'LONG':
                        if current_price >= tp_price:
                            hit_tp = True
                        elif current_price <= sl_price:
                            hit_sl = True
                    elif direction == 'SHORT':
                        if current_price <= tp_price:
                            hit_tp = True
                        elif current_price >= sl_price:
                            hit_sl = True
                    
                    # Telegram Ã¼zenet kÃ¼ldÃ©se
                    if hit_tp:
                        # Pip Ã©s HUF szÃ¡mÃ­tÃ¡s a valÃ³s exit Ã¡rral
                        entry_price = trade_info.get('entry')
                        pips_target = trade_info.get('pips_target', 0)
                        pip_value_huf = trade_info.get('pip_value_huf', 0)
                        pips_result = pips_target  # TP esetÃ©n a tervezett pip
                        huf_result = pips_result * pip_value_huf
                        direction_label = "LONG/vÃ©tel" if direction == "LONG" else "SHORT/eladÃ¡s"
                        
                        msg = (
                            f"ğŸ¯ **LONDON BREAKOUT**\n"
                            f"âœ… **NYERÅ TRADE: {symbol}**\n"
                            f"ğŸ¯ **CÃ‰LÃR ELÃ‰RVE!**\n\n"
                            f"IrÃ¡ny: {direction_label}\n"
                            f"BelÃ©pÅ‘: {entry_price:.5f}\n"
                            f"CÃ©lÃ¡r: {tp_price:.5f}\n"
                            f"Jelenlegi Ã¡r: {current_price:.5f}\n\n"
                            f"ğŸ’° **EredmÃ©ny:**\n"
                            f"ğŸ“Š Pip: +{pips_result:.1f}\n"
                            f"ğŸ’µ Profit: +{int(huf_result):,} Ft\n\n"
                            f"ğŸ‰ GratulÃ¡lok! A trade profittal lezÃ¡rult!"
                        )
                        if send_telegram(msg):
                            daily_signals[symbol]['status'] = 'tp_hit'
                            daily_signals[symbol]['pips_result'] = pips_result
                            daily_signals[symbol]['huf_result'] = huf_result
                            save_history(daily_signals)
                    
                    elif hit_sl:
                        # Pip Ã©s HUF szÃ¡mÃ­tÃ¡s a valÃ³s exit Ã¡rral
                        entry_price = trade_info.get('entry')
                        pips_target = trade_info.get('pips_target', 0)
                        pip_value_huf = trade_info.get('pip_value_huf', 0)
                        pips_result = -pips_target  # SL esetÃ©n negatÃ­v
                        huf_result = pips_result * pip_value_huf
                        direction_label = "LONG/vÃ©tel" if direction == "LONG" else "SHORT/eladÃ¡s"
                        
                        msg = (
                            f"ğŸ¯ **LONDON BREAKOUT**\n"
                            f"ğŸ”´ **VESZTÅ TRADE: {symbol}**\n"
                            f"ğŸ›¡ï¸ **STOP LOSS ELÃ‰RVE!**\n\n"
                            f"IrÃ¡ny: {direction_label}\n"
                            f"BelÃ©pÅ‘: {entry_price:.5f}\n"
                            f"Stop: {sl_price:.5f}\n"
                            f"Jelenlegi Ã¡r: {current_price:.5f}\n\n"
                            f"ğŸ’° **EredmÃ©ny:**\n"
                            f"ğŸ“Š Pip: {pips_result:.1f}\n"
                            f"ğŸ’µ Loss: {int(huf_result):,} Ft\n\n"
                            f"âš ï¸ A trade vesztesÃ©ggel lezÃ¡rult. KÃ¶vetkezÅ‘ alkalom!"
                        )
                        if send_telegram(msg):
                            daily_signals[symbol]['status'] = 'sl_hit'
                            daily_signals[symbol]['pips_result'] = pips_result
                            daily_signals[symbol]['huf_result'] = huf_result
                            save_history(daily_signals)
        # --- TRADE KÃ–VETÃ‰S VÃ‰GE ---
        
        for symbol in TARGET_PAIRS:
            st.markdown("---")
            st.header(f"ğŸ‡¬ğŸ‡§ {symbol}")
            
            # 1. Adatok
            df = get_data(symbol)
            if df is None:
                st.warning("Nem sikerÃ¼lt letÃ¶lteni az adatokat.")
                continue
                
            # HÃ©tvÃ©ge / FrissessÃ©g ellenÅ‘rzÃ©se
            last_time = df.index[-1]
            is_data_fresh = last_time.date() == datetime.utcnow().date()
            
            if not is_data_fresh:
                st.warning(f"âš ï¸ A piac zÃ¡rva van. Az utolsÃ³ adat: {last_time.strftime('%Y-%m-%d %H:%M')}")
            
            # 2. IndikÃ¡torok
            df['EMA_50'] = calculate_ema(df)
            
            # 3. StratÃ©gia ElemzÃ©s
            analysis = analyze_london_breakout(df, symbol)
            
            # 4. JelzÃ©s KezelÃ©se (One Bullet Logic)
            today_str = datetime.utcnow().strftime('%Y-%m-%d')
            saved_signal = daily_signals.get(symbol)
            
            signal_locked = False
            locked_direction = None
            
            # EllenÅ‘rizzÃ¼k, volt-e mÃ¡r MAI jelzÃ©s
            if saved_signal and saved_signal['date'] == today_str:
                signal_locked = True
                locked_direction = saved_signal['direction']
                st.info(f"ğŸ”’ **MAI JELZÃ‰S ELKÃœLDVE:** {locked_direction}. A terv a grafikonon lÃ¡thatÃ³ (One Bullet Rule).")
                
            # Ha mÃ©g nem volt jelzÃ©s, de most van TRIGGER Ã©s friss az adat
            # Ã‰S nem vagyunk automatikus frissÃ­tÃ©si mÃ³dban
            elif analysis and analysis["signal_type"] and is_data_fresh and not st.session_state.auto_refresh_mode:
                
                # --- DUPLA ELLENÅRZÃ‰S (Race Condition ellen) ---
                # FrissÃ­tjÃ¼k a memÃ³riÃ¡t a fÃ¡jlbÃ³l, hÃ¡tha egy mÃ¡sik tab mÃ¡r elkÃ¼ldte
                current_history = load_history()
                if symbol in current_history and current_history[symbol]['date'] == today_str:
                    st.warning(f"âš ï¸ {symbol} jelzÃ©st mÃ¡r egy mÃ¡sik folyamat elkÃ¼ldte! (Race Condition elkerÃ¼lve)")
                    continue

                # --- PÃ‰NZÃœGYI SZÃMÃTÃSOK (HUF) ---
                # AlapÃ©rtelmezÃ©sek
                lot_size = 0.01
                leverage = 30
                contract_size = 100000 # Standard lot
                
                # Deviza pÃ¡rok felbontÃ¡sa
                base_currency = symbol[:3] # pl GBP
                quote_currency = symbol[3:6] # pl USD
                
                # Ãrfolyamok lekÃ©rÃ©se
                base_huf_rate = get_huf_rate(base_currency)
                usd_huf_rate = get_huf_rate('USD') # Kell a pip Ã©rtÃ©khez ha USD a quote
                
                margin_huf = 0
                pip_value_huf = 0
                
                if base_huf_rate:
                    # Margin szÃ¡mÃ­tÃ¡s: (Contract Size * Lot * Base_HUF) / Leverage
                    # 0.01 lot esetÃ©n contract size effektÃ­v 1000
                    margin_huf = (1000 * base_huf_rate) / leverage
                
                # Pip Ã‰rtÃ©k szÃ¡mÃ­tÃ¡s
                if quote_currency == 'USD':
                    # XXX/USD: 1 pip = 10 USD / lot -> 0.1 USD / 0.01 lot
                    if usd_huf_rate:
                        pip_value_huf = 0.1 * usd_huf_rate
                elif quote_currency == 'JPY':
                    # XXX/JPY: 1 pip = 1000 JPY / lot -> 10 JPY / 0.01 lot
                    # ÃtvÃ¡ltÃ¡s: 10 JPY -> HUF. (USDHUF / USDJPY) vagy kÃ¶zelÃ­tÃ©s
                    # Mivel nincs USDJPY, hasznÃ¡ljunk egy kÃ¶zelÃ­tÃ©st vagy kÃ©rjÃ¼nk le USDJPY-t?
                    # EgyszerÅ±sÃ­tÃ©s: 1 JPY kb 2.5 HUF. De pontosabb ha USDHUF-bÃ³l szÃ¡moljuk.
                    # Ha nincs USDJPY, akkor a prompt szerinti "convert USD value" nehÃ©z.
                    # HasznÃ¡ljuk a prompt javaslatÃ¡t: "10 * (JPYHUF_Rate / 100)" ami fura.
                    # InkÃ¡bb: 10 JPY * (USDHUF / USDJPY).
                    # Mivel USDJPY nincs, hasznÃ¡ljuk a keresztÃ¡rfolyamot a jelenlegi Ã¡rbÃ³l:
                    # GBPJPY / GBPUSD = USDJPY
                    # De ehhez kellene a GBPUSD Ã¡rfolyam is.
                    # EgyszerÅ±bb: 10 JPY ~ 25 HUF (Hardcoded becslÃ©s ha nincs jobb, de prÃ³bÃ¡ljunk pontosabbat)
                    # Ha van USDHUF, akkor 1 USD = X HUF. 1 USD ~ 150 JPY. 1 JPY = X / 150.
                    if usd_huf_rate:
                        pip_value_huf = 10 * (usd_huf_rate / 153.0) # Kb 153 az USDJPY
                
                # NyeresÃ©g / VesztesÃ©g
                pips_gained = analysis['box_height'] * (100 if "JPY" in symbol else 10000)
                pips_risked = pips_gained # 1:1 R/R
                
                profit_huf = pips_gained * pip_value_huf
                loss_huf = pips_risked * pip_value_huf

                # TELEGRAM ÃœZENET Ã–SSZEÃLLÃTÃSA
                direction_icon = "ğŸŸ¢" if analysis["signal_type"] == "LONG" else "ğŸ”´"
                direction_label = "LONG/vÃ©tel" if analysis["signal_type"] == "LONG" else "SHORT/eladÃ¡s"
                
                msg = (
                    f"ğŸ¯ **LONDON BREAKOUT**\n"
                    f"ğŸ”” **JELZÃ‰S: {symbol}**\n"
                    f"-------------------------\n"
                    f"ğŸ‘‰ **IRÃNY:** {direction_icon} **{direction_label}**\n"
                    f"ğŸ“Š **StratÃ©gia:** Hougaard Daybreak\n\n"
                    
                    f"ğŸ’° **PÃ‰NZÃœGYEK (0.01 Lot):**\n"
                    f"ğŸ¦ **Feltett TÃ©t (Margin):** ~{int(margin_huf)} Ft\n"
                    f"ğŸ¯ **VÃ¡rhatÃ³ NyerÅ‘:** +{int(profit_huf)} Ft\n"
                    f"ğŸ›¡ï¸ **Max BukÃ³:** -{int(loss_huf)} Ft\n\n"
                    
                    f"ğŸ“ **SZINTEK:**\n"
                    f"ğŸ”µ BelÃ©pÅ‘: {analysis['entry']:.5f}\n"
                    f"ğŸŸ¢ TP: {analysis['tp']:.5f}\n"
                    f"ğŸ”´ SL: {analysis['sl']:.5f}\n\n"
                    
                    f"(âš ï¸ One Bullet Rule: Mai egyetlen jelzÃ©s!)"
                )
                
                # KÃ¼ldÃ©s
                if send_telegram(msg):
                    # Siker esetÃ©n mentÃ©s a fÃ¡jlba TRADE ADATOKKAL + PIP/HUF INFO + TIMESTAMP
                    daily_signals[symbol] = {
                        'date': today_str,
                        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                        'direction': analysis['signal_type'],
                        'entry': analysis['entry'],
                        'tp': analysis['tp'],
                        'sl': analysis['sl'],
                        'status': 'open',  # Nyitott pozÃ­ciÃ³, kÃ¶vetjÃ¼k
                        'pips_target': pips_gained,  # Tervezett pip
                        'pip_value_huf': pip_value_huf  # 1 pip Ã©rtÃ©ke HUF-ban
                    }
                    save_history(daily_signals)
                    
                    signal_locked = True
                    locked_direction = analysis['signal_type']
                    st.success("âœ… Telegram Ã¼zenet elkÃ¼ldve!")
                    st.rerun() # ÃšjratÃ¶ltÃ©s, hogy frissÃ¼ljÃ¶n a UI

            # 5. GRAFIKON RAJZOLÃSA (Mindig lÃ¡thatÃ³!)
            
            # Zoom beÃ¡llÃ­tÃ¡sa (utolsÃ³ 60 gyertya)
            zoom_start = df.index[-60]
            zoom_end = df.index[-1] + timedelta(hours=4) # Hely a jÃ¶vÅ‘nek
            
            # Y-tengely skÃ¡lÃ¡zÃ¡s (LÃ¡thatÃ³ rÃ©szre)
            visible_df = df[df.index >= zoom_start]
            y_min = visible_df['Low'].min()
            y_max = visible_df['High'].max()
            # Ha van doboz, azt is vegyÃ¼k figyelembe a skÃ¡lÃ¡nÃ¡l
            if analysis:
                y_min = min(y_min, analysis['box_low'])
                y_max = max(y_max, analysis['box_high'])
            padding = (y_max - y_min) * 0.1
            
            fig = go.Figure()

            # GyertyÃ¡k
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name="Ãrfolyam",
                increasing_line_color='green', decreasing_line_color='red'
            ))

            # EMA 50 (SÃ¡rga vonal)
            fig.add_trace(go.Scatter(
                x=df.index, y=df['EMA_50'],
                line=dict(color='yellow', width=2),
                name="Trend (EMA 50)"
            ))

            # London Doboz RajzolÃ¡sa MINDEN LÃ¡thatÃ³ Napra (07:00-08:00 GMT)
            # UtolsÃ³ 5 kereskedÃ©si napra rajzoljuk be a dobozokat
            visible_days = sorted(list(set(df.index.date)))[-5:]  # UtolsÃ³ 5 egyedi nap
            
            for day in visible_days:
                # SzÅ±rÃ©s az adott napra Ã©s a 07:00-08:00 GMT idÅ‘szakra
                day_mask = (df.index.date == day) & (df.index.hour == 7)
                morning_candles = df[day_mask]
                
                if not morning_candles.empty:
                    # Doboz hatÃ¡rainak kiszÃ¡mÃ­tÃ¡sa
                    box_high = float(morning_candles['High'].max())
                    box_low = float(morning_candles['Low'].min())
                    
                    # IdÅ‘pontok a dobozhoz
                    box_start_time = pd.Timestamp(day).tz_localize('UTC').replace(hour=7, minute=0, second=0, microsecond=0)
                    box_end_time = pd.Timestamp(day).tz_localize('UTC').replace(hour=8, minute=0, second=0, microsecond=0)
                    
                    # Mai napra mÃ¡s szÃ­n
                    is_today = (day == last_time.date())
                    fillcolor = "lightblue" if is_today else "lightgray"
                    linecolor = "blue" if is_today else "gray"
                    opacity = 0.3 if is_today else 0.15
                    
                    # TÃ©glalap alakÃº doboz
                    fig.add_shape(
                        type="rect",
                        x0=box_start_time, 
                        x1=box_end_time,
                        y0=box_low, 
                        y1=box_high,
                        fillcolor=fillcolor,
                        opacity=opacity,
                        line=dict(color=linecolor, width=2 if is_today else 1),
                        xref="x", 
                        yref="y"
                    )
                    
                    # Felirat csak a mai dobozra
                    if is_today:
                        box_center_time = box_start_time + (box_end_time - box_start_time) / 2
                        fig.add_annotation(
                            x=box_center_time,
                            y=box_high,
                            text="London Doboz (07-08 GMT)",
                            showarrow=False,
                            yshift=10,
                            font=dict(color="blue", size=10, weight="bold")
                        )


            # FormÃ¡zÃ¡s (Fix nÃ©zet, Nincs Zoom/Pan, Smart Scaling)
            fig.update_layout(
                height=500,
                xaxis_rangeslider_visible=False,
                yaxis=dict(range=[y_min - padding, y_max + padding], fixedrange=True), # Smart Scaling + Lock
                xaxis=dict(range=[zoom_start, zoom_end], fixedrange=True), # Zoom Lock
                dragmode=False, # Pan letiltÃ¡sa
                template="plotly_white",
                title=f"{symbol} (15m) - {analysis['trend'] if analysis else 'N/A'}",
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            # HÃ©tvÃ©gÃ©k kivÃ©tele (Hogy ne legyen rÃ©s)
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])

            # KonfigurÃ¡ciÃ³ (GÃ¶rgÅ‘ letiltÃ¡sa)
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})

            # KereskedÃ©si Terv SzÃ¶vegesen (Ha van doboz)
            if analysis:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Trend (EMA 50)", analysis['trend'], delta="Bika" if analysis['trend']=="BULLISH" else "-Medve")
                c2.metric("Doboz MagassÃ¡g", f"{(analysis['box_height']*10000):.1f} pip")
                c3.metric("ğŸ’° AktuÃ¡lis Ãr", f"{analysis['current_price']:.5f}")
                
                # StÃ¡tusz kiÃ­rÃ¡sa
                if signal_locked:
                    c4.info(f"ğŸ”’ PozÃ­ciÃ³: {locked_direction}")
                else:
                    c4.warning("â³ VÃ¡rakozÃ¡s kitÃ¶rÃ©sre...")
    
    # Automatikus frissÃ­tÃ©s visszaszÃ¡mlÃ¡lÃ³
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        countdown_placeholder = st.empty()
        countdown_placeholder.info(f"â±ï¸ KÃ¶vetkezÅ‘ frissÃ­tÃ©s {refresh_interval} mÃ¡sodperc mÃºlva...")
    
    # Automatikus frissÃ­tÃ©s idÅ‘zÃ­tÃ©s
    time.sleep(refresh_interval)
    # BeÃ¡llÃ­tjuk az auto_refresh_mode-ot, hogy ne kÃ¼ldjÃ¶n Ãºj jelzÃ©seket
    st.session_state.auto_refresh_mode = True
    st.rerun()

if __name__ == "__main__":
    main()
g *cascade08gkko *cascade08ou *cascade08uzz| *cascade08|ƒ *cascade08ƒˆˆ‰ *cascade08‰‹ *cascade08‹ŒŒ *cascade08‘ *cascade08‘““• *cascade08•™™š *cascade08š››œ *cascade08œŸ *cascade08Ÿ¡¡¢ *cascade08¢£ *cascade08£¤¤¥ *cascade08¥¦ *cascade08¦§*cascade08§¨¨ª *cascade08ª­­¯ *cascade08¯Ç*cascade08ÇÉ *cascade08ÉË *cascade08
Ëå åå*cascade08
åŒ Œ *cascade08““” *cascade08”• *cascade08•– *cascade08–— *cascade08—˜˜™ *cascade08™šš› *cascade08›Ÿ *cascade08Ÿ­­® *cascade08®³ *cascade08³º*cascade08ºÂ *cascade08ÂÃ*cascade08ÃÍ *cascade08ÍĞ *cascade08ĞÓ*cascade08ÓØ *cascade08ØÜ *cascade08Üİ*cascade08İŞ *cascade08Şß *cascade08ßâ*cascade08âå *cascade08åæ*cascade08æè *cascade08èııÿ *cascade08ÿ„„… *cascade08…††‡ *cascade08‡ˆˆ‰ *cascade08‰ *cascade08’ *cascade08’““” *cascade08”——˜ *cascade08˜œœ *cascade08  ¡ *cascade08¡¢¢¤ *cascade08¤¨¨© *cascade08©´´µ *cascade08µºº» *cascade08»¼¼½ *cascade08½¾¾¿ *cascade08¿ÃÃÄ *cascade08ÄÉÉË *cascade08ËÖÖå *cascade08åÿ*cascade08ÿ“ *cascade08“”*cascade08”– *cascade08–˜ *cascade08˜™™š *cascade08šœœ *cascade08¢¢£ *cascade08£²²¸ *cascade08¸ºº» *cascade08»¼¼½ *cascade08½¾ *cascade08¾ÂÂÃ *cascade08ÃÄ *cascade08ÄÆÆÇ *cascade08ÇÍÍÎ *cascade08ÎÏÏĞ *cascade08
ĞÙ ÙÚ *cascade08
Úß ßà *cascade08àá *cascade08áâ *cascade08âææç *cascade08
çû ûı *cascade08
ı• •™ *cascade08™‚ *cascade08‚‘*cascade08‘’ *cascade08’Æ*cascade08Æá
 *cascade08á
… *cascade08…ˆˆ‹ *cascade08‹””© *cascade08©¶¶À *cascade08
À” ”¹ *cascade08¹ËËÿ *cascade08ÿŒŒ *cascade08© *cascade08©Ì*cascade08Ì¬ *cascade08¬´´µ *cascade08µ¾¾ä *cascade08äëëø *cascade08øüü *cascade08Ï *cascade08Ïèèê *cascade08êííî *cascade08î‘ *cascade08‘¸¸¹ *cascade08¹ØØÜ *cascade08Üÿÿ— *cascade08—‘‘Å *cascade08ÅÍÍÎ *cascade08ÎÏÏĞ *cascade08Ğààá *cascade08áôôö *cascade08ö……œ *cascade08œ *cascade08ŸŸ¡ *cascade08¡££¤ *cascade08¤¥¥¦ *cascade08¦©©ª *cascade08ª­­¯ *cascade08¯²²³ *cascade08³¶¶¸ *cascade08¸ÁÁÂ *cascade08ÂÂ*cascade08ÂÄÄÅ*cascade08ÅĞ *cascade08ĞÑ*cascade08Ñü *cascade08üŒ *cascade08Œ‘‘¸ *cascade08¸ÅÅÛ *cascade08
Ûç çğ*cascade08
ğ“ “¡*cascade08
¡¢ ¢¦*cascade08
¦É! É!×! *cascade08×!Ş!Ş!ß! *cascade08ß!à!à!á! *cascade08á!â!â!ã! *cascade08ã!ç!ç!è! *cascade08è!ê!ê!ñ! *cascade08ñ!ò!ò!ó! *cascade08ó!÷!÷!ø! *cascade08ø!ü!ü!ı! *cascade08ı!ÿ!ÿ!€" *cascade08€"""‚" *cascade08‚"‡"‡"ˆ" *cascade08ˆ"""" *cascade08"""’" *cascade08’"“"“"”" *cascade08”"•"•"–" *cascade08–"š"š"›" *cascade08›"œ"œ"" *cascade08"""©" *cascade08©"ª"ª"°" *cascade08°"²"²"´" *cascade08´"¸"¸"»" *cascade08»"¾"¾"¿" *cascade08¿"À"À"Î" *cascade08Î"Ñ"Ñ"Ò" *cascade08Ò"Ô"Ô"Õ" *cascade08Õ"Ö"Ö"×" *cascade08×"Ø"Ø"Ü" *cascade08Ü"İ"İ"Ş" *cascade08Ş"ß"ß"à" *cascade08à"â"â"ã" *cascade08ã"ä"ä"æ" *cascade08æ"è"è"ê" *cascade08ê"ì"ì"î" *cascade08î"ó"ó"“# *cascade08“#–#–#š# *cascade08š#›#›# # *cascade08 #¢#¢#£# *cascade08£#¤#¤#¦# *cascade08¦#§#§#¨# *cascade08¨#ª#ª#«# *cascade08«#¬#¬#­# *cascade08­#°#°#±# *cascade08±#³#³#¸# *cascade08¸#¼#¼#Î# *cascade08Î#Ï#Ï#Ò# *cascade08Ò#Ó#Ó#İ# *cascade08İ#ã#ã#ä# *cascade08ä#æ#æ#ç# *cascade08ç#ë#ë#î# *cascade08î#ğ#ğ#ò# *cascade08ò#ó#ó#ş# *cascade08ş#ÿ#ÿ#‚$ *cascade08‚$ƒ$ƒ$„$ *cascade08„$ˆ$ˆ$Š$ *cascade08Š$Œ$Œ$$ *cascade08$$$‘$ *cascade08‘$’$’$“$ *cascade08“$—$—$™$ *cascade08™$œ$œ$$ *cascade08$ $ $¡$ *cascade08¡$£$£$¦$ *cascade08¦$©$©$ª$ *cascade08ª$¬$¬$®$ *cascade08®$±$±$²$ *cascade08²$³$³$´$ *cascade08´$¶$¶$È$ *cascade08È$Ğ$Ğ$Ñ$ *cascade08Ñ$Ò$Ò$Ó$ *cascade08Ó$Õ$Õ$Ö$ *cascade08Ö$Ù$Ù$Û$ *cascade08Û$Ü$Ü$Ş$ *cascade08Ş$æ$æ$è$ *cascade08è$é$é$ê$ *cascade08ê$í$í$î$ *cascade08î$ï$ï$õ$ *cascade08õ$ı$ı$ş$ *cascade08ş$€%€%% *cascade08%ƒ%ƒ%„% *cascade08„%…%…%‡% *cascade08‡%ˆ%ˆ%‰% *cascade08‰%%%‘% *cascade08‘%˜%˜%™% *cascade08™%%%Ÿ% *cascade08Ÿ%¤%¤%½% *cascade08½%Â%Â%Ã% *cascade08Ã%Ä%Ä%Å% *cascade08Å%È%È%É% *cascade08É%Ë%Ë%Ì% *cascade08Ì%Ï%Ï%Ğ% *cascade08Ğ%Ñ%Ñ%Ò% *cascade08Ò%Ô%Ô%Õ% *cascade08Õ%Ö%Ö%Ø% *cascade08Ø%Û%Û%Ü% *cascade08Ü%İ%İ%Ş% *cascade08Ş%à%à%é% *cascade08é%ê%*cascade08ê%ë%*cascade08ë%ì% *cascade08ì%î%*cascade08î%ï% *cascade08ï%ğ%*cascade08ğ%ø%ø%ù% *cascade08ù%ÿ%ÿ%€&*cascade08€&Š&Š&‹& *cascade08‹&Œ&*cascade08Œ&& *cascade08&’& *cascade08’&”& *cascade08”&•& *cascade08•&›&*cascade08›&œ& *cascade08œ&& *cascade08&Ÿ&*cascade08Ÿ& & *cascade08 &¡&*cascade08¡&£&*cascade08£&¤& *cascade08¤&¥&¥&¦& *cascade08¦&§& *cascade08§&©&*cascade08©&¬&¬&­& *cascade08­&®&®&¯& *cascade08¯&°& *cascade08°&±& *cascade08±&²& *cascade08²&´&´&µ& *cascade08µ&¶&¶&º& *cascade08º&»&»&½& *cascade08½&Â&Â&È& *cascade08È&Ó&Ó&×& *cascade08×&Ù&Ù&Û& *cascade08Û&æ&æ&ç& *cascade08ç&ê&ê&ë& *cascade08ë&ğ&ğ&ø& *cascade08ø&ú&ú&û& *cascade08û&ü&ü&ı& *cascade08ı&€'€'' *cascade08'ƒ'ƒ'„' *cascade08„'ˆ'ˆ'‰' *cascade08‰'''' *cascade08'''‘' *cascade08‘'’'’'“' *cascade08“'”'”'š' *cascade08š'œ'œ'¢' *cascade08¢'¯'¯'°' *cascade08°'±'±'³' *cascade08³'½'½'¾' *cascade08¾'¿'¿'Â' *cascade08Â'Ä'Ä'Æ' *cascade08Æ'Ê'Ê'Î' *cascade08Î'Õ'Õ'×' *cascade08×'İ' *cascade08İ'æ'æ'ç' *cascade08ç'ï'ï'ğ' *cascade08ğ'ñ'ñ'ò' *cascade08ò'û'û'ü' *cascade08ü'ı'ı'ˆ( *cascade08ˆ(‹(‹(Œ( *cascade08Œ(((( *cascade08(’(’(—( *cascade08—(˜(˜(¬( *cascade08¬(­(­(¯( *cascade08¯(±(±(¹( *cascade08¹(¼(¼(½( *cascade08½(À(À(Á( *cascade08Á(Ã(Ã(Å( *cascade08Å(É(É(Ê( *cascade08Ê(Ì(Ì(Î( *cascade08Î(Ö(Ö(×( *cascade08×(Ù(Ù(å( *cascade08å(æ(*cascade08æ(ç( *cascade08ç(ï(ï(ğ( *cascade08ğ(ö(ö(÷( *cascade08÷(ø( *cascade08ø(ù(ù(û( *cascade08û(ü( *cascade08ü(ü(*cascade08ü())‘) *cascade08‘)’) *cascade08’)œ)œ)¢) *cascade08¢)ª)ª)«)*cascade08«)°)°)±) *cascade08±)²)²)³) *cascade08³)¶)¶)¸) *cascade08¸)¿)¿)À) *cascade08À)Å)Å)Æ) *cascade08Æ)Õ)Õ)Ö) *cascade08Ö)×)×)Ø) *cascade08Ø)Û)Û)Ü) *cascade08Ü)Ş)Ş)ß) *cascade08ß)ä)ä)æ) *cascade08æ)ê) *cascade08ê)ì)ì)í) *cascade08í)ñ)ñ)ö) *cascade08ö)ù) *cascade08ù)ú)*cascade08ú)û) *cascade08û)ü)ü)ş) *cascade08ş)‡**cascade08‡*ˆ* *cascade08ˆ*Š**cascade08Š** *cascade08*œ*œ** *cascade08*¢*¢*£* *cascade08£*¤* *cascade08¤*¥**cascade08¥*¦* *cascade08¦*§**cascade08§*¨* *cascade08¨*©*©*¯* *cascade08¯*´**cascade08´*µ* *cascade08µ*¶* *cascade08¶*·**cascade08·*¸* *cascade08¸*¹**cascade08¹*º* *cascade08º*»*»*Á* *cascade08Á*Ã*Ã*Ä* *cascade08Ä*È*È*É* *cascade08É*Ì*Ì*Í* *cascade08Í*Ğ*Ğ*Ó* *cascade08Ó*Ô* *cascade08Ô*Õ*Õ*Ö* *cascade08Ö*Ø*Ø*Ù* *cascade08Ù*İ*İ*Ş* *cascade08Ş*â**cascade08â*å**cascade08å*ë* *cascade08ë*î* *cascade08î*ğ*ğ*ñ* *cascade08ñ*÷*÷*ø* *cascade08ø*ù*ù*ú* *cascade08ú*ı*ı*•+ *cascade08•+¥+¥+¦+ *cascade08¦+ª+ª+«+ *cascade08«+¯+¯+°+ *cascade08°+±+±+²+ *cascade08²+Ø+Ø+Ù+ *cascade08Ù+İ+İ+Ş+ *cascade08Ş+ã+ã+ä+ *cascade08ä+ğ+ğ+ó+ *cascade08ó+ô+ô+õ+ *cascade08õ+ø+ø+û+ *cascade08û+ü+ü+‚, *cascade08
‚,„, „,,*cascade08
,¡, ¡,­,*cascade08
­,³, ³,´, *cascade08´,¶,¶,·, *cascade08·,¸, *cascade08¸,»,*cascade08»,¾, *cascade08¾,Æ,Æ,Ç, *cascade08Ç,Í,Í,Î, *cascade08Î,Ï,Ï,Ğ, *cascade08Ğ,Ó,Ó,à, *cascade08à,á,á,â, *cascade08â,è, *cascade08è,é, *cascade08é,ë,ë,ï, *cascade08ï,ğ, *cascade08ğ,ñ,*cascade08ñ,ò, *cascade08ò,ú,ú,û, *cascade08û,ÿ,ÿ,€- *cascade08€---‚- *cascade08‚-‡-‡-“- *cascade08“-”-”-•- *cascade08•-›- *cascade08›-œ-*cascade08œ-- *cascade08-¡- *cascade08¡-£-*cascade08£-¤- *cascade08¤-¨- *cascade08¨-©- *cascade08©-«-«-°- *cascade08°-±- *cascade08±-²-*cascade08²-³- *cascade08³-´-*cascade08´-¶-¶-·- *cascade08·-¸-*cascade08¸-¹- *cascade08¹-º-*cascade08º-È- *cascade08È-Ë-Ë-Ì- *cascade08Ì-Ñ-Ñ-Ò- *cascade08Ò-Õ-Õ-Ö- *cascade08Ö-Ø-Ø-Ù- *cascade08Ù-İ-İ-ã- *cascade08
ã-å- å-î-*cascade08
î-œ. œ.Ÿ.*cascade08
Ÿ.¬. ¬.®. *cascade08®.².².µ. *cascade08µ.Á.Á.Â. *cascade08Â.Ä.Ä.Å. *cascade08Å.É.É.Ï. *cascade08Ï.Ø/Ø/Ù/ *cascade08Ù/Û/Û/Ü/ *cascade08Ü/Ş/Ş/á/ *cascade08á/ê/ê/ë/ *cascade08ë/í/í/î/ *cascade08
î/Ü0 Ü0æ0 *cascade08æ0î0î0ï0 *cascade08ï0ƒ1ƒ1„1 *cascade08„1…1…1†1 *cascade08†1ˆ1ˆ1‹1 *cascade08‹1”1”1˜1 *cascade08˜1¢1¢1£1 *cascade08£1«1«1¬1 *cascade08¬1®1®1´1 *cascade08´1½1½1¿1 *cascade08¿1Å1 *cascade08Å1É1 *cascade08É1Ë1 *cascade08Ë1Ğ1Ğ1Ñ1 *cascade08Ñ1İ1İ1Ş1 *cascade08Ş1ß1ß1å1 *cascade08å1æ1æ1ç1 *cascade08ç1ê1ê1î1 *cascade08î1ú1ú1û1 *cascade08û1ı1ı1‚2 *cascade08‚2„2„2†2 *cascade08†2ˆ2ˆ2‰2 *cascade08‰2Š2Š2‹2 *cascade08‹2222 *cascade082“2“2—2 *cascade08—2š2š2›2 *cascade08›2œ2œ22 *cascade082¢2¢2£2 *cascade08£2¤2 *cascade08¤2¦2¦2ª2 *cascade08ª2­2­2®2 *cascade08®2±2±2²2 *cascade08²2¶2¶2·2 *cascade08·2»2»2¼2 *cascade08¼2Æ2Æ2Ç2 *cascade08Ç2É2É2Ê2 *cascade08Ê2Î2Î2Ô2 *cascade08Ô2ç2ç2é2 *cascade08é2ì2ì2ğ2 *cascade08ğ2ò2ò2ô2*cascade08ô2õ2 *cascade08õ2ù2*cascade08ù2ú2 *cascade08ú2333 *cascade0833 *cascade083’3’3”3 *cascade08”3333*cascade083¤3¤3¥3 *cascade08¥3³3³3´3 *cascade08´3µ3 *cascade08µ3¹3¹3º3 *cascade08º3½3½3¿3 *cascade08¿3À3À3Ä3 *cascade08Ä3Ğ3Ğ3Ñ3 *cascade08Ñ3à3à3á3 *cascade08á3ä3ä3å3 *cascade08å3î3î3ï3 *cascade08ï3ğ3 *cascade08ğ3ñ3ñ3ò3 *cascade08ò3ø3ø3ù3 *cascade08ù3ˆ4ˆ4Š4 *cascade08Š4Œ4 *cascade08Œ44 *cascade084—4 *cascade08—4444 *cascade084¤4¤4¥4 *cascade08¥4®4®4¯4 *cascade08¯4Ã4Ã4È4 *cascade08È4Ë4Ë4Ó4 *cascade08Ó4Ô4Ô4Ş4 *cascade08Ş4±5±5µ5 *cascade08µ5½5 *cascade08½5À5À5Á5*cascade08Á5Â5 *cascade08Â5Ã5 *cascade08Ã5Ä5*cascade08Ä5Å5 *cascade08Å5Î5Î5Ï5 *cascade08Ï5â5â5ã5 *cascade08ã5‹6‹6Œ6 *cascade08Œ6–6–6—6 *cascade08—666Ÿ6 *cascade08Ÿ6 6 *cascade08 6¢6¢6£6 *cascade08£6§6§6¨6 *cascade08¨6µ6µ6¶6 *cascade08¶6·6·6¸6 *cascade08¸6º6º6»6 *cascade08»6¾6¾6¿6 *cascade08¿6Û6Û6Ü6 *cascade08Ü6°7°7º7 *cascade08º7»7»7Á7 *cascade08Á7×7×7Ù7*cascade08Ù7İ7 *cascade08İ7á7á7â7 *cascade08â7ã7ã7ä7 *cascade08ä7æ7æ7ç7 *cascade08ç7è7è7é7 *cascade08é7ë7ë7ì7 *cascade08ì7ô7ô7õ7 *cascade08õ7ö7ö7÷7 *cascade08÷7ø7ø7ù7 *cascade08ù7ú7ú7û7 *cascade08û7ş7ş7ÿ7 *cascade08ÿ7„8„8†8 *cascade08†8‡8‡8ˆ8 *cascade08ˆ8‹8*cascade08‹8¡8¡8¢8 *cascade08¢8£8*cascade08£8¤8 *cascade08¤8¨8*cascade08¨8©8 *cascade08©8ª8 *cascade08ª8«8*cascade08«8¬8*cascade08¬8Ğ8Ğ8Ñ8 *cascade08Ñ8Ó8 *cascade08Ó8Ú8Ú8à8 *cascade08à8ê8ê8ë8 *cascade08ë8ì8ì8í8 *cascade08í8ÿ8ÿ8‚9 *cascade08‚9ƒ9 *cascade08ƒ9…9 *cascade08…9Ÿ9Ÿ9¢9 *cascade08¢9ª9ª9°9 *cascade08°9½9½9¾9 *cascade08¾9Ç9Ç9È9 *cascade08È9É9É9Ê9 *cascade08Ê9Ì9Ì9Ï9*cascade08Ï9Ğ9 *cascade08Ğ9Ó9 *cascade08Ó9Ô9Ô9Õ9 *cascade08Õ9ß9ß9à9 *cascade08à9á9á9â9 *cascade08â9å9å9æ9 *cascade08æ9ï9ï9õ9 *cascade08õ9†:†:Œ: *cascade08
Œ:š: š:›: *cascade08›:Ÿ: *cascade08Ÿ:®:®:³: *cascade08³:´: *cascade08´:Ì;*cascade08
Ì;‹< ‹<Œ<*cascade08
Œ<Î< Î<Ú< *cascade08Ú<¢= *cascade08¢=£=*cascade08£=¤= *cascade08¤=¦=*cascade08¦=§= *cascade08§=­=*cascade08­=°= *cascade08°=±=*cascade08±=²= *cascade08²=³=*cascade08³=À= *cascade08À=Á=*cascade08Á=Â= *cascade08Â=Ä=*cascade08Ä=Å= *cascade08Å=Æ=*cascade08Æ=É= *cascade08É=Ê=*cascade08Ê=Ë= *cascade08Ë=Ğ=*cascade08Ğ=Ñ= *cascade08Ñ=Ò=*cascade08Ò=Ó= *cascade08Ó=Ö=*cascade08Ö=×= *cascade08×=Ú=*cascade08Ú=İ= *cascade08İ=à=*cascade08
à=é= é=ê=*cascade08
ê=ë= ë=í=*cascade08
í=î= î=ó=*cascade08
ó=€> €>>
>…> …>‡>*cascade08
‡>ˆ> ˆ>‰>*cascade08
‰>Œ> Œ>‘>*cascade08
‘>’> ’>“>
“>—> —>˜>*cascade08
˜>«> «>¬>
¬>Ù> Ù>Ú>*cascade08
Ú>Û> Û>Ü>*cascade08
Ü>í> í>è? *cascade08
è?‹@ ‹@@*cascade08
@@ @“@*cascade08
“@—@ —@˜@*cascade08
˜@¢@ ¢@£@ *cascade08
£@©@ ©@ª@*cascade08
ª@«@ «@¬@*cascade08
¬@­@ ­@¯@*cascade08
¯@°@ °@²@*cascade08
²@µ@ µ@¶@*cascade08
¶@·@ ·@¹@*cascade08
¹@ò@ ò@–A*cascade08
–A¾C ¾CğG*cascade08
ğGŠH ŠH•H*cascade08
•H•I •I¹J*cascade08
¹JÓK ÓK’O*cascade08
’OÔP ÔPëR*cascade08
ëRÑT ÑTêV*cascade08
êVõW õWÌX*cascade08
ÌXéj éjk*cascade08
k»k »kÀk*cascade08
ÀkËk ËkÏk*cascade08
ÏkĞk ĞkÓk*cascade08
Ókúk úk‹x *cascade08‹xğx*cascade08ğx¹y *cascade08¹y¿y*cascade08¿y~ *cascade08
~¦ ¦©*cascade08
©« «­*cascade08
­¯ ¯°*cascade08
°± ±²*cascade08
²³ ³º*cascade08º¡€ ¡€Ó€*cascade08Ó€Ô€ Ô€Ş€*cascade08Ş€ß€ ß€*cascade08‡ ‡•*cascade08•— —«*cascade08«­ ­´*cascade08´µ µ¹*cascade08¹º º¿*cascade08¿À ÀÃ*cascade08ÃÇ ÇÑ*cascade08Ñö öƒ*cascade08ƒ¤ƒ ¤ƒ¨ƒ*cascade08¨ƒ‚„ ‚„„*cascade08„‘„ ‘„„*cascade08„„ „¨„*cascade08¨„©„ ©„ª„*cascade08ª„«„ «„¬„*cascade08¬„­„ ­„·„*cascade08·„¸„ ¸„Ã„*cascade08Ã„Ä„ Ä„Õ„*cascade08Õ„Ö„ Ö„ä„*cascade08ä„å„ å„ò„*cascade08ò„ó„ ó„„…*cascade08„…Ÿ… Ÿ…£…*cascade08£…¦… ¦…º…*cascade08º…»… »…Ã…*cascade08Ã…Ä… Ä…Ì…*cascade08Ì…Í… Í…Ğ…*cascade08Ğ…Ò… Ò…Ó…*cascade08Ó…Õ… Õ…æ…*cascade08æ…é… é…í…*cascade08í…‘† ‘†•†*cascade08•†œ† œ††*cascade08†¦† ¦†¨†*cascade08¨†Ï† Ï†Ñ†*cascade08Ñ†”‡ ”‡İ‡*cascade08İ‡û‡ 
û‡¦ˆ¦ˆ¡‰ ¡‰–Š*cascade08–ŠãŠ ãŠçŠ*cascade08çŠèŠ èŠéŠ*cascade08éŠ’‹ ’‹™‹*cascade08™‹¾‹ ¾‹Å‹*cascade08Å‹÷‹ ÷‹ş‹*cascade08ş‹ÖŒ ÖŒÚŒ*cascade08ÚŒÛŒ ÛŒÜŒ*cascade08ÜŒ˜ ˜œ*cascade08œ *cascade08¶ ¶ª*cascade08ª¸ ¸¹*cascade08¹º º»*cascade08»¼ ¼À*cascade08ÀÙ Ùß*cascade08ßª“ ª“±“*cascade08±“²“ ²“´“*cascade08´“¶“ ¶“º“*cascade08º“™” ™”›” *cascade08›”é© é©Êª*cascade08Êª´« ´«º«*cascade08º«ş² ş²ÿ² *cascade08ÿ²«³ «³¬³ *cascade08¬³¢Â ¢Â‡Ã*cascade08‡ÃàÃ 
àÃ›Ä›Ä¬Å ¬Å²Å*cascade08²ÅÎÏ ÎÏ³Ğ*cascade08³ĞìĞ ìĞ§Ñ*cascade08§ÑßÒ ßÒåÒ*cascade08åÒÏÙ ÏÙÑÙ *cascade08ÑÙÕÙ *cascade08
ÕÙÛÙÛÙßÙ *cascade08
ßÙãÙãÙäÙ *cascade08
äÙæÙæÙçÙ *cascade08çÙ“Ú “Ú”Ú *cascade08”ÚèÚ èÚéÚ *cascade08éÚòÚ òÚüÚ *cascade08üÚšÛ šÛÛ *cascade08
ÛŸÛŸÛ Û *cascade08 Û¥Û ¥Û¦Û *cascade08¦Û­Û ­Û®Û *cascade08®Û½Û ½Û¾Û *cascade08¾Û¿Û *cascade08¿Ûøİ øİúİ *cascade08úİüİ *cascade08üİ†Ş *cascade08
†Ş‘Ş‘Ş’Ş *cascade08
’Ş•Ş•Ş–Ş *cascade08
–ŞŞŞŞ *cascade08
Ş£Ş£Ş¤Ş *cascade08
¤Ş¨Ş¨Ş©Ş *cascade08
©Ş®Ş®Ş¯Ş *cascade08
¯ŞµŞµŞ¶Ş *cascade08¶Ş·Ş *cascade08
·Ş¸Ş¸Ş¹Ş *cascade08
¹Ş»Ş»Ş¼Ş *cascade08
¼ŞÁŞÁŞÂŞ *cascade08
ÂŞÃŞÃŞÄŞ *cascade08
ÄŞÇŞÇŞÈŞ *cascade08
ÈŞËŞËŞÌŞ *cascade08
ÌŞÎŞÎŞĞŞ *cascade08
ĞŞâŞâŞãŞ *cascade08
ãŞêŞêŞ÷Ş *cascade08
÷ŞúŞúŞÿŞ *cascade08
ÿŞßßß *cascade08
ß•ß•ß–ß *cascade08
–ß¸ß¸ß¹ß *cascade08
¹ß»ß»ß¼ß*cascade08
¼ß½ß½ß¾ß *cascade08
¾ßÂßÂßÃß *cascade08
ÃßÑßÑßÓß *cascade08ÓßÕß *cascade08
ÕßÙßÙßßß *cascade08ßßáß *cascade08
áßûßûßƒà *cascade08
ƒàˆàˆà‰à *cascade08
‰à‹à‹àŒà *cascade08
Œàààà *cascade08
ààà’à *cascade08
’àšàšàà *cascade08
à à à¡à *cascade08
¡à£à£à¤à *cascade08
¤à¨à¨à©à *cascade08
©à¯à¯à°à *cascade08
°àµàµà·à *cascade08·àÃà *cascade08
ÃàÅàÅàÉà *cascade08
ÉàÜàÜàİà *cascade08
İàâàâàãà *cascade08
ãàááá *cascade08
ááá‘á *cascade08
‘á™á™ášá *cascade08
šáŸáŸá á *cascade08
 á­á­á®á *cascade08
®áÔáÔá×á *cascade08×áØá*cascade08ØáÙá *cascade08
ÙáÛáÛáÜá *cascade08Üáİá *cascade08
İáâáâáãá *cascade08
ãáíáíáîá *cascade08
îáğáğáşá *cascade08
şá€â€â„â *cascade08
„ââââ *cascade08
â’â’â“â *cascade08
“â•â•â–â *cascade08
–â—â—â˜â *cascade08
˜â™â™âšâ *cascade08šâœâ *cascade08
œâ â â¡â*cascade08
¡âµâµâ¶â *cascade08
¶â·â·â¸â *cascade08
¸â¹â¹âºâ *cascade08
ºâ¿â¿âÀâ *cascade08
ÀâÁâÁâÂâ *cascade08
ÂâÃâÃâÄâ *cascade08
ÄâÅâÅâÆâ *cascade08ÆâÈâ *cascade08ÈâĞâ *cascade08
ĞâÔâÔâÖâ *cascade08
Öâ×â×âßâ *cascade08
ßâåâåâæâ *cascade08
æâìâìâíâ *cascade08
íâóâóâôâ *cascade08
ôâ÷â÷âøâ *cascade08
øâùâùâúâ *cascade08úâûâ *cascade08
ûâÿâÿâ€ã *cascade08
€ãããƒã *cascade08
ƒã‹ã‹ãã *cascade08ã‘ã*cascade08‘ã”ã *cascade08”ã—ã *cascade08—ã™ã*cascade08™ãœã *cascade08
œãŸãŸã ã *cascade08
 ã¥ã¥ã¦ã *cascade08
¦ã²ã²ã³ã *cascade08³ã´ã *cascade08
´ã¾ã¾ã¿ã *cascade08
¿ãÁãÁãÂã *cascade08
ÂãÄãÄãÅã *cascade08
ÅãÆãÆãÇã *cascade08
ÇãÊãÊãËã *cascade08
ËãÌãÌãÎã *cascade08ÎãÏã *cascade08ÏãÑã *cascade08ÑãÓã*cascade08Óã×ã*cascade08×ãßã *cascade08ßãáã*cascade08
áãåãåãæã *cascade08
æãéãéãëã *cascade08
ëãîãîãïã *cascade08ïãñã *cascade08ñãòã*cascade08
òãõãõã÷ã *cascade08÷ãûã*cascade08ûã†ä *cascade08†ä‡ä*cascade08
‡ä‹ä‹äŒä *cascade08
Œääää *cascade08
äää‘ä *cascade08
‘ä’ä’ä“ä *cascade08
“ä—ä—ä˜ä *cascade08˜äšä *cascade08šä›ä *cascade08
›äªäªä«ä *cascade08«ä°ä °ä±ä *cascade08
±ä³ä³äµä *cascade08µä¸ä ¸ä¹ä*cascade08¹äÁä ÁäÂä *cascade08Âäğä ğäñä *cascade08
ñäöäöä÷ä *cascade08÷äıä ıäşä *cascade08
şä†å†å‡å *cascade08
‡å‰å‰åŠå *cascade08
Šå‹å‹åŒå *cascade08
Œåååå *cascade08åå *cascade08
å‘å‘å’å *cascade08
’å›å›åœå*cascade08œå·å ·å»å*cascade08»åØå ØåÙå *cascade08
ÙåİåİåŞå*cascade08Şåæå æåçå *cascade08çåûå ûåüå *cascade08üå‹æ ‹æŒæ*cascade08Œæ•æ •æ–æ *cascade08–æœæ *cascade08œææ *cascade08ææ *cascade08æŸæ *cascade08Ÿæ æ *cascade08 æ¡æ ¡æ¤æ *cascade08
¤æèæèæéæ *cascade08
éæïæïæğæ *cascade08
ğæõæõæöæ *cascade08
öæŠçŠç‹ç *cascade08
‹çççç *cascade08
ç—ç—ç˜ç *cascade08
˜ç™ç™çšç *cascade08
šç›ç›çç *cascade08çİç İçïç*cascade08ïçğç ğçñç *cascade08ñçôç*cascade08ôçõç *cascade08
õçÈëÈëÍë*cascade08ÍëÏë ÏëÒë*cascade08Òë×ë ×ëØë*cascade08ØëŞë Şëşë*cascade08şëÿë ÿëì*cascade08ìšì šì¢ì *cascade08¢ì§ì*cascade08§ì¨ì *cascade08¨ìÇì*cascade08ÇìÈì *cascade08ÈìÊì*cascade08ÊìËì *cascade08Ëìâì*cascade08âìãì *cascade08ãìåì*cascade08åìæì *cascade08æììì*cascade08ììíì *cascade08íì¿í*cascade08¿íÁí *cascade08ÁíÜí*cascade08ÜíŞí *cascade08Şíìí*cascade08ìííí *cascade08íí˜î*cascade08˜î™î *cascade08™î›î*cascade08›îî *cascade08îşî*cascade08şîÿî *cascade08ÿî‡ï*cascade08‡ïˆï *cascade08ˆïï*cascade08ïï *cascade08ï™ï*cascade08™ïšï *cascade08šï§ï*cascade08§ï¨ï ¨ïÆï*cascade08ÆïÇï Çïäï*cascade08äïåï åï„ñ*cascade08„ñ…ñ …ñ¬ñ*cascade08¬ñ­ñ *cascade08­ñ¯ñ*cascade08¯ñ°ñ °ñ¹ñ*cascade08¹ñºñ ºñÇñ*cascade08ÇñÈñ *cascade08Èñåñ*cascade08
åñæñæñò*cascade08òò *cascade08ò•ò*cascade08•ò–ò –òÈò*cascade08ÈòÉò Éòâò*cascade08âòãò ãòÏó*cascade08ÏóĞó Ğóıó*cascade08ıóşó şóÉô*cascade08ÉôÊô Êô¬õ*cascade08¬õ®õ *cascade08®õ¯õ*cascade08¯õ°õ *cascade08°õØõ*cascade08ØõÙõ *cascade08ÙõÑö*cascade08ÑöÓö *cascade08ÓöØö*cascade08ØöÙö *cascade08Ùöôö*cascade08ôöõö *cascade08õöâø*cascade08âøäø *cascade08äøõø*cascade08õøöø *cascade08öøşø*cascade08şøˆù *cascade08
ˆùùù¤ù*cascade08¤ù¥ù *cascade08¥ù¨ù*cascade08
¨ù©ù©ù¯ù*cascade08¯ù°ù *cascade08°ùÅù*cascade08ÅùÆù *cascade08ÆùÁú*cascade08ÁúÂú *cascade08ÂúËú*cascade08
ËúÌúÌú û*cascade08 û£û *cascade08£ûÒû*cascade08ÒûÓû *cascade08Óûæû*cascade08æûçû *cascade08çûü*cascade08üü *cascade08üŸü*cascade08Ÿü ü  ü¬ü*cascade08¬ü­ü ­ü¯ü*cascade08¯ü°ü °üµü*cascade08µü¶ü ¶ü¸ü*cascade08¸ü¹ü ¹üÁü*cascade08ÁüÂü *cascade08ÂüÒü*cascade08ÒüÔü *cascade08Ôü‡ı*cascade08‡ıˆı *cascade08ˆıŞş*cascade08Şşßş *cascade08ßşæş*cascade08æşçş *cascade08çş’ÿ*cascade08’ÿ“ÿ *cascade08“ÿœÿ œÿ´ÿ*cascade08´ÿµÿ µÿ½ÿ*cascade08½ÿ¾ÿ *cascade08¾ÿÂÿ*cascade08ÂÿÄÿ *cascade08ÄÿÈÿ*cascade08ÈÿÉÿ *cascade08ÉÿÎÿ Îÿúÿ*cascade08úÿıÿ ıÿ´€*cascade08´€µ€ µ€¸€ *cascade08¸€š‚*cascade08š‚œ‚ *cascade08œ‚‡ƒ*cascade08
‡ƒŒƒŒƒ”ƒ *cascade08
”ƒ—ƒ—ƒ™ƒ*cascade08
™ƒ¡ƒ¡ƒ°ƒ *cascade08°ƒãƒ*cascade08ãƒåƒ *cascade08
åƒæƒæƒòƒ *cascade08
òƒùƒùƒûƒ *cascade08ûƒÿƒ*cascade08ÿƒ‚„ *cascade08‚„„„*cascade08„„…„ *cascade08…„‰„*cascade08‰„Œ„ *cascade08
Œ„’„’„“„ *cascade08
“„•„•„š„ *cascade08
š„›„›„§„ *cascade08
§„®„®„×„ *cascade08×„Ú„ *cascade08
Ú„â„â„ä„ *cascade08ä„è„*cascade08è„é„ *cascade08é„ì„*cascade08ì„í„ *cascade08í„ï„*cascade08ï„ğ„ *cascade08ğ„ñ„*cascade08ñ„ò„ *cascade08ò„ô„*cascade08ô„ö„ *cascade08ö„‰…*cascade08‰…Š…*cascade08Š…‹… ‹……*cascade08…… *cascade08…‘…*cascade08‘…“… *cascade08“…–…*cascade08–…—… *cascade08—…˜…*cascade08˜…™… *cascade08™…›…*cascade08›… … *cascade08
 …¥…¥…°… *cascade08°…±…*cascade08
±…´…´…¶… *cascade08¶…º…*cascade08º…½… *cascade08½…Ç…*cascade08Ç…Ë… *cascade08Ë…Ò…*cascade08Ò…Ó… *cascade08Ó…Ø…*cascade08Ø…Ú… *cascade08Ú…† *cascade08†“†*cascade08“†©† *cascade08©†ª† *cascade08ª†°†*cascade08°†±† *cascade08±†ã†*cascade08ã†å† *cascade08å†é†*cascade08é†ê† *cascade08ê†ë†*cascade08ë†ì† *cascade08ì†ñ†*cascade08ñ†ò† ò†õ†*cascade08õ†ö† ö†¦‡*cascade08¦‡§‡ *cascade08§‡¬‡*cascade08¬‡­‡ ­‡·‡*cascade08·‡¸‡ *cascade08¸‡¿‡*cascade08¿‡À‡ *cascade08À‡Ë‡*cascade08Ë‡Ì‡ *cascade08Ì‡ğ‡*cascade08ğ‡ñ‡ ñ‡‚ˆ*cascade08‚ˆƒˆ ƒˆ†ˆ*cascade08†ˆ‡ˆ ‡ˆˆ*cascade08ˆ‘ˆ ‘ˆ¢ˆ *cascade08
¢ˆªˆªˆÀˆ*cascade08ÀˆÂˆ *cascade08
ÂˆÆˆÆˆÉˆ *cascade08ÉˆÎˆ*cascade08ÎˆÏˆ ÏˆĞˆ*cascade08ĞˆÓˆ *cascade08Óˆüˆ*cascade08üˆşˆ *cascade08
şˆÿˆÿˆ€‰ *cascade08
€‰‰‰‚‰ *cascade08
‚‰ƒ‰ƒ‰„‰ *cascade08
„‰ˆ‰ˆ‰‰‰ *cascade08
‰‰‰‰¥‰ *cascade08¥‰¯‰ *cascade08¯‰³‰*cascade08³‰´‰ *cascade08´‰¶‰ ¶‰¹‰ *cascade08
¹‰º‰º‰»‰ *cascade08
»‰Ã‰Ã‰Å‰ *cascade08
Å‰Ç‰Ç‰İ‰ *cascade08
İ‰å‰å‰ç‰ *cascade08ç‰ë‰*cascade08ë‰í‰ *cascade08í‰î‰ *cascade08î‰ñ‰ *cascade08
ñ‰ô‰ô‰õ‰ *cascade08
õ‰÷‰÷‰ø‰ *cascade08
ø‰ÿ‰ÿ‰„Š *cascade08
„Š†Š†ŠˆŠ *cascade08ˆŠ‰Š *cascade08‰ŠŸŠ *cascade08ŸŠ¡Š *cascade08
¡Š©Š©Š¸Š *cascade08
¸Š¾Š¾Š¿Š *cascade08¿ŠÂŠ*cascade08ÂŠÃŠ ÃŠÉŠ*cascade08ÉŠÊŠ ÊŠÏŠ*cascade08ÏŠĞŠ ĞŠÑŠ*cascade08ÑŠÒŠ *cascade08ÒŠÓŠ*cascade08ÓŠØŠ ØŠÙŠ *cascade08
ÙŠÚŠÚŠÛŠ *cascade08
ÛŠãŠãŠäŠ *cascade08äŠåŠ åŠéŠ *cascade08
éŠìŠìŠôŠ *cascade08
ôŠùŠùŠüŠ *cascade08
üŠƒ‹ƒ‹‹‹ *cascade08
‹‹Œ‹Œ‹–‹ *cascade08
–‹§‹§‹¨‹ *cascade08
¨‹°‹°‹±‹ *cascade08
±‹¼‹¼‹Ë‹ *cascade08
Ë‹Ë‹Ë‹Ï‹ *cascade08
Ï‹Ğ‹Ğ‹Ú‹ *cascade08Ú‹æ‹ *cascade08æ‹é‹ *cascade08
é‹í‹í‹î‹ *cascade08
î‹õ‹õ‹ö‹ *cascade08ö‹€Œ €ŒŒ*cascade08ŒƒŒ ƒŒ…Œ*cascade08…Œ¦Œ ¦Œ²Œ*cascade08²Œ´Œ *cascade08
´Œ»Œ»Œ¿Œ *cascade08¿ŒÇŒ *cascade08
ÇŒÈŒÈŒÉŒ*cascade08ÉŒÊŒ *cascade08ÊŒËŒ*cascade08ËŒÌŒ *cascade08ÌŒÍŒ*cascade08ÍŒÎŒ *cascade08ÎŒÏŒ*cascade08ÏŒĞŒ *cascade08ĞŒÑŒ*cascade08ÑŒÒŒ *cascade08ÒŒÔŒ *cascade08ÔŒÖŒ*cascade08
ÖŒÜŒÜŒàŒ *cascade08àŒƒ ƒˆ *cascade08ˆ‰ *cascade08‰Œ*cascade08Œ *cascade08 ä*cascade08äæ *cascade08
æééõ *cascade08õ ‚ *cascade08‚ƒ *cascade08
ƒ„„… *cascade08…˜ ˜™ *cascade08™œ‘ œ‘‘ *cascade08‘Ÿ‘ *cascade08Ÿ‘±‘ ±‘ø‘*cascade08ø‘†’ *cascade08†’’ *cascade08
’’’’’“’ *cascade08“’’ ’ ’ *cascade08
 ’¡’¡’¢’ *cascade08¢’¸’ *cascade08
¸’½’½’¾’*cascade08¾’À’ *cascade08
À’Á’Á’Ã’ *cascade08
Ã’Ä’Ä’Å’ *cascade08
Å’È’È’É’ *cascade08
É’Ê’Ê’Ë’ *cascade08Ë’Ì’ *cascade08
Ì’Í’Í’Î’ *cascade08
Î’Ö’Ö’Ø’ *cascade08
Ø’Ù’Ù’Ú’ *cascade08
Ú’İ’İ’Ş’ *cascade08
Ş’ß’ß’à’ *cascade08
à’â’â’ì’ *cascade08ì’í’ *cascade08í’ø’ *cascade08
ø’ü’ü’ş’ *cascade08
ş’ƒ“ƒ“„“ *cascade08
„“‡“‡“ˆ“ *cascade08
ˆ““““ *cascade08
“”“”“–“ *cascade08–“—“ *cascade08—“™“ *cascade08
™“š“š“›“ *cascade08
›“¡“¡“¢“ *cascade08
¢“¥“¥“¯“ *cascade08
¯“²“²“½“ *cascade08
½“¿“¿“À“ *cascade08
À“Â“Â“Ã“ *cascade08
Ã“Í“Í“Î“ *cascade08
Î“Ö“Ö“Ù“ *cascade08
Ù“İ“İ“Ş“ *cascade08
Ş“ç“ç“è“ *cascade08
è“ï“ï“ı“ *cascade08
ı“ş“ş“ÿ“ *cascade08
ÿ“””‚” *cascade08
‚”Š”Š”‹” *cascade08
‹”•”•”–” *cascade08
–”š”š”›” *cascade08
›”””Ÿ” *cascade08
Ÿ”¡”¡”¢” *cascade08
¢”£”£”¥” *cascade08
¥”©”©”³” *cascade08³”´” *cascade08
´”·”·”¹” *cascade08¹”»” *cascade08»”¿” *cascade08¿”î” î”õ” *cascade08õ”ü” *cascade08
ü”ı”ı”ş” *cascade08
ş”„•„•…• *cascade08
…•†•†•‡• *cascade08
‡•ˆ•ˆ•‰• *cascade08
‰•Œ•Œ•• *cascade08
•••• *cascade08
•–•–•˜• *cascade08˜•œ•*cascade08œ• • *cascade08 •¡• *cascade08¡•¢• *cascade08¢•¤• *cascade08
¤•¬•¬•­• *cascade08
­•®•®•¯• *cascade08
¯•°•°•±• *cascade08
±•²•²•³• *cascade08³•´• *cascade08
´•µ•µ•¶• *cascade08
¶•»•»•¼• *cascade08
¼•½•½•¾• *cascade08
¾•Á•Á•Â• *cascade08
Â•Ã•Ã•Ä• *cascade08
Ä•Å•Å•Ç• *cascade08
Ç•Ê•Ê•Ë• *cascade08
Ë•Ì•Ì•Î• *cascade08
Î•Ğ•Ğ•Ñ• *cascade08
Ñ•Ò•Ò•Ó• *cascade08
Ó•Ô•Ô•Ö• *cascade08
Ö•×•×•Ù• *cascade08Ù•Ú• *cascade08
Ú•İ•İ•Ş• *cascade08
Ş•à•à•á• *cascade08
á•â•â•ã• *cascade08ã•å• *cascade08
å•æ•æ•î• *cascade08
î•ñ•ñ•ó• *cascade08ó•û• *cascade08û•¬– ¬–°– *cascade08
°–²–²–¸– *cascade08
¸–¼–¼–½– *cascade08
½–¾–¾–¿– *cascade08¿–Á– *cascade08
Á–Â–Â–Å– *cascade08
Å–Ç–Ç–È– *cascade08È–É–*cascade08
É–Î–Î–Ï– *cascade08
Ï–Ø–Ø–Ù– *cascade08
Ù–Û–Û–Ü– *cascade08
Ü–İ–İ–å– *cascade08å–×— ×—Ø— *cascade08Ø—à— à—á— *cascade08á—ï— ï—ğ— *cascade08ğ—¥˜ ¥˜©˜ *cascade08©˜»˜ »˜¼˜ *cascade08¼˜İ˜ İ˜Ş˜ *cascade08
Ş˜ß˜ß˜à˜ *cascade08à˜é˜ é˜ê˜ *cascade08ê˜ë˜ ë˜ì˜ *cascade08
ì˜ö˜ö˜÷˜ *cascade08÷˜ı˜ ı˜ş˜ *cascade08ş˜€™ *cascade08
€™†™†™‡™ *cascade08
‡™ˆ™ˆ™‰™ *cascade08
‰™Š™Š™‹™ *cascade08
‹™Œ™Œ™–™ *cascade08
–™›™›™œ™ *cascade08
œ™™™¡™ *cascade08
¡™¤™¤™¥™ *cascade08
¥™ª™ª™«™ *cascade08
«™¬™¬™­™ *cascade08
­™°™°™±™ *cascade08
±™³™³™´™ *cascade08
´™µ™µ™¶™ *cascade08
¶™·™·™¸™ *cascade08
¸™»™»™¼™ *cascade08
¼™½™½™Ä™ *cascade08Ä™Å™ *cascade08Å™Æ™ *cascade08Æ™Ç™ *cascade08Ç™Í™ *cascade08
Í™Õ™Õ™î™ *cascade08
î™ö™ö™÷™*cascade08÷™ø™ *cascade08
ø™ú™ú™û™*cascade08
û™ššƒš *cascade08
ƒš‹š‹š¶š *cascade08
¶š¾š¾šÁš *cascade08
ÁšÂšÂšËš *cascade08
ËšÑšÑšÙš *cascade08
ÙšÛšÛšáš *cascade08
ášâšâšòš *cascade08
òšóšóšüš *cascade08
üš››“› *cascade08
“›”›”›¤› *cascade08
¤›¥›¥›±› *cascade08
±›³›³›»› *cascade08
»›Á›Á›Æ› *cascade08
Æ›Ç›Ç›Ğ› *cascade08
Ğ›Ñ›Ñ›Ô› *cascade08
Ô›Ö›Ö›Ş› *cascade08
Ş›ä›ä›¤œ *cascade08
¤œ¬œ¬œ®œ *cascade08
®œ°œ°œ²œ *cascade08²œ¶œ*cascade08
¶œºœºœ¾œ *cascade08¾œ¿œ*cascade08¿œÀœ *cascade08ÀœÂœ*cascade08ÂœÃœ *cascade08ÃœÆœ *cascade08
ÆœÕœÕœ×œ *cascade08
×œßœßœäœ *cascade08äœåœ *cascade08åœçœ*cascade08çœèœ *cascade08èœşœ *cascade08
şœƒƒ‹ *cascade08
‹‘ *cascade08
‘’’” *cascade08”• *cascade08• *cascade08
£ *cascade08
£¤¤İ *cascade08
İŞŞä *cascade08
ä““™ *cascade08
™¡¡§ *cascade08§± ±² *cascade08
²³³´ *cascade08
´ÖÖâ *cascade08
âææç *cascade08çé *cascade08éŒŸ ŒŸŸ *cascade08Ÿ¡Ÿ ¡Ÿ¢Ÿ *cascade08¢Ÿ¯  ¯ °  *cascade08° º  º Ä  *cascade08Ä º¤ º¤»¤ *cascade08»¤¼¤ *cascade08¼¤½¤*cascade08
½¤¾¤¾¤¿¤ *cascade08¿¤Ú¤ Ú¤Û¤ *cascade08Û¤å¤ å¤æ¤ *cascade08
æ¤ç¤ç¤è¤ *cascade08
è¤é¤é¤ê¤ *cascade08ê¤…¥ …¥†¥ *cascade08†¥Ÿ¥ Ÿ¥ ¥ *cascade08
 ¥¡¥¡¥£¥ *cascade08
£¥¥¥¥¥§¥ *cascade08§¥¬¥ ¬¥­¥ *cascade08­¥µ¥ µ¥¶¥ *cascade08¶¥Á¥ Á¥Ä¥ *cascade08
Ä¥È¥È¥Ğ¥ *cascade08Ğ¥Ù¥ Ù¥Ú¥ *cascade08Ú¥å¥ å¥æ¥ *cascade08æ¥ù¥ ù¥ú¥ *cascade08ú¥š¦ š¦›¦ *cascade08›¦³¦ ³¦´¦ *cascade08´¦»¦ »¦¼¦ *cascade08
¼¦¾¦¾¦Ä¦ *cascade08
Ä¦Ô¦Ô¦Ö¦ *cascade08
Ö¦æ¦æ¦è¦ *cascade08è¦ì¦ *cascade08ì¦´¨ ´¨µ¨ *cascade08µ¨ÿ© ÿ©€ª *cascade08€ª‚ª ‚ªƒª *cascade08ƒª†ª †ª‡ª *cascade08
‡ª‰ª‰ªŠª *cascade08Šª¡ª ¡ª¤ª *cascade08¤ª¥ª ¥ª¦ª *cascade08¦ª§ª *cascade08
§ª¨ª¨ªªª *cascade08ªª«ª «ª¬ª *cascade08
¬ª­ª­ª®ª *cascade08®ª¯ª *cascade08
¯ª°ª°ª²ª *cascade08²ª¶ª *cascade08¶ª¸ª *cascade08¸ª¸ª*cascade08¸ªÃª*cascade08ÃªÄª ÄªÉª*cascade08ÉªÕª ÕªÖª*cascade08Öª×ª ×ªÚª*cascade08ÚªÛª Ûªáª *cascade08
áªâªâªäª *cascade08
äªåªåªíª *cascade08íª€« €«« *cascade08«¥« ¥«­« *cascade08­«È« È«Ê« *cascade08Ê«Ü« Ü«Ş« *cascade08
Ş«ê«ê«ö« *cascade08ö«÷« *cascade08÷«ù« ù«ú« *cascade08ú«û« *cascade08û«ü«*cascade08ü«ş« *cascade08
ş«…¬…¬ˆ¬ *cascade08ˆ¬¬ ¬›¬ *cascade08
›¬œ¬œ¬¬ *cascade08¬°¬ *cascade08°¬³¬ ³¬´¬ *cascade08
´¬¹¬¹¬Á¬ *cascade08
Á¬Õ¬Õ¬Ö¬ *cascade08
Ö¬×¬×¬Ù¬ *cascade08
Ù¬İ¬İ¬á¬ *cascade08
á¬é¬é¬ñ¬ *cascade08
ñ¬ô¬ô¬õ¬ *cascade08õ¬­ ­Ÿ­ *cascade08
Ÿ­£­£­¯­ *cascade08¯­¶­ ¶­¾­ *cascade08¾­Â­ *cascade08Â­Æ­ *cascade08
Æ­Ê­Ê­Ì­ *cascade08
Ì­Î­Î­Ö­ *cascade08Ö­ö­ ö­÷­ *cascade08÷­¿® ¿®À® *cascade08
À®Á®Á®Â® *cascade08Â®Æ® Æ®Ç® *cascade08Ç®Ê® *cascade08Ê®Ë® Ë®Ì® *cascade08Ì®Ñ® Ñ®Ô® *cascade08Ô®×® ×®Ø® *cascade08Ø®è® è®é® *cascade08é®ê®*cascade08ê®ë® *cascade08ë®ï® *cascade08
ï®ó®ó®ô® *cascade08
ô®ú®ú®û® *cascade08
û®ü®ü®ı® *cascade08
ı®€¯€¯„¯ *cascade08„¯Î¯ Î¯Ï¯ *cascade08
Ï¯Ğ¯Ğ¯Ñ¯ *cascade08
Ñ¯Ò¯Ò¯Ó¯ *cascade08Ó¯Ù¯ Ù¯Ú¯ *cascade08Ú¯Û¯ Û¯İ¯ *cascade08
İ¯ß¯ß¯ë¯ *cascade08ë¯ú¯ ú¯û¯ *cascade08û¯ü¯ ü¯ı¯ *cascade08
ı¯ş¯ş¯ÿ¯ *cascade08
ÿ¯°°‚° *cascade08‚°ƒ° ƒ°†° *cascade08
†°‡°‡°“° *cascade08“°£° £°¤° *cascade08
¤°¥°¥°§° *cascade08
§°«°«°¬° *cascade08
¬°®°®°¯° *cascade08
¯°´°´°µ° *cascade08
µ°¿°¿°À° *cascade08
À°Â°Â°Ä° *cascade08
Ä°Ë°Ë°Ø° *cascade08
Ø°å°å°æ° *cascade08
æ°î°î°ï° *cascade08ï°˜± ˜±š± *cascade08
š±ª±ª±¶± *cascade08¶±·± ·±¹± *cascade08¹±º± º±»± *cascade08»±Á± Á±Â± *cascade08Â±Å± Å±Æ± *cascade08
Æ±È±È±É± *cascade08
É±Ê±Ê±Ë± *cascade08
Ë±Ì±Ì±Î± *cascade08Î±Ò± Ò±Ó± *cascade08Ó±Õ± Õ±×± *cascade08
×±İ±İ±Ş± *cascade08
Ş±à±à±â± *cascade08â±ã±*cascade08
ã±ÿ±ÿ±€² *cascade08
€²„²„²’² *cascade08’²”² *cascade08
”²¾²¾²¿² *cascade08
¿²À²À²Á² *cascade08
Á²Ê²Ê²Ì² *cascade08Ì²Ğ² *cascade08
Ğ²Ø²Ø²Ù² *cascade08Ù²Ü² *cascade08Ü²İ²*cascade08İ²Ş² *cascade08Ş²å² *cascade08å²æ²*cascade08æ²ç² *cascade08ç²è²*cascade08è²ñ² *cascade08ñ²ô² *cascade08ô²õ² *cascade08õ²ø² ø²ü² *cascade08
ü²ı²ı²ÿ² *cascade08
ÿ²³³ƒ³ *cascade08
ƒ³†³†³‘³ *cascade08‘³™³ *cascade08™³Ÿ³ *cascade08Ÿ³ª³ *cascade08ª³«³*cascade08«³¸³ *cascade08¸³»³ *cascade08
»³Â³Â³Ê³ *cascade08
Ê³Ì³Ì³Í³ *cascade08
Í³Î³Î³Ï³ *cascade08
Ï³Ğ³Ğ³Ö³ *cascade08
Ö³Û³Û³Ü³ *cascade08
Ü³ş³ş³€´ *cascade08
€´…´…´†´ *cascade08
†´Š´Š´‹´ *cascade08
‹´´´’´ *cascade08
’´˜´˜´š´ *cascade08
š´¨´¨´ª´ *cascade08
ª´¬´¬´°´ *cascade08
°´¶´¶´º´ *cascade08
º´¾´¾´¿´ *cascade08
¿´Ã´Ã´Ä´ *cascade08
Ä´Í´Í´Î´ *cascade08
Î´Ğ´Ğ´Ñ´ *cascade08
Ñ´Ó´Ó´Ø´ *cascade08
Ø´Ú´Ú´Û´ *cascade08
Û´Ş´Ş´ß´ *cascade08
ß´é´é´ë´ *cascade08
ë´ì´ì´ò´ *cascade08ò´ó´ *cascade08
ó´€µ€µˆµ *cascade08
ˆµ—µ—µ˜µ *cascade08
˜µ£µ£µ§µ *cascade08
§µ©µ©µªµ*cascade08
ªµ¬µ¬µ­µ *cascade08
­µ²µ²µ¸µ *cascade08¸µ¼µ *cascade08¼µÀµ *cascade08ÀµÃµ *cascade08ÃµÄµ *cascade08
ÄµÕµÕµÖµ *cascade08
Öµ×µ×µÙµ *cascade08
ÙµÜµÜµŞµ *cascade08Şµæµ *cascade08
æµïµïµğµ *cascade08
ğµôµôµõµ *cascade08
õµşµşµÿµ *cascade08
ÿµ’¶’¶—¶ *cascade08
—¶™¶™¶š¶ *cascade08
š¶œ¶œ¶¶ *cascade08
¶±¶±¶²¶ *cascade08
²¶³¶³¶Á¶ *cascade08
Á¶Î¶Î¶Ï¶ *cascade08
Ï¶Ğ¶Ğ¶Ñ¶ *cascade08
Ñ¶Ü¶Ü¶İ¶ *cascade08
İ¶â¶â¶ã¶ *cascade08
ã¶ç¶ç¶ò¶ *cascade08
ò¶÷¶÷¶…· *cascade08…·‡· *cascade08‡·‹· *cascade08‹·Œ· *cascade08Œ·“· *cascade08
“·”·”·•· *cascade08
•·˜·˜·™· *cascade08
™·Ÿ·Ÿ· · *cascade08
 ·«·«·¬· *cascade08
¬·­·­·®· *cascade08®·¯· *cascade08
¯·°·°·±· *cascade08
±·²·²·³· *cascade08
³·µ·µ·¶· *cascade08¶··· *cascade08
··¿·¿·À·*cascade08À·Â· *cascade08Â·Ê· *cascade08
Ê·Ñ·Ñ·Ò· *cascade08
Ò·Õ·Õ·Ö· *cascade08
Ö·ß·ß·à· *cascade08
à·á·á·â· *cascade08
â·å·å·ç· *cascade08
ç·é·é·ê· *cascade08
ê·ë·ë·ì· *cascade08ì·í· *cascade08
í·ñ·ñ·ò· *cascade08
ò·û·û·ü· *cascade08
ü·‚¸‚¸ƒ¸ *cascade08
ƒ¸…¸…¸†¸ *cascade08
†¸ˆ¸ˆ¸‹¸ *cascade08‹¸¸ *cascade08¸‘¸ *cascade08‘¸’¸ *cascade08’¸™¸ *cascade08
™¸š¸š¸›¸ *cascade08
›¸¸¸Ÿ¸*cascade08Ÿ¸¢¸ ¢¸£¸ *cascade08£¸©¸ ©¸ª¸ *cascade08ª¸¾¸ ¾¸Ì¸ *cascade08Ì¸Ï¸ *cascade08
Ï¸Ø¸Ø¸Ú¸ *cascade08
Ú¸Û¸Û¸İ¸ *cascade08
İ¸à¸à¸á¸ *cascade08
á¸æ¸æ¸è¸ *cascade08
è¸ú¸ú¸û¸ *cascade08
û¸ˆ¹ˆ¹‰¹*cascade08
‰¹¹¹‘¹ *cascade08
‘¹”¹”¹•¹ *cascade08
•¹˜¹˜¹™¹ *cascade08
™¹¹¹¹ *cascade08
¹¡¹¡¹¢¹ *cascade08
¢¹£¹£¹¤¹ *cascade08
¤¹¦¹¦¹§¹ *cascade08§¹¨¹ *cascade08
¨¹©¹©¹ª¹ *cascade08
ª¹­¹­¹¯¹ *cascade08¯¹±¹ *cascade08
±¹³¹³¹½¹ *cascade08
½¹É¹É¹Ê¹ *cascade08
Ê¹Í¹Í¹Î¹ *cascade08
Î¹Ñ¹Ñ¹Ò¹ *cascade08
Ò¹ï¹ï¹ù¹ *cascade08ù¹ı¹ *cascade08
ı¹€º€ºº *cascade08º‚º *cascade08
‚ºƒºƒº„º *cascade08„º…º *cascade08…º‡º *cascade08
‡ºˆºˆº‰º *cascade08‰º“º *cascade08“º—º *cascade08
—ºººŸº *cascade08
Ÿº¢º¢º£º *cascade08
£º¥º¥º©º*cascade08©ºªº *cascade08
ªº«º«º¬º *cascade08¬º®º *cascade08®º¯º*cascade08
¯º°º°º±º *cascade08
±º´º´ºµº *cascade08
µº¶º¶º·º *cascade08·º¸º*cascade08¸º¹º*cascade08¹º»º *cascade08
»º½º½º¾º *cascade08¾ºÂº *cascade08ÂºÃº *cascade08ÃºÄº *cascade08ÄºÅº *cascade08ÅºÉº *cascade08ÉºËº *cascade08
ËºÎºÎºÏº *cascade08
ÏºĞºĞºÑº *cascade08
ÑºÒºÒºÓº *cascade08
ÓºØºØºÙº *cascade08
ÙºÛºÛºİº *cascade08İºãº *cascade08ãºäº*cascade08äºåº *cascade08
åºæºæºçº *cascade08
çºéºéºêº *cascade08
êºòºòºóº *cascade08
óºùºùºúº *cascade08
úºıºıºşº *cascade08şºÿº *cascade08
ÿº†»†»‡» *cascade08
‡»‰»‰»Š» *cascade08
Š»»»»*cascade08»‘» *cascade08
‘»˜»˜»™» *cascade08
™»§»§»¨» *cascade08¨»©» *cascade08
©»ª»ª»«» *cascade08
«»¬»¬»­» *cascade08
­»³»³»µ» *cascade08µ»»» *cascade08»»¾» ¾»¿» *cascade08¿»Ç» *cascade08
Ç»É»É»Ê» *cascade08
Ê»Ë»Ë»Ì» *cascade08
Ì»Í»Í»Î» *cascade08Î»å» å»æ» *cascade08
æ»ë»ë»ì» *cascade08
ì»÷»÷»ø» *cascade08
ø»Š¼Š¼‹¼ *cascade08
‹¼¼¼’¼ *cascade08’¼ç¼*cascade08ç¼ë¼ *cascade08
ë¼í¼í¼õ¼ *cascade08õ¼ö¼ *cascade08ö¼÷¼ ÷¼½ *cascade08
½„½„½ˆ½ *cascade08ˆ½‰½ *cascade08
‰½Š½Š½‹½ *cascade08
‹½Œ½Œ½½ *cascade08
½½½½ *cascade08½’½ *cascade08
’½“½“½”½ *cascade08
”½˜½˜½™½ *cascade08
™½›½›½œ½ *cascade08
œ½½½¦½ *cascade08¦½§½ *cascade08§½©½ *cascade08©½ª½ *cascade08
ª½«½«½¯½ *cascade08¯½°½ *cascade08
°½±½±½´½ *cascade08
´½µ½µ½¶½ *cascade08¶½·½ *cascade08
·½º½º½»½ *cascade08
»½¼½¼½½½ *cascade08½½¾½ *cascade08
¾½¿½¿½Ê½ *cascade08Ê½×½ ×½Ø½*cascade08Ø½Û½ Û½İ½ *cascade08
İ½ä½ä½å½ *cascade08
å½ë½ë½ì½ *cascade08
ì½ó½ó½ö½ *cascade08
ö½ú½ú½û½ *cascade08
û½ş½ş½ÿ½ *cascade08
ÿ½€¾€¾¾ *cascade08
¾„¾„¾†¾ *cascade08
†¾‡¾‡¾•¾ *cascade08
•¾—¾—¾˜¾ *cascade08
˜¾™¾™¾š¾ *cascade08
š¾›¾›¾¾ *cascade08
¾¤¾¤¾°¾ *cascade08°¾²¾ ²¾³¾*cascade08³¾¶¾ ¶¾¸¾ *cascade08¸¾¹¾ *cascade08
¹¾»¾»¾¼¾ *cascade08
¼¾À¾À¾Á¾ *cascade08
Á¾Ä¾Ä¾Å¾ *cascade08
Å¾Ë¾Ë¾Ì¾ *cascade08
Ì¾Ï¾Ï¾Ğ¾ *cascade08
Ğ¾Ü¾Ü¾ß¾ *cascade08ß¾ŞÁ *cascade08
ŞÁÜÂÜÂèÂ *cascade08èÂ’Ã *cascade082$file:///c:/Users/Tomi/.gemini/app.py
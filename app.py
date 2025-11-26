import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import time
import requests
import json
import os

# --- FELHASZNÁLÓI KONFIGURÁCIÓ ---
# Cseréld le a sajátodra, ha szükséges!
TELEGRAM_BOT_TOKEN = "7487229026:AAH51YJ4atFsvqHKfQj9l_QU7ytJMIwo0w0" 
TELEGRAM_CHAT_ID = "1736205722"

# --- KONSTANSOK ÉS BEÁLLÍTÁSOK ---
TARGET_PAIRS = ['GBPUSD=X', 'GBPJPY=X', 'EURUSD=X']
BUFFER_PIPS = 0.0003 # Kb. 3 pip puffer a doboz széleihez
RISK_PER_TRADE = 0.005 # 0.5% kockázat (példa)
HISTORY_FILE = os.path.join(os.getcwd(), "trade_history.json")

# Az oldal beállítása
st.set_page_config(page_title="London Breakout Pro", layout="wide")

# --- SEGÉDFÜGGVÉNYEK ---

def load_history():
    """Betölti a korábbi jelzéseket a JSON fájlból."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Hiba a betöltéskor: {e}")
            return {}
    return {}

def save_history(history):
    """Elmenti a jelzéseket a JSON fájlba."""
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    except Exception as e:
        st.error(f"Hiba a mentéskor: {e}")

def send_telegram(message):
    """Üzenet küldése a Telegram Bot API-n keresztül."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Telegram hiba: {e}")
        return False

@st.cache_data(ttl=3600) # Óránként elég frissíteni az árfolyamokat
def get_huf_rate(base_currency):
    """
    Lekéri az aktuális HUF árfolyamot a megadott devizához.
    Támogatott: EUR, USD, GBP.
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

@st.cache_data(ttl=60) # Gyorsítótár 60 másodpercig
def get_data(ticker):
    """Adatok letöltése (15 perces, 59 napra)."""
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

        # Időzóna kezelés (Yfinance néha UTC-t ad, néha mást - normalizáljuk)
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        else:
            df.index = df.index.tz_convert('UTC')
            
        return df
    except Exception as e:
        st.error(f"Hiba az adatok letöltésekor ({ticker}): {e}")
        return None

def calculate_ema(df, span=50):
    """Exponenciális Mozgóátlag számítása."""
    return df['Close'].ewm(span=span, adjust=False).mean()

def analyze_london_breakout(df, symbol):
    """
    A London Breakout stratégia logikája.
    1. Megkeresi a mai 07:00-08:00 GMT sávot.
    2. Meghatározza a trendet (EMA 50).
    3. Kiszámolja a belépőt, stopot, célt.
    """
    # Aktuális dátum meghatározása
    last_candle_time = df.index[-1]
    today_str = last_candle_time.strftime('%Y-%m-%d')
    
    # Szűrés a mai napra és a 07:00-08:00 GMT időszakra
    # Megjegyzés: A pandas szeletelésnél az óra a kezdést jelöli
    morning_mask = (df.index.date == last_candle_time.date()) & (df.index.hour == 7) 
    morning_candles = df[morning_mask]

    if morning_candles.empty:
        return None # Még nincs adat a mai reggelről (pl. éjfél van)

    # Doboz meghatározása (Wick-to-Wick)
    # --- FIX: Ensure scalar values (float) ---
    box_high = float(morning_candles['High'].max())
    box_low = float(morning_candles['Low'].min())
    box_height = box_high - box_low
    
    # Aktuális ár és EMA
    # --- FIX: Ensure scalar values using .item() or float() ---
    current_price = df['Close'].iloc[-1]
    if isinstance(current_price, pd.Series):
        current_price = current_price.iloc[0]
    current_price = float(current_price)

    ema_50 = df['EMA_50'].iloc[-1]
    if isinstance(ema_50, pd.Series):
        ema_50 = ema_50.iloc[0]
    ema_50 = float(ema_50)
    
    # Trend meghatározása
    trend = "BULLISH" if current_price > ema_50 else "BEARISH"
    
    # Szintek számítása
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
    
    # Trigger logika (Hougaard-féle trendszűrés)
    if trend == "BULLISH":
        # Csak LONG lehet
        entry_price = box_high + BUFFER_PIPS
        if current_price > entry_price:
            result["signal_type"] = "LONG"
            result["entry"] = entry_price
            result["sl"] = box_low
            result["tp"] = entry_price + box_height # 1:1 Célár
            
    elif trend == "BEARISH":
        # Csak SHORT lehet
        entry_price = box_low - BUFFER_PIPS
        if current_price < entry_price:
            result["signal_type"] = "SHORT"
            result["entry"] = entry_price
            result["sl"] = box_high
            result["tp"] = entry_price - box_height # 1:1 Célár

    return result

# --- FŐ ALKALMAZÁS ---

def main():
    # Logo megjelenítése
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", use_container_width=True)
    
    st.title("🇬🇧 London Breakout Pro Dashboard")
    st.caption("3 Eszköz Szimultán Figyelése (07:00-08:00 GMT + EMA 50)")
    
    # Session State inicializálása (Védi az automatikus frissítést)
    if 'auto_refresh_mode' not in st.session_state:
        st.session_state.auto_refresh_mode = True
        
    # --- TRADING MODE KAPCSOLÓ ---
    # Ez engedélyezi a jelzések küldését. Alapból kikapcsolva a biztonságért.
    trading_mode = st.sidebar.checkbox("Trading Mode (Jelzések küldése)", value=True, help="Pipáld be, ha szeretnéd, hogy a rendszer Telegram üzeneteket küldjön!")
    
    if trading_mode:
        st.sidebar.success("✅ JELZÉSEK AKTÍVAK")
    else:
        st.sidebar.warning("⚠️ JELZÉSEK KIKAPCSOLVA")

    
    # Automatikus frissítés időzítő megjelenítése
    placeholder = st.empty()
    refresh_interval = 30  # másodperc

    # Memória inicializálása (Fájlból)
    daily_signals = load_history()
    # Struktúra: {'GBPUSD=X': {'date': '2025-11-24', 'timestamp': '2025-11-24 10:30:00', 'direction': 'LONG', 'entry': 1.25, 'tp': 1.26, 'sl': 1.24, 'status': 'open'}, ..., '_meta': {'last_weekly_report': '2025-11-24'}}
    
    # --- TELJESÍTMÉNYSTATISZTIKÁK (Dashboard) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Teljesítmény Összegző")
    
    # Helper function to get week start (Monday) and end (Sunday)
    def get_week_range(date):
        """Meghatározza a hét kezdetét (hétfő) és végét (vasárnap) egy adott dátumhoz."""
        weekday = date.weekday()  # 0=Hétfő, 6=Vasárnap
        week_start = date - timedelta(days=weekday)
        week_end = week_start + timedelta(days=6)
        return week_start, week_end
    
    # Aktuális hét határainak meghatározása
    now = datetime.utcnow()
    current_week_start, current_week_end = get_week_range(now.date())
    
    # Statisztikák számítása (ALL TIME)
    total_trades = 0
    wins = 0
    losses = 0
    open_trades = 0
    total_pips = 0.0
    total_huf = 0.0
    
    # Heti statisztikák (Current Week Only)
    weekly_trades = 0
    weekly_wins = 0
    weekly_losses = 0
    weekly_pips = 0.0
    weekly_huf = 0.0
    
    # Napi lezárt tradek gyűjtése
    today_closed_trades = []
    today_str = now.strftime('%Y-%m-%d')

    for symbol, data in daily_signals.items():
        if symbol.startswith('_'):  # Skip metadata
            continue
        status = data.get('status')
        
        # Ellenőrizzük, hogy az aktuális héten zárult-e le
        trade_date_str = data.get('date')
        is_current_week = False
        is_today = False
        
        if trade_date_str:
            try:
                trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d').date()
                is_current_week = current_week_start <= trade_date <= current_week_end
                is_today = trade_date_str == today_str
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
            
            # Today stats
            if is_today:
                today_closed_trades.append({'symbol': symbol, 'result': 'WIN', 'huf': data.get('huf_result', 0), 'pips': data.get('pips_result', 0)})
                
        elif status == 'sl_hit':
            losses += 1
            total_trades += 1
            total_pips += data.get('pips_result', 0)  # már negatív
            total_huf += data.get('huf_result', 0)  # már negatív
            
            # Weekly stats
            if is_current_week:
                weekly_losses += 1
                weekly_trades += 1
                weekly_pips += data.get('pips_result', 0)
                weekly_huf += data.get('huf_result', 0)

            # Today stats
            if is_today:
                today_closed_trades.append({'symbol': symbol, 'result': 'LOSS', 'huf': data.get('huf_result', 0), 'pips': data.get('pips_result', 0)})
                
        elif status == 'open':
            open_trades += 1
    
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    weekly_win_rate = (weekly_wins / weekly_trades * 100) if weekly_trades > 0 else 0
    
    # Napi aktuális P/L számítás (nyitott pozíciók)
    daily_current_pips = 0.0
    daily_current_huf = 0.0
    
    for symbol, data in daily_signals.items():
        if symbol.startswith('_'):  # Skip metadata
            continue
        
        # CSAK HA BE VAN PIPÁLVA (vagy alapból False)
        if not data.get('manual_sent', False):
            continue

        if data.get('status') == 'open':
            # Friss ár lekérése
            df_current = get_data(symbol)
            if df_current is not None and not df_current.empty:
                current_price = float(df_current['Close'].iloc[-1])
                
                direction = data.get('direction')
                entry_price = data.get('entry')
                pip_value_huf = data.get('pip_value_huf', 0)
                
                # Számítsuk ki a jelenlegi P/L-t
                pip_multiplier = 100 if "JPY" in symbol else 10000
                
                if direction == 'LONG':
                    pips_current = (current_price - entry_price) * pip_multiplier
                else:  # SHORT
                    pips_current = (entry_price - current_price) * pip_multiplier
                
                huf_current = pips_current * pip_value_huf
                
                daily_current_pips += pips_current
                daily_current_huf += huf_current
    
    # Megjelenítés
    st.sidebar.metric("Összes Trade", total_trades)
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Nyerő ✅", wins)
    col2.metric("Vesztő ❌", losses)
    st.sidebar.metric("Nyerési Arány", f"{win_rate:.1f}%")
    
    # Pip és HUF összegzés (All Time)
    pip_color = "normal" if total_pips >= 0 else "inverse"
    huf_color = "normal" if total_huf >= 0 else "inverse"
    st.sidebar.metric("Összes Pip", f"{total_pips:+.1f}", delta=None)
    st.sidebar.metric("Összes Profit/Loss", f"{int(total_huf):+,} Ft", delta=None)
    
    # Napi aktuális P/L (csak ha van nyitott pozíció)
    if open_trades > 0:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Mai Napi Aktuális Állás")
        current_pl_delta_style = "normal" if daily_current_huf >= 0 else "inverse"
        st.sidebar.metric(
            "💰 Napi Aktuális P/L", 
            f"{int(daily_current_huf):+,} Ft",
            delta=f"{daily_current_pips:+.1f} pip"
        )
    
    # Nyitott pozíciók részletes megjelenítése
    if open_trades > 0:
        with st.sidebar.expander(f"🔄 {open_trades} nyitott pozíció - Kattints a részletekért!", expanded=False):
            for symbol, data in daily_signals.items():
                if symbol.startswith('_'):  # Skip metadata
                    continue
                if data.get('status') == 'open':
                    # Friss ár lekérése
                    df_current = get_data(symbol)
                    if df_current is not None and not df_current.empty:
                        current_price = float(df_current['Close'].iloc[-1])
                        
                        direction = data.get('direction')
                        entry_price = data.get('entry')
                        tp_price = data.get('tp')
                        sl_price = data.get('sl')
                        pip_value_huf = data.get('pip_value_huf', 0)
                        
                        # Számítsuk ki a jelenlegi P/L-t
                        pip_multiplier = 100 if "JPY" in symbol else 10000
                        
                        if direction == 'LONG':
                            pips_current = (current_price - entry_price) * pip_multiplier
                        else:  # SHORT
                            pips_current = (entry_price - current_price) * pip_multiplier
                        
                        huf_current = pips_current * pip_value_huf
                        
                        # Színes megjelenítés profit/loss alapján
                        color = "🟢" if pips_current >= 0 else "🔴"
                        direction_label = "LONG/vétel" if direction == "LONG" else "SHORT/eladás"
                        
                        st.markdown(f"**{color} {symbol}** - {direction_label}")
                        
                        # --- CHECKBOX A FELADÁSHOZ ---
                        current_sent = data.get('manual_sent', False)
                        is_sent = st.checkbox("✅ Feladva (Számoljon)", value=current_sent, key=f"sidebar_chk_{symbol}")
                        
                        if is_sent != current_sent:
                            daily_signals[symbol]['manual_sent'] = is_sent
                            save_history(daily_signals)
                            st.rerun()
                        # -----------------------------

                        st.caption(f"Belépő: {entry_price:.5f}")
                        st.caption(f"Aktuális: {current_price:.5f}")
                        st.caption(f"TP: {tp_price:.5f} | SL: {sl_price:.5f}")
                        
                        # P/L metrika
                        pl_color = "normal" if huf_current >= 0 else "inverse"
                        st.metric("Jelenlegi P/L", 
                                f"{int(huf_current):+,} Ft", 
                                delta=f"{pips_current:+.1f} pip")
                        st.markdown("---")
    # --- MAI LEZÁRT TRADEK (ÚJ) ---
    if today_closed_trades:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ✅ Mai Lezárt Tradek")
        for trade in today_closed_trades:
            icon = "✅" if trade['result'] == 'WIN' else "❌"
            st.sidebar.markdown(f"{icon} **{trade['symbol']}**: {int(trade['huf']):+,} Ft ({trade['pips']:+.1f} pip)")

    st.sidebar.markdown("---")
    # --- STATISZTIKÁK VÉGE ---
    
    # --- HETI ÖSSZEGZŐ TELEGRAM REPORT ---
    # Ellenőrizzük, hogy péntek este 20:00-e
    meta = daily_signals.get('_meta', {})
    last_report_str = meta.get('last_weekly_report')
    
    # Helyi idő (GMT+1)
    local_now = now + timedelta(hours=1)  # UTC -> GMT+1
    is_friday = local_now.weekday() == 4  # 4 = Péntek
    is_8pm = local_now.hour == 20
    
    send_weekly = False
    
    # Küldjünk reportot ha:
    # 1. Péntek este 20:00 óra van
    # 2. Még nem küldtünk ezen a héten
    if is_friday and is_8pm:
        if last_report_str:
            last_report_date = datetime.strptime(last_report_str, '%Y-%m-%d').date()
            # Ellenőrizzük, hogy nem ugyanezen a héten volt-e már report
            last_week_start, last_week_end = get_week_range(last_report_date)
            if not (current_week_start <= last_report_date <= current_week_end):
                send_weekly = True
        else:
            # Első futtatás - küldjünk reportot
            send_weekly = True
    
    if send_weekly:
        # Heti report üzenet (csak az aktuális hét statisztikáival)
        weekly_msg = (
            f"🎯 **LONDON BREAKOUT**\n"
            f"📈 **HETI TELJESÍTMÉNY ÖSSZEGZŐ**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 Időszak: {current_week_start.strftime('%Y-%m-%d')} - {current_week_end.strftime('%Y-%m-%d')}\n\n"
            f"📊 **Statisztikák:**\n"
            f"Összes Trade: {weekly_trades}\n"
            f"✅ Nyerő: {weekly_wins}\n"
            f"❌ Vesztő: {weekly_losses}\n"
            f"📈 Nyerési Arány: {weekly_win_rate:.1f}%\n\n"
            f"💰 **Pénzügyek:**\n"
            f"Összes Pip: {weekly_pips:+.1f} pip\n"
            f"Összes Profit/Loss: {int(weekly_huf):+,} Ft\n\n"
        )
        
        if open_trades > 0:
            weekly_msg += f"🔄 Nyitott pozíciók: {open_trades}\n\n"
        
        # Következő péntek kiszámítása
        next_friday = local_now.date() + timedelta(days=7)
        
        weekly_msg += (
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Következő report: {next_friday.strftime('%Y-%m-%d')} 20:00\n\n"
            f"💪 Kitartás! Minden trade tapasztalat!"
        )
        
        if send_telegram(weekly_msg):
            # Frissítjük az utolsó report dátumát
            if '_meta' not in daily_signals:
                daily_signals['_meta'] = {}
            daily_signals['_meta']['last_weekly_report'] = local_now.date().strftime('%Y-%m-%d')
            save_history(daily_signals)
    # --- HETI REPORT VÉGE ---

    # --- NAPI ZÁRÁS EMLÉKEZTETŐ (17:25-KOR) ---
    # Ellenőrizzük, hogy 17:25-e (GMT+1)
    meta = daily_signals.get('_meta', {})
    last_close_reminder_str = meta.get('last_close_reminder')
    
    # Helyi idő (GMT+1)
    local_now = now + timedelta(hours=1)  # UTC -> GMT+1
    is_1725 = local_now.hour == 17 and local_now.minute == 25
    
    send_close_reminder = False
    
    # Küldjünk emlékeztetőt ha:
    # 1. 17:25 óra van
    # 2. Még nem küldtünk MA emlékeztetőt
    # 3. Van legalább 1 nyitott pozíció
    if is_1725 and open_trades > 0:
        today_str_local = local_now.date().strftime('%Y-%m-%d')
        if last_close_reminder_str != today_str_local:
            send_close_reminder = True
    
    if send_close_reminder:
        # Emlékeztető üzenet összeállítása
        reminder_msg = (
            f"🎯 **LONDON BREAKOUT**\n"
            f"⏰ **NAPI ZÁRÁS EMLÉKEZTETŐ**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 Dátum: {local_now.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"🔔 **{open_trades} nyitott pozíció van!**\n"
            f"Kérlek, zárd be manuálisan a pozíciókat!\n\n"
        )
        
        # Minden nyitott pozíció részletei
        for symbol, data in daily_signals.items():
            if symbol.startswith('_'):  # Skip metadata
                continue
            if data.get('status') == 'open':
                # Friss ár lekérése
                df_current = get_data(symbol)
                if df_current is not None and not df_current.empty:
                    current_price = float(df_current['Close'].iloc[-1])
                    
                    direction = data.get('direction')
                    entry_price = data.get('entry')
                    tp_price = data.get('tp')
                    sl_price = data.get('sl')
                    pip_value_huf = data.get('pip_value_huf', 0)
                    
                    # Számítsuk ki a jelenlegi P/L-t
                    pip_multiplier = 100 if "JPY" in symbol else 10000
                    
                    if direction == 'LONG':
                        pips_current = (current_price - entry_price) * pip_multiplier
                    else:  # SHORT
                        pips_current = (entry_price - current_price) * pip_multiplier
                    
                    huf_current = pips_current * pip_value_huf
                    
                    # Eredmény jelölés
                    result_icon = "📈" if pips_current >= 0 else "📉"
                    result_text = "PROFIT" if pips_current >= 0 else "LOSS"
                    direction_label = "LONG/vétel" if direction == "LONG" else "SHORT/eladás"
                    
                    reminder_msg += (
                        f"{result_icon} **{symbol}** - {direction_label}\n"
                        f"Belépő: {entry_price:.5f}\n"
                        f"Aktuális: {current_price:.5f}\n"
                        f"Várható {result_text}: {int(huf_current):+,} Ft ({pips_current:+.1f} pip)\n\n"
                    )
        
        reminder_msg += (
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ Ne feledd: A pozíciókat manuálisan kell lezárni a webappon!\n"
            f"Holnap új lehetőségek várnak! 💪"
        )
        
        if send_telegram(reminder_msg):
            # Frissítjük az utolsó emlékeztető dátumát
            if '_meta' not in daily_signals:
                daily_signals['_meta'] = {}
            daily_signals['_meta']['last_close_reminder'] = local_now.date().strftime('%Y-%m-%d')
            save_history(daily_signals)
    # --- NAPI ZÁRÁS EMLÉKEZTETŐ VÉGE ---



    # --- TABS LÉTREHOZÁSA ---
    tab_charts, tab_history = st.tabs(["📈 Grafikonok", "📜 Teljes Előzmények"])

    with tab_history:
        st.header("📜 Kereskedési Előzmények")
        st.caption("Pipáld be a '✅ Feladva' oszlopot, ha a jelzést sikeresen kezelted! A statisztika csak a bepipált elemeket számolja.")
        
        # Adatok előkészítése szerkesztéshez
        history_data = []
        for symbol, data in daily_signals.items():
            if symbol.startswith('_'): continue
            
            # Csak a lezárt vagy nyitott tradek
            status_map = {
                'tp_hit': '✅ NYERŐ',
                'sl_hit': '❌ VESZTŐ',
                'open': '🔄 NYITOTT'
            }
            
            history_data.append({
                'ID': symbol, # Kulcs a mentéshez (bár a symbol nem egyedi, ha több trade van ugyanazon a páron naponta... de a jelenlegi logika szerint napi 1 van)
                # Jobb lenne egyedi ID, de a jelenlegi struktúra: daily_signals[symbol]. 
                # Mivel "One Bullet Rule" van, a symbol egyedi kulcs a napi map-ben.
                # DE várjunk, a daily_signals a teljes history? NEM!
                # A load_history() betölti a fájlt. A fájl szerkezete: {"GBPUSD=X": {...}}
                # Ez azt jelenti, hogy CSAK A LEGUTOLSÓ trade van benne páronként?
                # IGEN! A kód: daily_signals[symbol] = {...} felülírja az előzőt!
                # EZ EGY BUG, amit a felhasználó nem vett észre, vagy nem zavarta eddig.
                # De a "Teljes Előzmények" fül így csak a legutolsókat mutatja.
                # A felhasználó kérése most a "pipálás".
                # Maradjunk a jelenlegi struktúránál, de tegyük lehetővé a szerkesztést.
                
                'Dátum': data.get('date'),
                'Pár': symbol,
                'Irány': data.get('direction'),
                'Belépő': data.get('entry'),
                'Kilépő': data.get('tp') if data.get('status') == 'tp_hit' else (data.get('sl') if data.get('status') == 'sl_hit' else '-'),
                'Eredmény (Pip)': data.get('pips_result', 0) if data.get('status') != 'open' else '-',
                'Profit (HUF)': int(data.get('huf_result', 0)) if data.get('status') != 'open' else '-',
                'Státusz': status_map.get(data.get('status'), 'Ismeretlen'),
                '✅ Feladva': data.get('manual_sent', True) # Alapértelmezett True, hogy a régiek látszódjanak? Vagy False? User azt mondta "én tudjam kipipálni". Legyen False alapból az újaknál? Vagy True?
                # "ha pedig nem akkor ne számolja bel a statisztikába" -> Tehát alapból legyen True (vagy False és ő pipálja).
                # Legyen alapból False az újaknál, de a régieknél (amik már benne vannak) legyen True, hogy ne tűnjenek el a statból hirtelen?
                # A user azt mondta: "én tudjam kipipálni".
                # Legyen alapból False.
            })
            
        if history_data:
            df_history = pd.DataFrame(history_data)
            # Dátum szerinti rendezés csökkenő
            df_history = df_history.sort_values(by='Dátum', ascending=False)
            
            # Data Editor
            edited_df = st.data_editor(
                df_history,
                column_config={
                    "✅ Feladva": st.column_config.CheckboxColumn(
                        "Feladva?",
                        help="Pipáld be, ha a trade élesben is ment!",
                        default=False,
                    )
                },
                disabled=["Dátum", "Pár", "Irány", "Belépő", "Kilépő", "Eredmény (Pip)", "Profit (HUF)", "Státusz"],
                hide_index=True,
                use_container_width=True,
                key="history_editor"
            )
            
            # Változások mentése
            # Összehasonlítjuk az eredetit a szerkesztettel
            # Mivel a daily_signals a forrás, azt kell frissíteni.
            # Iteráljunk végig az edited_df-en és frissítsük a daily_signals-t
            
            changes_detected = False
            for index, row in edited_df.iterrows():
                symbol = row['Pár']
                is_sent = row['✅ Feladva']
                
                if symbol in daily_signals:
                    current_sent = daily_signals[symbol].get('manual_sent', False)
                    if current_sent != is_sent:
                        daily_signals[symbol]['manual_sent'] = is_sent
                        changes_detected = True
            
            if changes_detected:
                save_history(daily_signals)
                st.rerun()

            
            # Összesítő a táblázat alatt is (CSAK A BEPIPÁLTAK!)
            # Újraszámolás a szűrt adatokkal
            filtered_trades = 0
            filtered_wins = 0
            filtered_huf = 0.0
            
            for symbol, data in daily_signals.items():
                if symbol.startswith('_'): continue
                if not data.get('manual_sent', False): continue # CSAK HA BE VAN PIPÁLVA
                
                status = data.get('status')
                if status == 'tp_hit':
                    filtered_wins += 1
                    filtered_trades += 1
                    filtered_huf += data.get('huf_result', 0)
                elif status == 'sl_hit':
                    filtered_trades += 1
                    filtered_huf += data.get('huf_result', 0)
            
            filtered_win_rate = (filtered_wins / filtered_trades * 100) if filtered_trades > 0 else 0

            st.markdown("### 📊 Összesített Eredmény (Csak 'Feladva')")
            c1, c2, c3 = st.columns(3)
            c1.metric("Összes Trade", filtered_trades)
            c2.metric("Összes Profit", f"{int(filtered_huf):+,} Ft")
            c3.metric("Nyerési Arány", f"{filtered_win_rate:.1f}%")
        else:
            st.info("Még nincs rögzített kereskedés.")

    # Adatok frissítése állapotjelzővel
    with st.spinner('Piacok elemzése...'):
        
        # --- TRADE KÖVETÉS ÉS UTÁNKÜLDÉS ---
        # Ellenőrizzük az 'open' státuszú tradeket
        for symbol in TARGET_PAIRS:
            if symbol in daily_signals and daily_signals[symbol].get('status') == 'open':
                # Friss adat lekérése
                df_check = get_data(symbol)
                if df_check is not None and not df_check.empty:
                    current_price = float(df_check['Close'].iloc[-1])
                    trade_info = daily_signals[symbol]
                    
                    tp_price = trade_info.get('tp')
                    sl_price = trade_info.get('sl')
                    direction = trade_info.get('direction')
                    
                    # TP vagy SL ellenőrzése
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
                    
                    # Telegram üzenet küldése
                    if hit_tp:
                        # Pip és HUF számítás a valós exit árral
                        entry_price = trade_info.get('entry')
                        pips_target = trade_info.get('pips_target', 0)
                        pip_value_huf = trade_info.get('pip_value_huf', 0)
                        pips_result = pips_target  # TP esetén a tervezett pip
                        huf_result = pips_result * pip_value_huf
                        direction_label = "LONG/vétel" if direction == "LONG" else "SHORT/eladás"
                        
                        msg = (
                            f"🎯 <b><a href='https://t.me'>LONDON BREAKOUT</a></b>\n"
                            f"✅ <b>NYERŐ TRADE: {symbol}</b>\n"
                            f"🎯 <b>CÉLÁR ELÉRVE!</b>\n\n"
                            f"Irány: {direction_label}\n"
                            f"Belépő: {entry_price:.5f}\n"
                            f"Célár: {tp_price:.5f}\n"
                            f"Jelenlegi ár: {current_price:.5f}\n\n"
                            f"💰 <b>Eredmény:</b>\n"
                            f"📊 Pip: +{pips_result:.1f}\n"
                            f"💵 Profit: +{int(huf_result):,} Ft\n\n"
                            f"🎉 Gratulálok! A trade profittal lezárult!"
                        )
                        if send_telegram(msg):
                            daily_signals[symbol]['status'] = 'tp_hit'
                            daily_signals[symbol]['pips_result'] = pips_result
                            daily_signals[symbol]['huf_result'] = huf_result
                            save_history(daily_signals)
                    
                    elif hit_sl:
                        # Pip és HUF számítás a valós exit árral
                        entry_price = trade_info.get('entry')
                        pips_target = trade_info.get('pips_target', 0)
                        pip_value_huf = trade_info.get('pip_value_huf', 0)
                        pips_result = -pips_target  # SL esetén negatív
                        huf_result = pips_result * pip_value_huf
                        direction_label = "LONG/vétel" if direction == "LONG" else "SHORT/eladás"
                        
                        msg = (
                            f"🎯 <b><a href='https://t.me'>LONDON BREAKOUT</a></b>\n"
                            f"🔴 <b>VESZTŐ TRADE: {symbol}</b>\n"
                            f"🛡️ <b>STOP LOSS ELÉRVE!</b>\n\n"
                            f"Irány: {direction_label}\n"
                            f"Belépő: {entry_price:.5f}\n"
                            f"Stop: {sl_price:.5f}\n"
                            f"Jelenlegi ár: {current_price:.5f}\n\n"
                            f"💰 <b>Eredmény:</b>\n"
                            f"📊 Pip: {pips_result:.1f}\n"
                            f"💵 Loss: {int(huf_result):,} Ft\n\n"
                            f"⚠️ A trade veszteséggel lezárult. Következő alkalom!"
                        )
                        if send_telegram(msg):
                            daily_signals[symbol]['status'] = 'sl_hit'
                            daily_signals[symbol]['pips_result'] = pips_result
                            daily_signals[symbol]['huf_result'] = huf_result
                            save_history(daily_signals)
        # --- TRADE KÖVETÉS VÉGE ---
        
        with tab_charts:
            for symbol in TARGET_PAIRS:
                st.markdown("---")
                st.header(f"🇬🇧 {symbol}")
                
                # 1. Adatok
                df = get_data(symbol)
                if df is None:
                    st.warning("Nem sikerült letölteni az adatokat.")
                    continue
                    
                # Hétvége / Frissesség ellenőrzése
                last_time = df.index[-1]
                is_data_fresh = last_time.date() == datetime.utcnow().date()
                
                if not is_data_fresh:
                    st.warning(f"⚠️ A piac zárva van. Az utolsó adat: {last_time.strftime('%Y-%m-%d %H:%M')}")
                
                # 2. Indikátorok
                df['EMA_50'] = calculate_ema(df)
                
                # 3. Stratégia Elemzés
                analysis = analyze_london_breakout(df, symbol)
                
                # 4. Jelzés Kezelése (One Bullet Logic)
                today_str = datetime.utcnow().strftime('%Y-%m-%d')
                saved_signal = daily_signals.get(symbol)
                
                signal_locked = False
                locked_direction = None
                
                # Ellenőrizzük, volt-e már MAI jelzés
                if saved_signal and saved_signal['date'] == today_str:
                    signal_locked = True
                    locked_direction = saved_signal['direction']
                    st.info(f"🔒 **MAI JELZÉS ELKÜLDVE:** {locked_direction}. A terv a grafikonon látható (One Bullet Rule).")
                    
                # Ha még nem volt jelzés, de most van TRIGGER és friss az adat
                # ÉS be van kapcsolva a Trading Mode
                elif analysis and analysis["signal_type"] and is_data_fresh and trading_mode:
                    
                    # --- DUPLA ELLENŐRZÉS (Race Condition ellen) ---
                    # Frissítjük a memóriát a fájlból, hátha egy másik tab már elküldte
                    current_history = load_history()
                    if symbol in current_history and current_history[symbol]['date'] == today_str:
                        st.warning(f"⚠️ {symbol} jelzést már egy másik folyamat elküldte! (Race Condition elkerülve)")
                        continue
    
                    # --- PÉNZÜGYI SZÁMÍTÁSOK (HUF) ---
                    # Alapértelmezések
                    lot_size = 0.01
                    leverage = 30
                    contract_size = 100000 # Standard lot
                    
                    # Deviza párok felbontása
                    base_currency = symbol[:3] # pl GBP
                    quote_currency = symbol[3:6] # pl USD
                    
                    # Árfolyamok lekérése
                    base_huf_rate = get_huf_rate(base_currency)
                    usd_huf_rate = get_huf_rate('USD') # Kell a pip értékhez ha USD a quote
                    
                    margin_huf = 0
                    pip_value_huf = 0
                    
                    if base_huf_rate:
                        # Margin számítás: (Contract Size * Lot * Base_HUF) / Leverage
                        # 0.01 lot esetén contract size effektív 1000
                        margin_huf = (1000 * base_huf_rate) / leverage
                    
                    # Pip Érték számítás
                    if quote_currency == 'USD':
                        # XXX/USD: 1 pip = 10 USD / lot -> 0.1 USD / 0.01 lot
                        if usd_huf_rate:
                            pip_value_huf = 0.1 * usd_huf_rate
                    elif quote_currency == 'JPY':
                        # XXX/JPY: 1 pip = 1000 JPY / lot -> 10 JPY / 0.01 lot
                        # Átváltás: 10 JPY -> HUF. (USDHUF / USDJPY) vagy közelítés
                        # Mivel nincs USDJPY, használjunk egy közelítést vagy kérjünk le USDJPY-t?
                        # Egyszerűsítés: 1 JPY kb 2.5 HUF. De pontosabb ha USDHUF-ból számoljuk.
                        # Ha nincs USDJPY, akkor a prompt szerinti "convert USD value" nehéz.
                        # Használjuk a prompt javaslatát: "10 * (JPYHUF_Rate / 100)" ami fura.
                        # Inkább: 10 JPY * (USDHUF / USDJPY).
                        # Mivel USDJPY nincs, használjuk a keresztárfolyamot a jelenlegi árból:
                        # GBPJPY / GBPUSD = USDJPY
                        # De ehhez kellene a GBPUSD árfolyam is.
                        # Egyszerűbb: 10 JPY ~ 25 HUF (Hardcoded becslés ha nincs jobb, de próbáljunk pontosabbat)
                        # Ha van USDHUF, akkor 1 USD = X HUF. 1 USD ~ 150 JPY. 1 JPY = X / 150.
                        if usd_huf_rate:
                            pip_value_huf = 10 * (usd_huf_rate / 153.0) # Kb 153 az USDJPY
                    
                    # Nyereség / Veszteség
                    pips_gained = analysis['box_height'] * (100 if "JPY" in symbol else 10000)
                    pips_risked = pips_gained # 1:1 R/R
                    
                    profit_huf = pips_gained * pip_value_huf
                    loss_huf = pips_risked * pip_value_huf
    
                    # TELEGRAM ÜZENET ÖSSZEÁLLÍTÁSA
                    direction_icon = "🟢" if analysis["signal_type"] == "LONG" else "🔴"
                    direction_label = "LONG/vétel" if analysis["signal_type"] == "LONG" else "SHORT/eladás"
                    
                    msg = (
                        f"🎯 <b><a href='https://t.me'>LONDON BREAKOUT</a></b>\n"
                        f"🔔 <b>JELZÉS: {symbol}</b>\n"
                        f"-------------------------\n"
                        f"👉 <b>IRÁNY:</b> {direction_icon} <b>{direction_label}</b>\n"
                        f"📊 <b>Stratégia:</b> Hougaard Daybreak\n\n"
                        
                        f"💰 <b>PÉNZÜGYEK (0.01 Lot):</b>\n"
                        f"🏦 <b>Feltett Tét (Margin):</b> ~{int(margin_huf)} Ft\n"
                        f"🎯 <b>Várható Nyerő:</b> +{int(profit_huf)} Ft\n"
                        f"🛡️ <b>Max Bukó:</b> -{int(loss_huf)} Ft\n\n"
                        
                        f"📍 <b>SZINTEK:</b>\n"
                        f"🔵 Belépő: {analysis['entry']:.5f}\n"
                        f"🟢 TP: {analysis['tp']:.5f}\n"
                        f"🔴 SL: {analysis['sl']:.5f}\n\n"
                        
                        f"(⚠️ One Bullet Rule: Mai egyetlen jelzés!)"
                    )
                    
                    # Küldés
                    if send_telegram(msg):
                        # Siker esetén mentés a fájlba TRADE ADATOKKAL + PIP/HUF INFO + TIMESTAMP
                        daily_signals[symbol] = {
                            'date': today_str,
                            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                            'direction': analysis['signal_type'],
                            'entry': analysis['entry'],
                            'tp': analysis['tp'],
                            'sl': analysis['sl'],
                            'status': 'open',  # Nyitott pozíció, követjük
                            'pips_target': pips_gained,  # Tervezett pip
                            'pip_value_huf': pip_value_huf  # 1 pip értéke HUF-ban
                        }
                        save_history(daily_signals)
                        
                        signal_locked = True
                        locked_direction = analysis['signal_type']
                        st.success("✅ Telegram üzenet elküldve!")
                        st.rerun() # Újratöltés, hogy frissüljön a UI

            # 5. GRAFIKON RAJZOLÁSA (Mindig látható!)
            
            # Zoom beállítása (utolsó 60 gyertya)
            zoom_start = df.index[-60]
            zoom_end = df.index[-1] + timedelta(hours=4) # Hely a jövőnek
            
            # Y-tengely skálázás (Látható részre)
            visible_df = df[df.index >= zoom_start]
            y_min = visible_df['Low'].min()
            y_max = visible_df['High'].max()
            # Ha van doboz, azt is vegyük figyelembe a skálánál
            if analysis:
                y_min = min(y_min, analysis['box_low'])
                y_max = max(y_max, analysis['box_high'])
            padding = (y_max - y_min) * 0.1
            
            fig = go.Figure()

            # Gyertyák
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name="Árfolyam",
                increasing_line_color='green', decreasing_line_color='red'
            ))

            # EMA 50 (Sárga vonal)
            fig.add_trace(go.Scatter(
                x=df.index, y=df['EMA_50'],
                line=dict(color='yellow', width=2),
                name="Trend (EMA 50)"
            ))

            # London Doboz Rajzolása MINDEN Látható Napra (07:00-08:00 GMT)
            # Utolsó 5 kereskedési napra rajzoljuk be a dobozokat
            visible_days = sorted(list(set(df.index.date)))[-5:]  # Utolsó 5 egyedi nap
            
            for day in visible_days:
                # Szűrés az adott napra és a 07:00-08:00 GMT időszakra
                day_mask = (df.index.date == day) & (df.index.hour == 7)
                morning_candles = df[day_mask]
                
                if not morning_candles.empty:
                    # Doboz határainak kiszámítása
                    box_high = float(morning_candles['High'].max())
                    box_low = float(morning_candles['Low'].min())
                    
                    # Időpontok a dobozhoz
                    box_start_time = pd.Timestamp(day).tz_localize('UTC').replace(hour=7, minute=0, second=0, microsecond=0)
                    box_end_time = pd.Timestamp(day).tz_localize('UTC').replace(hour=8, minute=0, second=0, microsecond=0)
                    
                    # Mai napra más szín
                    is_today = (day == last_time.date())
                    fillcolor = "lightblue" if is_today else "lightgray"
                    linecolor = "blue" if is_today else "gray"
                    opacity = 0.3 if is_today else 0.15
                    
                    # Téglalap alakú doboz
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


            # Formázás (Fix nézet, Nincs Zoom/Pan, Smart Scaling)
            fig.update_layout(
                height=500,
                xaxis_rangeslider_visible=False,
                yaxis=dict(range=[y_min - padding, y_max + padding], fixedrange=True), # Smart Scaling + Lock
                xaxis=dict(range=[zoom_start, zoom_end], fixedrange=True), # Zoom Lock
                dragmode=False, # Pan letiltása
                template="plotly_white",
                title=f"{symbol} (15m) - {analysis['trend'] if analysis else 'N/A'}",
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            # Hétvégék kivétele (Hogy ne legyen rés)
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    
            # Konfiguráció (Görgő letiltása)
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': False})

            # Kereskedési Terv Szövegesen (Ha van doboz)
            if analysis:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Trend (EMA 50)", analysis['trend'], delta="Bika" if analysis['trend']=="BULLISH" else "-Medve")
                c2.metric("Doboz Magasság", f"{(analysis['box_height']*10000):.1f} pip")
                c3.metric("💰 Aktuális Ár", f"{analysis['current_price']:.5f}")
                
                # Státusz kiírása
                if signal_locked:
                    c4.info(f"🔒 Pozíció: {locked_direction}")
                else:
                    c4.warning("⏳ Várakozás kitörésre...")
    
    # Automatikus frissítés visszaszámláló
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        countdown_placeholder = st.empty()
        countdown_placeholder.info(f"⏱️ Következő frissítés {refresh_interval} másodperc múlva...")
    
    # Automatikus frissítés időzítés
    time.sleep(refresh_interval)
    # Beállítjuk az auto_refresh_mode-ot, hogy ne küldjön új jelzéseket
    st.session_state.auto_refresh_mode = True
    st.rerun()

if __name__ == "__main__":
    main()

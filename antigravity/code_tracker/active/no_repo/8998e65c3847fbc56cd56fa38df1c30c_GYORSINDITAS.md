�# TTM Squeeze Webapp - Gyorsindítás

## 🚀 Azonnali Használat

### 1. Dashboard Indítása

```bash
cd c:\Users\Tomi\FOREX
streamlit run app.py
```

A böngésződben megnyílik: `http://localhost:8501`

### 2. Automatikus Monitoring (Opcionális)

24/7 háttérfigyelés Telegram értesítésekkel:

```bash
python scheduler.py
```

---

## 📱 Telegram Beállítások

✅ **Telegram már konfigurálva van!**

- Bot Token: `7487229026:AAH51YJ4atFsvqHKfQj9l_QU7ytJMIwo0w0`
- Chat ID: `1736205722`

Teszteld: 
```bash
python -c "from telegram_notifier import TelegramNotifier; n = TelegramNotifier(); n.test_connection()"
```

---

## 🎯 Figyelt Devizapárok

1. EURUSD
2. GBPUSD
3. USDJPY
4. GBPJPY
5. AUDUSD

---

## ⚙️ Konfiguráció

Szerkeszd a `config.py` fájlt:

```python
# Párok módosítása
MONITORED_PAIRS = ['EURUSD', 'GBPUSD', ...]

# Timeframe változtatása
DEFAULT_INTERVAL = '1h'  # Lehetőségek: '15m', '30m', '1h', '4h'

# Ellenőrzési gyakoriság (scheduler)
CHECK_INTERVAL = 900  # másodperc (15 perc)
```

---

## 📊 TTM Squeeze Stratégia

**Squeeze ON** 🟢  
- Konszolidáció, alacsony volatilitás
- Várj a kitörésre

**Squeeze FIRE** 🔴  
- Kitörés, magas volatilitás
- 🚀 BUY ha Momentum > 0
- 🔻 SELL ha Momentum < 0

---

## 🆘 Hibaelhárítás

**Probléma:** Nincs adat
```bash
# Változtass timeframe-et vagy időszakot
config.py-ban DEFAULT_INTERVAL = '4h'
```

**Probléma:** Telegram nem működik
```bash
# Ellenőrizd a .env fájlt
type .env
```

---

## 📁 Projekt Fájlok

| Fájl | Leírás |
|------|--------|
| `app.py` | Streamlit dashboard |
| `ttm_squeeze.py` | TTM számítások |
| `data_fetcher.py` | Adatletöltés |
| `scheduler.py` | Automatikus monitoring |
| `config.py` | Beállítások |

---

**Tovább a részletes dokumentációhoz:** [README.md](README.md)
�*cascade082+file:///c:/Users/Tomi/FOREX/GYORSINDITAS.md
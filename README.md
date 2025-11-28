# 🇬🇧 London Breakout Pro 2025

Ez a **London Breakout Pro 2025** kereskedési algoritmus hivatalos repository-ja. A rendszer automatikusan figyeli a devizapiacokat és Telegramon riasztást küld a londoni nyitás (07:00-08:00 GMT) körüli kitöréseknél.

🔗 **ÉLŐ DEMO:** [https://forex-robot-u7sx7cbkeyn3xmtggnqpzw.streamlit.app/](https://forex-robot-u7sx7cbkeyn3xmtggnqpzw.streamlit.app/)

---

## ✨ Új: Twelve Data API Integráció

**Pontosabb árfolyamok XTB-kompatibilis forrásból!**

- ✅ **Broker-minőségű adatok** (nem késleltetett Yahoo Finance)
- ✅ **Batch request optimalizálás** (1 API call = 3 devizapár)
- ✅ **Ingyenes tier** (8 hívás/perc, 800/nap - bőven elég)
- ✅ **Automatikus fallback** yfinance-ra ha nem elérhető

---

## 🚀 Funkciók

*   **Multi-Asset Monitorozás:** Egyszerre figyeli a 3 fő devizapárt (`GBPUSD`, `GBPJPY`, `EURUSD`).
*   **Hougaard Daybreak Stratégia:**
    *   07:00-08:00 GMT London doboz meghatározása
    *   EMA 50 trendszűrés
    *   1:1 Risk/Reward arány
*   **Automata Telegram Riasztás:**
    *   Azonnali üzenetküldés kitöréskor
    *   Beépített kockázatkezelés (dinamikus lot sizing)
    *   Kereskedési terv (Belépő, SL, TP) generálása
*   **Pontos adatok:** Twelve Data API (vagy yfinance fallback)

---

## 🛠️ Telepítés

### 1. Repository klónozása
```bash
git clone https://github.com/vagyokakivagyok09/forex-robot.git
cd forex-robot
```

### 2. Függőségek telepítése
```bash
pip install -r requirements.txt
```

### 3. API Kulcsok beállítása

#### Telegram Bot (kötelező)
1. Készíts Telegram botot: [@BotFather](https://t.me/BotFather)
2. Szerezd meg a chat ID-t: [@userinfobot](https://t.me/userinfobot)

#### Twelve Data API (ajánlott, de opcionális)
1. Regisztrálj: [Twelve Data Free Tier](https://twelvedata.com/pricing)
2. Generálj API kulcsot a dashboardon
3. Limit: 8 hívás/perc, 800/nap (ingyenes)

#### Secrets konfiguráció

Hozz létre `.streamlit/secrets.toml` fájlt:

```toml
TWELVE_DATA_API_KEY = "a_te_api_kulcsod"
TELEGRAM_BOT_TOKEN = "a_te_bot_tokened"
TELEGRAM_CHAT_ID = "a_te_chat_id-d"
```

> [!NOTE]
> Ha nincs Twelve Data API key, a rendszer automatikusan yfinance-t használ (kevésbé pontos, de működik).

### 4. Alkalmazás indítása

**Lokálisan:**
```bash
streamlit run app.py
```

**Streamlit Cloud-on:**
1. Push GitHub-ra
2. Deploy Streamlit Cloud-on
3. Secrets-et add hozzá a dashboard Settings → Secrets menüben

---

## 📊 Használat

### Adatforrás státusz

A sidebar mutatja az aktív adatforrást:
- ✅ **Twelve Data API** - Pontos, broker-minőségű árfolyamok
- ⚠️ **YFinance** - Késleltetett Yahoo Finance adatok (eltérhet XTB-től)

### Jelzések

1. **Trading Mode** bekapcsolása a sidebarban
2. Telegram értesítések 07:00-20:00 magyar időben
3. Manuális trade végrehajtás XTB-n a jelzés alapján

### Teljesítmény követés

- **Nyitott pozíciók:** Sidebar expandable section
- **Lezárt tradek:** "Teljes Előzmények" tab
- **Statisztikák:** Sidebar metrics (nyerési arány, pip összesítés, HUF profit/loss)

---

## 🧪 Tesztelés

### Twelve Data API teszt
```bash
python test_twelve_data.py
```

Elvárt kimenet:
```
✅ API is accessible!
✅ Batch request successful!
   GBP/USD: 1.3242
   GBP/JPY: 206.8
   EUR/USD: 1.1598
✅ Historical data retrieved: 100 candles
```

---

## 📈 Használt Technológiák

*   **Python 3.8+**
*   **Streamlit** - Web dashboard
*   **Plotly** - Interaktív chartok
*   **Twelve Data API** - Forex adatok (pontos)
*   **yfinance** - Fallback adatforrás
*   **Telegram Bot API** - Értesítések

---

## 🔧 Konfiguráció

### Konstansok (`app.py`)

```python
TARGET_PAIRS = ['GBPUSD=X', 'GBPJPY=X', 'EURUSD=X']  # Figyelt párok
BUFFER_PIPS = 0.0003  # Kitörési buffer (3 pip)
ACCOUNT_BALANCE = 1_000_000  # Számla HUF
RISK_PERCENT = 0.01  # Kockáztatott % (1%)
```

### Frissítési időközök

- **Aktív kereskedési idő** (06:00-23:00 GMT): 30 másodperc
- **Éjszaka/Hétvége**: 5 perc

---

## 🚨 Fontos Megjegyzések

> [!WARNING]
> **Yfinance vs Twelve Data**
> - Yfinance: Késleltetett Yahoo Finance adatok → **eltérhet az XTB árfolyamoktól**
> - Twelve Data: Valós idejű broker feed → **pontosabb trade szintek**

> [!CAUTION]
> **Kockázatkezelés**
> - A webapp **csak jelzéseket küld**, nem nyit pozíciókat
> - Minden trade-et **manuálisan** kell végrehajtani XTB-n
> - Ellenőrizd a pozícióméretet és stop loss-t végrehajtás előtt!

---

## 📝 Changelog

### v2.0.0 - Twelve Data Integration
- ✅ Twelve Data API elsődleges adatforrásként
- ✅ Batch request optimalizálás (rate limit hatékonyság)
- ✅ Automatikus fallback yfinance-ra
- ✅ API status indicator sidebar-ban

### v1.x - Korábbi verziók
- Hougaard Daybreak stratégia implementációja
- Dinamikus lot sizing
- Telegram értesítések
- GitHub Actions 24/7 futás

---

## 🤝 Támogatás

Kérdések, hibák, javaslatok: [GitHub Issues](https://github.com/vagyokakivagyok09/forex-robot/issues)

---

*Készítette: vagyokakivagyok09* | *Utolsó frissítés: 2025-11-28*

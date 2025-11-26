�## GitHub Feltöltés - Lépésről Lépésre (Git nélkül)

Mivel nincs Git telepítve a gépeden, a legegyszerűbb módszer a GitHub web felületen keresztüli feltöltés.

---

## 🌐 OPCIÓ 1: GitHub Web Feltöltés (AJÁNLOTT - Legegyszerűbb!)

### 1. lépés: Új Repository Létrehozása

1. **Menj a [github.com](https://github.com)**
2. **Jelentkezz be** a fiókoddal
3. **Kattints a "+" ikonra** a jobb felső sarokban → **"New repository"**

### 2. lépés: Repository Beállítások

Töltsd ki a következőket:

```
Repository name: ttm-squeeze
Description: Real-time forex trading dashboard with TTM Squeeze momentum strategy
```

**Fontos beállítások:**
- ✅ **Public** (nyilvános)
- ❌ **NE** add hozzá a README-t (már megvan)
- ❌ **NE** add hozzá a .gitignore-t (már megvan)
- ❌ **NE** add hozzá a license-t (már megvan)

**Kattints**: **"Create repository"**

---

### 3. lépés: Fájlok Feltöltése

A repository létrehozása után látni fogsz egy üres oldalt. Kattints:

**"uploading an existing file"** linkre

VAGY

Kattints a **"Add file"** → **"Upload files"** gombra

---

### 4. lépés: Fájlok Kiválasztása

**Húzd be vagy válaszd ki** az alábbi fájlokat a `c:\Users\Tomi\FOREX` mappából:

#### ✅ Feltöltendő fájlok (18 db):

```
app.py
config.py
data_fetcher.py
get_chat_id.py
requirements.txt
scheduler.py
telegram_notifier.py
test_modules.py
trade_tracker.py
ttm_squeeze.py
.gitignore
LICENSE
README.md
DEPLOYMENT.md
GYORSINDITAS.md
.env.example
.streamlit/secrets.toml
```

#### ❌ NE töltsd fel:

```
.env (tartalmazza a titkos tokeneket!)
trade_history.json (személyes adatok)
__pycache__ (Python cache)
.venv (virtual environment)
```

---

### 5. lépés: Commit

A fájlok kiválasztása után:

**Commit message:**
```
Initial commit: TTM Squeeze Trading Dashboard
```

**Kattints:** **"Commit changes"**

---

### 6. lépés: Ellenőrzés

✅ Ellenőrizd, hogy minden fájl feltöltődött
✅ Nézd meg a README.md-t - szépen renderelve látható
✅ Győződj meg róla, hogy a `.env` fájl **NINCS** ott!

---

## 🚀 STREAMLIT CLOUD DEPLOYMENT

Most már készen állsz a Streamlit Cloud-ra!

### 1. lépés: Streamlit Cloud Regisztráció

1. **Menj a [share.streamlit.io](https://share.streamlit.io)**
2. **Kattints "Sign up"**
3. **Válaszd:** "Continue with GitHub"
4. **Engedélyezd** a Streamlit számára a GitHub hozzáférést

---

### 2. lépés: Új App Létrehozása

1. **Kattints:** "New app"
2. **Töltsd ki:**

```
Repository: [TeFelhasználóneved]/ttm-squeeze
Branch: main
Main file path: app.py
```

**App URL:** `ttm-squeeze` (vagy bármilyen egyedi név)

---

### 3. lépés: SECRETS Beállítása (FONTOS!)

**MIELŐTT deploy-olnál**, kattints:

**"Advanced settings"** → **"Secrets"**

Másold be **PONTOSAN** ezt a formátumot:

```toml
[TELEGRAM]
TELEGRAM_BOT_TOKEN = "7487229026:AAH51YJ4atFsvqHKfQj9l_QU7ytJMIwo0w0"
TELEGRAM_CHAT_ID = "1736205722"
```

⚠️ **NAGYON FONTOS:**
- A formátum pontosan ilyen legyen (TOML formátum)
- `[TELEGRAM]` section header
- Idézőjelek kötelezők!

---

### 4. lépés: Deploy!

**Kattints:** **"Deploy!"**

⏰ **Várj 2-3 percet** amíg a build lefut.

---

### 5. lépés: Tesztelés

Ha minden jól ment:

✅ Látod a dashboard-ot
✅ Forex párok adatai betöltődnek
✅ Squeeze státuszok láthatók
✅ Sidebar mutatja a Telegram státuszt: "🟢 Enabled"

**Az app URL-je valami ilyesmi lesz:**
```
https://ttm-squeeze.streamlit.app
```

vagy

```
https://[választott-név].streamlit.app
```

---

## 🎉 KÉSZ!

**Az app mostantól 24/7 elérhető!**

Megoszthatod a linket bárkivel, vagy csak te használhatod.

---

## 🔄 Frissítések (Később)

Ha módosítasz a kódon:

1. Töltsd fel a módosított fájlt GitHubra (Upload files)
2. Streamlit automatikusan újra-deployal!

---

## ❓ Hibaelhárítás

**Probléma:** "No module named..."
- Ellenőrizd, hogy a `requirements.txt` feltöltődött-e

**Probléma:** Telegram nem működik
- Ellenőrizd a Secrets formátumot (TOML!)
- Biztos, hogy `[TELEGRAM]` section van?

**Probléma:** Nem tölt be adat
- Várj pár percet, a yfinance lehet lassú
- Próbáld meg később

---

## 📞 Kérdésed van?

Szólj bátran, segítek! 🚀
�#*cascade0822file:///c:/Users/Tomi/FOREX/GITHUB_UPLOAD_GUIDE.md
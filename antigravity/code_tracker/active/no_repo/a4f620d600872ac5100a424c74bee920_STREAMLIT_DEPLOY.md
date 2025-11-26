�## Streamlit Cloud Deployment - Lépésről Lépésre

## 🎯 MOSTANI FELADAT: Online App Deploy

---

## 1. lépés: Streamlit Cloud Megnyitása

**Menj a böngészőben:**
```
https://share.streamlit.io
```

✅ Meg kellene nyílnia egy Streamlit Cloud landing page-nek

---

## 2. lépés: Bejelentkezés GitHub-bal

**Kattints:** "Sign in" vagy "Continue with GitHub"

Ez átirányít GitHub-ra, ahol meg kell erősítened a hozzáférést.

**FONTOS:** 
- Engedélyezd a Streamlit-nek, hogy hozzáférjen a repository-idhoz
- Ez biztonságos, a Streamlit hivatalos szolgáltatása

---

## 3. lépés: Új App Létrehozása

Bejelentkezés után:

**Kattints:** "New app" vagy "Create app" gombra

---

## 4. lépés: Repository Beállítások

Töltsd ki a következőket:

### Repository kiválasztása:
```
Repository: [TeFelhasználóneved]/ttm-squeeze
Branch: main
Main file path: app.py
```

**Példa:**
```
Repository: tomi/ttm-squeeze
Branch: main
Main file path: app.py
```

### App URL (opcionális):
```
App URL: ttm-squeeze
```

vagy bármilyen egyedi név

---

## 5. lépés: SECRETS Beállítása ⚠️ KRITIKUS!

**MIELŐTT deploy-olsz!**

**Kattints:** "Advanced settings" alul

Majd:

**Kattints:** "Secrets" tab-ra

### Másold be PONTOSAN ezt:

```toml
[TELEGRAM]
TELEGRAM_BOT_TOKEN = "7487229026:AAH51YJ4atFsvqHKfQj9l_QU7ytJMIwo0w0"
TELEGRAM_CHAT_ID = "1736205722"
```

⚠️ **NAGYON FONTOS:**
- Pont így, a `[TELEGRAM]` sorral kezdve
- Idézőjelek kötelezők!
- Ne hagyd ki a section headert!

---

## 6. lépés: Deploy!

**Kattints:** "Deploy!" gomb (jobb alsó sarok)

---

## 7. lépés: Várakozás (2-3 perc)

A Streamlit Cloud most:
- ✓ Letölti a kódot GitHubról
- ✓ Telepíti a requirements.txt csomagokat
- ✓ Elindítja az appot

Látni fogsz egy build log-ot, ahol folyamatosan írja, mit csinál.

**Normális üzenetek:**
```
Cloning repository...
Installing requirements...
Running app.py...
```

---

## 8. lépés: APP KÉSZ! 🎉

Ha minden rendben van:

✅ A dashboard betöltődik
✅ Látod a forex párokat
✅ Squeeze státuszok frissülnek
✅ Sidebar-ban: Telegram 🟢 Enabled

**Az URL valami ilyesmi:**
```
https://ttm-squeeze.streamlit.app
```

vagy

```
https://[általad-választott-név].streamlit.app
```

---

## 🔗 APP MEGOSZTÁSA

**Az URL-t:**
- Bárkivel megoszthatod
- Könyvjelzőzheted
- Telefonról is elérhető
- **24/7 elérhető!**

---

## ❓ Hibaelhárítás

### Probléma: "ModuleNotFoundError"

**Megoldás:**
- Ellenőrizd, hogy a `requirements.txt` feltöltődött-e GitHubra
- Nézd meg, hogy minden csomag benne van-e

### Probléma: Telegram nem működik (sidebar: Disabled)

**Megoldás:**
- Menj Settings → Secrets
- Ellenőrizd a TOML formátumot:
  - Van `[TELEGRAM]` header?
  - Idézőjelek rendben vannak?
- Mentsd el újra a secrets-et
- Reboot app (Settings → Reboot)

### Probléma: "No data available"

**Megoldás:**
- Ez normális lehet hétvégén (forex piac zárva)
- Várj pár percet, a yfinance néha lassú
- Próbáld meg hétköznap

### Probléma: App "sleeping" / "waking up"

**Megoldás:**
- Streamlit ingyenes tier: inaktivitás után sleep
- Első látogatáskor 10-20 mp indulás
- Ez normális, nem hiba

---

## 🔄 Frissítések a Jövőben

Ha módosítod a kódot:

1. **Töltsd fel GitHubra** a változtatásokat (web feltöltés)
2. **Streamlit automatikusan újra-deployal!**
3. 1-2 percen belül élesben lesz

---

## 📊 Streamlit Cloud Dashboard

**Settings gomb** (jobb felső sarok):
- **Reboot app** - Újraindítás
- **Edit Secrets** - Secrets módosítása
- **Delete app** - App törlése
- **Logs** - Részletes app logok
- **Analytics** - Látogatási statisztikák

---

## ✅ ELLENŐRZŐ LISTA

- [ ] Bejelentkeztem Streamlit Cloud-ba
- [ ] Repository kiválasztva (ttm-squeeze)
- [ ] Branch: main
- [ ] Main file: app.py
- [ ] Secrets beállítva (TOML formátum!)
- [ ] Deploy gomb megnyomva
- [ ] Build log nézése
- [ ] App betöltődött
- [ ] Telegram: Enabled a sidebar-ban
- [ ] URL elmentve/könyvjelzőzve

---

## 🎉 GRATULÁLOK!

**Az app mostantól 24/7 online!**

Akár telefonról is elérheted az URL-en keresztül! 📱

**Következő lépés:** Monitorozd a squeeze jelzéseket és kapsz Telegram értesítéseket! 🚀
�#*cascade082/file:///c:/Users/Tomi/FOREX/STREAMLIT_DEPLOY.md
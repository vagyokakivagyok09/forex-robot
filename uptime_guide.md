# 0-24 Működés Biztosítása (UptimeRobot Útmutató)

A Streamlit Cloud alkalmazások alapértelmezetten "elalszanak", ha nincs aktív látogató. A folyamatos működéshez (hogy a Telegram üzenetek 07:00-16:00 között is megérkezzenek) egy külső szolgáltatást kell használnod, ami rendszeresen "megpingeli" az oldalt.

## Megoldás: UptimeRobot (Ingyenes)

Ez a szolgáltatás 5 percenként megnyitja az oldaladat a háttérben, így a Streamlit szerverei aktívnak érzékelik, és nem állítják le a programot.

### Beállítási Lépések:

1.  **Regisztráció**:
    *   Menj a [uptimerobot.com](https://uptimerobot.com/) oldalra.
    *   Kattints a "Register for FREE" gombra és regisztrálj.

2.  **Monitor Létrehozása**:
    *   Belépés után kattints az **"Add New Monitor"** gombra (bal felső sarok).
    *   **Monitor Type**: Válaszd a `HTTP(s)` típust.
    *   **Friendly Name**: Adj neki egy nevet (pl. `London Breakout`).
    *   **URL (or IP)**: Másold be a Streamlit alkalmazásod publikus linkjét (pl. `https://london-breakout-pro.streamlit.app`).
    *   **Monitoring Interval**: Állítsd `5 minutes`-re (ez az ingyenes verzió minimuma, és tökéletesen elég).
    *   **Monitor Timeout**: Hagyhatod alapértelmezetten (30 sec).

3.  **Mentés**:
    *   Kattints a **"Create Monitor"** gombra.

### Eredmény:
*   Az UptimeRobot mostantól 5 percenként megnyitja az oldaladat.
*   Ez biztosítja, hogy a Python kód folyamatosan fusson a háttérben 0-24 órában (vagy amíg az UptimeRobot fut).
*   Így a reggel 7:00-kor esedékes ellenőrzések és üzenetküldések akkor is megtörténnek, ha te épp nem nézed az oldalt.

> [!NOTE]
> A kódban frissítettem az időzóna kezelést (`Europe/Budapest`), így a rendszer pontosan tudja, mikor van reggel 7 óra Magyarországon, téli/nyári időszámítástól függetlenül.

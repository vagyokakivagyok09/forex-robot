�# 🚀 GitHub Pages Deployment Útmutató

## Mivel a Git nincs telepítve a rendszeredre, íme a lépések a manuális feltöltéshez:

### 1. lépés: GitHub Repository létrehozása

1. Menj a [GitHub weboldalra](https://github.com) és jelentkezz be
2. Kattints a jobb felső sarokban a **+** ikonra → **New repository**
3. Add meg az alábbi adatokat:
   - **Repository name**: `fire-escape-room` (vagy bármilyen nevet választasz)
   - **Description**: "Interaktív szabadulószoba 5. osztályosoknak - Tűz és tűzbiztonság témakör"
   - **Public** (fontos, hogy publikus legyen a GitHub Pages-hez!)
   - ✅ Jelöld be: **Add a README file** - NE jelöld be (mivel már van README-nk)
4. Kattints a **Create repository** gombra

### 2. lépés: Fájlok feltöltése

1. Az új repository oldalon kattints az **uploading an existing file** linkre
2. Húzd be az alábbi fájlokat:
   - `index.html`
   - `style.css`
   - `script.js`
   - `README.md`
3. Vagy kattints a **choose your files** linkre és válaszd ki őket
4. Írd be a commit message-t: `Initial commit: Fire Escape Room webapp`
5. Kattints a **Commit changes** gombra

### 3. lépés: GitHub Pages aktiválása

1. A repository oldalon kattints a **Settings** fülre (fogaskerék ikon)
2. A bal oldali menüben görgess le a **Pages** opcióhoz
3. **Source** alatt válaszd ki: **Deploy from a branch**
4. **Branch** alatt válaszd ki:
   - Branch: `main` (vagy `master`)
   - Folder: `/ (root)`
5. Kattints a **Save** gombra
6. Várj 1-2 percet, amíg a deployment lefut
7. Frissítsd az oldalt - megjelenik egy zöld doboz a linkkel!

### 4. lépés: Megosztható link

A webapp elérhetősége:
```
https://<felhasználóneved>.github.io/fire-escape-room/
```

Például: `https://johndoe.github.io/fire-escape-room/`

---

## ⚡ Gyorsabb módszer: Git telepítése (opcionális)

Ha később szeretnél könnyebben frissíteni, telepítsd a Git-et:

1. Töltsd le: https://git-scm.com/download/win
2. Telepítsd (hagyd az alapértelmezett beállításokat)
3. Nyisd meg újra a PowerShell-t
4. Futtasd:

```powershell
cd "C:\Users\Tomi\Oktatás\fire-escape-room"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<felhasználóneved>/fire-escape-room.git
git push -u origin main
```

---

## 📱 Tesztelés után

Amikor a GitHub Pages link elkészült:
1. Nyisd meg mobilon is a linket
2. Teszteld az összes állomást
3. Oszd meg a gyerekekkel! 🎉

**Jó játékot! 🔥**
�*cascade082Afile:///C:/Users/Tomi/Oktat%C3%A1s/fire-escape-room/DEPLOYMENT.md
# Adaptív Oktatási Platform - Implementációs Terv

Egy online, AI-alapú személyre szabott tanulási rendszer, amely a Google Gemini modellt használja ügynök-alapú (Agentic AI) oktatásra. A platform az 5-6. évfolyamos természettudomány és 7-8. évfolyamos földrajz tantárgyakra fókuszál.

## User Review Required

> [!IMPORTANT]
> **API Kulcs Szükséges**: A projekt működéséhez Google Gemini API kulcsra lesz szükség. Ezt a [Google AI Studio](https://aistudio.google.com/apikey)-ban lehet ingyenesen létrehozni.

> [!WARNING]
> **Adatvédelem**: A tanulói profilok jelenleg a böngésző localStorage-ában tárolódnak. Éles környezetben backend adatbázis és GDPR-kompatibilis adatkezelés szükséges.

> [!CAUTION]
> **Prototípus Fázis**: Ez egy MVP (Minimum Viable Product) verzió lesz. A teljes Knowledge Graph, RAG integráció és KRÉTA csatlakozás későbbi iterációkban kerül implementálásra.

## Proposed Changes

### Frontend Architektúra

#### [NEW] [index.html](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/index.html)

A fő alkalmazás belépési pontja. Tartalmazza:
- Bejelentkezési/regisztrációs felületet
- Tantárgy választót (Természettudomány vs. Földrajz)
- Tanulói profil inicializálást
- API kulcs konfigurációs felületet

#### [NEW] [css/design-system.css](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/css/design-system.css)

Premium design rendszer:
- Modern CSS változók (HSL alapú színpaletta)
- Glassmorphism effektek
- Smooth animációk és átmenetek
- Responsive grid rendszer
- Dark mode támogatás

#### [NEW] [css/components.css](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/css/components.css)

Újrafelhasználható UI komponensek:
- Chat buborékok (diák vs. AI)
- Interaktív kártyák
- Progress bárok és teljesítmény indikátorok
- Modal dialógusok
- Tooltipek és segítő elemek

---

### Core JavaScript Modulok

#### [NEW] [js/config.js](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/js/config.js)

Globális konfiguráció:
- Gemini API endpoint beállítások
- Model paraméterek (temperature, top_p, max_tokens)
- Tantárgyi konstansok
- Debug módok

#### [NEW] [js/gemini-agent.js](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/js/gemini-agent.js)

Az Agentic AI mag implementációja:
- **Planning Module**: Tanítási stratégia tervezés (Szókratészi módszer, scaffolding, enrichment)
- **Tool Use**: Külső források hívása (szimuláció indítás, vizualizáció generálás)
- **Self-Correction**: Válaszok pedagógiai megfelelőségének ellenőrzése
- **Persistence**: Chat history és tanulói kontextus kezelése

Fő függvények:
```javascript
async function planLesson(topic, studentProfile)
async function generateResponse(userMessage, context)
async function assessUnderstanding(studentAnswer, correctAnswer)
async function adaptDifficulty(performanceMetrics)
```

#### [NEW] [js/knowledge-tracing.js](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/js/knowledge-tracing.js)

Tudás követés (Knowledge Tracing):
- Bayesian Knowledge Tracing egyszerűsített implementáció
- Fogalom-szintű tudás valószínűségek számítása
- Learning curve vizualizáció
- Misconception pattern detection

Adatstruktúra:
```javascript
{
  studentId: "unique_id",
  conceptMastery: {
    "halmazállapot": 0.75,
    "oldódás": 0.40,
    "forráspont": 0.90
  },
  interactionHistory: [...],
  learningStyle: "visual" | "auditory" | "kinesthetic"
}
```

---

### Természettudomány Modul (5-6. osztály)

#### [NEW] [subjects/science/knowledge-graph.js](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/subjects/science/knowledge-graph.js)

Tudásgráf definíció:
- Csomópontok: Anyagok, folyamatok, jelenségek (pl. "Víz", "Párolgás", "Kondenzáció")
- Élek: Hierarchikus és oksági kapcsolatok
- Előfeltételek: "Halmazállapot" → "Víz körforgása"

```javascript
const scienceKG = {
  nodes: [
    { id: 'halmazállapot', level: 1, prerequisites: [] },
    { id: 'oldódás', level: 2, prerequisites: ['halmazállapot'] },
    { id: 'víz_körforgása', level: 3, prerequisites: ['halmazállapot', 'párolgás'] }
  ],
  edges: [...]
}
```

#### [NEW] [subjects/science/simulations.js](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/subjects/science/simulations.js)

Interaktív szimulációk Canvas-szal:
- **Részecske-modell animáció**: Szilárd/folyékony/gáznemű halmazállapotok vizualizációja
- **Hőmérséklet szimulátor**: Felhasználó változtathatja a hőmérsékletet, és látja az anyag viselkedését
- **Oldódás szimuláció**: Vízmolekulák "szétszedik" a cukorkristályt

#### [NEW] [subjects/science/misconceptions.js](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/subjects/science/misconceptions.js)

Gyakori tévhitek adatbázisa pattern matching-gel:
```javascript
{
  pattern: /elolvad.*cukor.*víz/i,
  misconception: "oldódás_vs_olvadás",
  intervention: "socratic_contrast",
  correctConcept: "oldódás"
}
```

---

### Földrajz Modul (7-8. osztály)

#### [NEW] [subjects/geography/demographics.js](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/subjects/geography/demographics.js)

Demográfiai adatok és számítások:
- Korfa típusok (piramis, urna, harang)
- Népességi mutatók kalkulátor (természetes szaporodás, öregedési index)
- Szimulált KSH adatok magyar városokra

#### [NEW] [subjects/geography/population-pyramid.js](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/subjects/geography/population-pyramid.js)

Interaktív korfa vizualizáció:
- D3.js-szerű vizualizáció Vanilla JS-ben
- Dinamikus adatfrissítés
- Annotációk (háborús "lyukak", baby boom)
- Összehasonlító nézet (két ország/időszak egymás mellett)

#### [NEW] [subjects/geography/minister-game.js](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/subjects/geography/minister-game.js)

"Pénzügyminiszter" játék (gamification):
- Döntési fa alapú szimuláció
- AI által generált forgatókönyvek
- Következmények számítása (gazdaság, népszerűség)
- Eredmény vizualizáció (frissített korfa, GDP grafikon)

---

### Adaptív Motor

#### [NEW] [js/adaptive-engine.js](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/js/adaptive-engine.js)

A rendszer "agya", amely összeköti a komponenseket:

**ZPD Kalkulátor**: Meghatározza a diák aktuális Legközelebbi Fejlődési Zónáját
```javascript
function calculateZPD(conceptMastery, knowledgeGraph) {
  // Témák, amiket a diák 0.3-0.7 mastery között tud → ZPD
}
```

**Difficulty Adapter**: Valós időben állítja a feladat nehézségét
- Túl könnyű (3 egymás utáni helyes válasz) → Complexity++
- Túl nehéz (2 egymás utáni hiba) → Complexity--, Scaffolding beiktat

**Content Router**: Eldönti, mikor kell szimulációt, mikor szöveges magyarázatot, mikor Szókratészi kérdést használni

---

### Tanulói Interfész

#### [NEW] [pages/learning-session.html](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/pages/learning-session.html)

A fő tanulási felület:
- **Chat Panel**: AI-val való beszélgetés (balra)
- **Visualization Panel**: Szimulációk, grafikonok, 3D modellek (középen, nagy)
- **Progress Sidebar**: Aktuális témakör, elsajátított fogalmak, következő lépések (jobbra)

#### [NEW] [pages/dashboard.html](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/pages/dashboard.html)

Tanulói dashboard:
- Haladás vizualizáció (concept mastery radar chart)
- Tanulási idővonal (timeline)
- Erősségek / Fejlesztendő területek
- AI által generált személyes javaslatok

---

### Prompt Engineering

#### [NEW] [prompts/system-prompts.js](file:///C:/Users/Tomi/Természettudomány,földrajz%20önálló%20modell/prompts/system-prompts.js)

Tantárgy-specifikus rendszerüzenetek a Gemini számára:

**Természettudomány prompt**:
```
ROLE: Türelmes, lelkes természettudomány tutor 5-6. osztályosoknak
OBJECTIVE: Segítsd a diákot a [TOPIC] megértésében NAT 2020 szerint
CONSTRAINTS:
- SOHA ne add meg a választ közvetlenül
- Használj rávezető kérdéseket (Szókratészi módszer)
- Ha misconception-t észlelsz, kérj magyarázatot, majd adj ellenpéldát
- Használj mindennapi analógiákat
TONE: Barátságos, bátorító, kíváncsi
TOOLS: Hozzáférésed van szimulációkhoz és vizualizációhoz
```

**Földrajz prompt**:
```
ROLE: Geográfus mentor 7-8. osztályosoknak
OBJECTIVE: Fejleszd a diák térbeli és rendszerszemléletét a [TOPIC] témában
CONSTRAINTS:
- Kapcsolj össze természeti és társadalmi folyamatokot
- Használj valós, aktuális példákat (magyar városok, KSH adatok)
- Ösztönözd a kritikai gondolkodást ok-okozati kapcsolatokkal
TONE: Szakértő, de közérthető
TOOLS: Korfák, térképek, statisztikai adatok
```

---

## Verification Plan

### Automated Tests

Mivel ez frontend-heavy alkalmazás, az alábbi automatizált teszteket fogjuk végezni:

```bash
# Gemini API kapcsolat tesztelése
node tests/test-gemini-connection.js

# Knowledge Tracing logika tesztelése
node tests/test-knowledge-tracing.js

# Adaptive Engine edge cases
node tests/test-adaptive-engine.js
```

### Manual Verification

#### Természettudomány Modul Tesztelése

1. **Helyes válasz sorozat** (gifted learner szimuláció):
   - Diák 3x egymás után helyesen válaszol az oldódásról
   - Elvárás: AI automatikusan emeli a nehézséget, bevezeti a nyomás hatását

2. **Misconception detektálás**:
   - Diák azt írja: "A cukor elolvad a teában"
   - Elvárás: AI Szókratészi kérdéssel (vaj példa) rávezet az oldódásra

3. **Szimuláció használat**:
   - Részecske-modell animáció elindul
   - Diák változtatja a hőmérsékletet
   - Elvárás: Smooth animáció, AI magyarázza a változásokat

#### Földrajz Modul Tesztelése

1. **Személyes relevancia**:
   - Diák megadja a városát (pl. Debrecen)
   - Elvárás: AI generál Debrecenre specifikus korfát és elemzi

2. **Minister Game**:
   - Diák választ egy demográfiai politikát
   - Elvárás: AI kiszámolja a következményeket 10 év távlatában, frissíti a korfát

3. **Vizuális támogatás**:
   - Diák nem érti a korfa férfi/nő oldalát
   - Elvárás: AI színkódolással és nyilakkal segít

### Browser Testing

- Chrome (latest)
- Firefox (latest)  
- Edge (latest)
- Mobile responsive (tablet/phone)

### Accessibility

- Keyboard navigation
- Screen reader kompatibilitás (ARIA labels)
- Színkontraszrt ellenőrzés (WCAG AA)

---

## Implementációs Fázisok

### Fázis 1: MVP Core (1-2 nap)
- Alapvető HTML/CSS struktúra
- Gemini API integráció
- Egyszerű chat interface
- LocalStorage alapú profil

### Fázis 2: Természettudomány Modul (1 nap)
- Knowledge Graph implementálás
- 1-2 interaktív szimuláció
- Misconception detection

### Fázis 3: Földrajz Modul (1 nap)
- Korfa vizualizáció
- Minister Game
- Demográfiai adatok

### Fázis 4: Adaptív Motor (1 nap)
- ZPD kalkulátor
- Difficulty adapter
- Knowledge Tracing finomhangolás

### Fázis 5: Polish & Deploy (0.5 nap)
- UI/UX finomítás
- Teljesítmény optimalizálás
- Dokumentáció

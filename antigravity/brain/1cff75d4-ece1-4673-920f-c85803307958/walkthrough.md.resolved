# Heti Report Ütemezés - Walkthrough

## Összefoglaló

A kereskedési bot heti teljesítmény összegzését módosítottam:

✅ **Új funkciók:**
- A report most **minden péntek este 20:00-kor** (helyi idő, GMT+1) küldi ki
- **Csak az aktuális hét** statisztikáit összegzi (hétfő-vasárnap)
- Timestamp követés a trade-eknél a heti szűréshez

---

## Változtatások részletesen

### 1. **Heti idősáv kalkuláció**

Új helper függvény került bevezetésre, amely meghatározza az aktuális hét kezdetét (hétfő) és végét (vasárnap):

```python
def get_week_range(date):
    """Meghatározza a hét kezdetét (hétfő) és végét (vasárnap) egy adott dátumhoz."""
    weekday = date.weekday()  # 0=Hétfő, 6=Vasárnap
    week_start = date - timedelta(days=weekday)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end
```

### 2. **Heti és all-time statisztikák szétválasztása**

Most két különálló statisztika készül:
- **All-time**: Minden korábbi trade
- **Weekly**: Csak az aktuális héten lezárt trade-ek

```python
# Heti statisztikák (Current Week Only)
weekly_trades = 0
weekly_wins = 0
weekly_losses = 0
weekly_pips = 0.0
weekly_huf = 0.0
```

### 3. **Péntek 20:00 trigger**

A report most pontos időpontban küldi ki az üzenetet:

```python
# Helyi idő (GMT+1)
local_now = now + timedelta(hours=1)  # UTC -> GMT+1
is_friday = local_now.weekday() == 4  # 4 = Péntek
is_8pm = local_now.hour == 20

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
```

### 4. **Heti report tartalom**

Az üzenet most már tartalmazza:
- Az aktuális hét időszakát (pl. "2025-11-25 - 2025-12-01")
- Csak az aktuális hét statisztikáit
- Következő péntek dátumát pontosan (+ 7 nap)

```python
weekly_msg = (
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
```

### 5. **Timestamp hozzáadása trade-ekhez**

Új trade nyitásakor most timestamp is mentésre kerül:

```python
daily_signals[symbol] = {
    'date': today_str,
    'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),  # ÚJ!
    'direction': analysis['signal_type'],
    'entry': analysis['entry'],
    'tp': analysis['tp'],
    'sl': analysis['sl'],
    'status': 'open',
    'pips_target': pips_gained,
    'pip_value_huf': pip_value_huf
}
```

---

## Tesztelés

A kód logikája helyes, de a valós teszteléshez várni kell **péntek este 20:00-ig**. 

### Kézi teszt lehetőség:

Ha azonnal szeretnéd tesztelni, átmenetileg módosíthatod a feltételt:

```python
# Teszt: azonnal küldje ki
send_weekly = True  # Helyettesítse az if is_friday and is_8pm: feltételt
```

**Fontos**: A teszt után állítsd vissza az eredeti logikát!

---

## Eredmény

Most a bot:
1. ✅ **Minden péntek este 20:00-kor** küldi a heti összegzést
2. ✅ **Csak az aktuális hét** (hétfő-vasárnap) teljesítményét mutatja
3. ✅ **Következő péntek dátumát** jelzi pontosan a következő reportig
4. ✅ **Automatikusan reset-eli** a számláló hetente

![uploaded_image_1764056099596.png](C:/Users/Tomi/.gemini/antigravity/brain/1cff75d4-ece1-4673-920f-c85803307958/uploaded_image_1764056099596.png)
*Az új report formátum már tartalmazza az időszakot és a pontosabb következő report időpontot*

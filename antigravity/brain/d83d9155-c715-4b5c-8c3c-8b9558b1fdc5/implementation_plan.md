# Implementation Plan - Czech Table Tennis Betting Analyzer

## Goal Description
Convert the existing generic "BetSmart" prototype into a specialized analyzer for Czech Table Tennis (Liga Pro). The core feature is a "Statistical Dominance" search engine that calculates winning probabilities based on a custom algorithm (Rating, H2H, Daily Form) and highlights trends.

## User Review Required
> [!IMPORTANT]
> **Data Source Strategy**: Direct scraping of `tt.league-pro.com` from a browser-based app is likely to be blocked by CORS. I will implement a **Mock Data Generator** that creates realistic Czech Table Tennis scenarios (players, ratings, H2H history) to demonstrate the algorithm immediately. I will also keep the "Paste HTML Source" feature as a fallback for real data analysis.

## Proposed Changes

### Logic Layer
#### [MODIFY] [calculators.js](file:///c:/Users/Tomi/PRóba/js/calculators.js)
- Implement the specific "Matek" algorithm:
    - Base: 50-50%
    - Rating diff: +1% per 10 points
    - H2H: +10-15% for 7/10 wins (Dominance)
    - Daily Form: Bonus for wins, penalty for losses
- Add `calculateDominanceScore` function.

#### [MODIFY] [data_fetcher.js](file:///c:/Users/Tomi/PRóba/js/data_fetcher.js)
- Remove "EsportsBattle" specific logic.
- Add `generateMockData()` to create realistic Table Tennis match data (Players like "Novak", "Kolar", etc.).
- Update `parseHTML` to be more generic or targeted towards standard table structures found on sports sites.

### UI Layer
#### [MODIFY] [index.html](file:///c:/Users/Tomi/PRóba/index.html)
- Update title and branding to "TT.League Analyzer".
- Redesign Dashboard to show:
    - Match List
    - Calculated Probability (e.g., "Novak: 78%")
    - Visual indicators for "Mumus" effect and "Flow" state.
- Remove irrelevant sections (like generic "Odds Converter" if it's not the main focus, though it can stay as a utility).

#### [MODIFY] [app.js](file:///c:/Users/Tomi/PRóba/js/app.js)
- Wire up the new `calculators.js` logic to the dashboard.
- Initialize with Mock Data by default for immediate visualization.

#### [MODIFY] [style.css](file:///c:/Users/Tomi/PRóba/css/style.css)
- Ensure "Premium" look (Dark mode, neon accents) as requested.

## Verification Plan

### Automated Tests
- None (No test framework installed).

### Manual Verification
1.  **Algorithm Check**:
    - Open the app.
    - Verify that a player with higher rating + good H2H + won daily matches has a high % (e.g., >70%).
    - Verify that a "Mumus" scenario (lower rating but high H2H wins) correctly reflects a higher chance than rating alone would suggest.
2.  **UI Check**:
    - Verify the dashboard lists matches.
    - Check if "Flow" state (winning streak) is visually distinct (e.g., green icon).
    - Check if "Mumus" warning appears where applicable.

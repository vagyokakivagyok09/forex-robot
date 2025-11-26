# Tippmix.hu Integration Plan

## Goal Description
Integrate live match data and odds from `tippmix.hu` into the existing Table Tennis Analyzer app. This will allow users to see real-time odds alongside the statistical analysis.

## User Review Required
> [!IMPORTANT]
> **Architecture Change**: To bypass CORS and access Tippmix data reliably, I will create a small **Local Proxy Server** (`proxy.js`) using Node.js and Puppeteer. You will need to run this server locally (`node proxy.js`). This server will scrape the data from Tippmix and serve it to the web app.

## Proposed Changes

### Backend (Local Proxy)
#### [NEW] [proxy.js](file:///c:/Users/Tomi/PRóba/proxy.js)
- Express server running on port 3000.
- Endpoint `/api/matches` that:
    - Launches a headless browser (Puppeteer).
    - Navigates to `tippmix.hu/sport/asztalitenisz`.
    - Scrapes match data (Time, Players, Odds).
    - Returns JSON.

### Data Layer
#### [MODIFY] [data_fetcher.js](file:///c:/Users/Tomi/PRóba/js/data_fetcher.js)
- Replace mock data with `fetch('http://localhost:3000/api/matches')`.
- Add error handling (if proxy is not running, show warning).


### UI Layer
#### [MODIFY] [ui.js](file:///c:/Users/Tomi/PRóba/js/ui.js)
- Update dashboard to show a list of live/upcoming matches from Tippmix.
- Add "Odds" column to the match display.

## Verification Plan
### Manual Verification
- Check if matches load in the console/UI.
- Verify odds match the website.

# Implementation Plan - Crypto/Forex Pattern Matching App

## Goal Description
Build a Streamlit web application that allows users to select a symbol (default BTC-USD), downloads historical data, finds the most similar historical price pattern to the last 30 days, and projects future movement based on that historical match. The UI will be in Hungarian.

## User Review Required
> [!NOTE]
> The application requires `streamlit`, `yfinance`, `plotly`, and `numpy` to be installed. I will assume these are available or the user will install them.

## Proposed Changes

### Root Directory
#### [NEW] [app.py](file:///C:/Users/Tomi/.gemini/app.py)
- **Imports**: `streamlit`, `yfinance`, `plotly.graph_objects`, `numpy`.
- **UI Layout**:
    - Title: "Kripto/Forex Mintaillesztő Motor" (Crypto/Forex Pattern Matching Engine).
    - Sidebar: Input for Symbol (Dropdown: BTC-USD, ETH-USD, etc.), Date range selection (optional, or just max).
- **Logic**:
    - `download_data(ticker)`: Fetches data using `yfinance`.
    - `find_pattern(data, window_size=30)`:
        - Extract last `window_size` closing prices.
        - Normalize (e.g., % change from start of window).
        - Iterate through history to find the window with lowest Euclidean distance to the current pattern.
    - `plot_results(data, best_match_index, window_size)`:
        - Plot current price.
        - Overlay the "projected" path (price movement following the best match) scaled to current price.
- **Language**: All labels and text in Hungarian.

## Verification Plan
### Automated Tests
- None planned for this script-based task.
### Manual Verification
- User will run `streamlit run app.py`.
- Verify the chart loads and shows a projection.

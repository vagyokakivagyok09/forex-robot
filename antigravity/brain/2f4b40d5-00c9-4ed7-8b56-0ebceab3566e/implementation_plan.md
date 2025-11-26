# Signal Visibility Implementation Plan

## Goal
Ensure the chart remains visible after a signal is sent, and permanently display the trading plan (projection) for the direction that was alerted, regardless of subsequent price movements.

## Proposed Changes
### Core Logic (`app.py`)
#### [MODIFY] [app.py](file:///c:/Users/Tomi/.gemini/app.py)
- **Session State**:
    - Update `daily_signals` to store `{'date': ..., 'direction': ...}`.
- **`analyze_pair`**:
    - If locked, return `status="LOCKED"`, but ALSO return all data needed for rendering (don't return early with just status).
    - When alerting, save `direction` to session state.
- **`render_view`**:
    - Remove the early return for "LOCKED".
    - Add `st.info` banner if locked, showing the sent direction.
    - **Visualization Logic**:
        - Check if `ticker` is in `daily_signals` for today.
        - If YES: Set `visual_direction = saved_direction`.
        - If NO: Set `visual_direction = current_trend_direction`.
        - Draw projection based on `visual_direction`.

## Verification Plan
### Manual Verification
- Wait for a signal (or simulate one by modifying state).
- Verify chart is still visible.
- Verify the projection line matches the sent signal (e.g., Green for Long), even if price moves against it later.

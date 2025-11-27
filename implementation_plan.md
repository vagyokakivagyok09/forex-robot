# Fix Missing Charts in London Breakout Dashboard

## Goal Description
The charts in the dashboard are not appearing for each symbol. The headers appear, but the charts are missing or only appearing at the bottom. This is caused by an indentation error in `app.py` where the chart rendering logic is placed outside the loop that iterates over the symbols. The goal is to move the chart rendering logic inside the loop so that a chart is generated for each symbol immediately after its header.

## User Review Required
> [!IMPORTANT]
> This change modifies the indentation of a large block of code in `app.py`. While the logic remains the same, the execution flow is significantly corrected.

## Proposed Changes

### Dashboard Logic
#### [MODIFY] [app.py](file:///c:/Users/Tomi/.gemini/app.py)
- Indent lines 1009-1124 (approximate range) to be inside the `for symbol in TARGET_PAIRS:` loop.
- Ensure `st.plotly_chart` is called for each symbol.

## Verification Plan

### Automated Tests
- None available for Streamlit UI layout.

### Manual Verification
- Run the Streamlit app.
- Verify that for each symbol (GBPUSD, GBPJPY, EURUSD), a header is displayed followed immediately by its corresponding chart.
- Verify that 3 charts are visible in total (one for each symbol).

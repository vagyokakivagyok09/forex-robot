# Walkthrough - Smart Y-Axis Scaling

I have updated the app to improve the chart visibility by fixing the Y-axis scaling.

## Changes

### `app.py`

#### [MODIFY] [app.py](file:///c:/Users/Tomi/.gemini/app.py)
-   Implemented "Smart Y-Axis Scaling" logic:
    -   Calculates `y_min` and `y_max` from the visible data (last ~60 candles).
    -   Expands the range to include the projection path if it exists.
    -   Adds 10% padding to the top and bottom.
-   Updated `fig.update_layout`:
    -   Replaced `autorange=True` with `range=[y_min, y_max]`.

## Verification Results

### Manual Verification
-   **Candle Size**: The candles should now appear large and detailed, occupying most of the vertical space.
-   **Visibility**: The chart should focus on the recent price action and the projection, rather than showing the entire history's price range.
-   **Padding**: There should be a small amount of empty space above the highest high and below the lowest low to prevent cutting off the chart.

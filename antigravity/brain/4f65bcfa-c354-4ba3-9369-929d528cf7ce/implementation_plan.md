# Implementation Plan - Main Menu (Hub) Structure

## Goal
Transform the linear game flow into a Hub-based structure where users access stations from a "Main Menu" and return to it after completing tasks.

## Proposed Changes

### HTML (`index.html`)
- [NEW] Add a `<section id="main-menu" class="screen">` after the intro screen.
- The menu will contain a grid of 6 items:
    - Station 1 Card
    - Station 2 Card
    - Station 3 Card
    - Station 4 Card
    - Station 5 Card
    - Final Gate Card
- Add "Vissza a menübe" (Back to Menu) button to each station (top left or bottom) for better UX (optional, but good practice).

### CSS (`style.css`)
- Style `.mission-grid`: Responsive grid layout.
- Style `.mission-card`:
    - Default (Locked): Greyed out, lock icon.
    - Active: Colored, clickable, hover effects.
    - Completed: Green border, checkmark icon.
- Animations for unlocking new stations.

### JavaScript (`script.js`)
- Update `startGame()`: Navigate to `main-menu` instead of `station-1`.
- Create `updateMainMenu()`:
    - Check `gameState.unlockedDigits`.
    - Unlock Station 1 (Always).
    - Unlock Station N if Station N-1 is complete (Sequential Logic to preserve story flow).
    - Unlock Final Gate if Station 5 is complete.
    - Update visual state of cards (add/remove classes `locked`, `active`, `completed`).
- Update `checkStationX()` functions:
    - On success: `unlockDigit(...)` -> `showFeedback(...)` -> `setTimeout(() => showScreen('main-menu'), 2000)`.
- Add event listeners for the new menu cards.

## Verification
- Start game -> See Menu.
- Click Station 1 -> Solve -> Return to Menu -> Station 1 marked done, Station 2 unlocked.
- Verify all 5 stations and Final Gate access.

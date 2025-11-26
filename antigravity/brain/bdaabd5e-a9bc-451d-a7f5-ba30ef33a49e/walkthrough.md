# Kisalföld Educational App - Walkthrough

## Overview
We have created an interactive educational web application for 7th-grade students about the Kisalföld region.

## Features
1.  **Lesson Summary**: Key facts about location, formation, and parts.
2.  **Blind Map Task**: Drag-and-drop game to identify regions on a map.
3.  **Quiz**: True/False and Multiple Choice questions.
4.  **Logic Problem**: A text-based scenario to solve.

## How to Run
1.  Navigate to the `kisalfold_project` folder.
2.  Open `index.html` in any modern web browser.

## Verification
### Map Task
- **Test**: Drag "Szigetköz" to the area between the Danube and Mosoni-Danube.
- **Expected Result**: The label should snap into place and turn green.
- **Test**: Drag a label to the wrong spot.
- **Expected Result**: The drop zone should flash red.

### Quiz
- **Test**: Answer the questions.
- **Expected Result**: Immediate feedback (Green checkmark or Red X) is provided.

### Logic Problem
- **Test**: Enter "Szigetköz és Csallóköz" or similar variations.
- **Expected Result**: The system recognizes keywords and provides specific feedback.

## Files
- `index.html`: Main structure.
- `style.css`: Premium styling.
- `script.js`: Game logic.
- `assets/kisalfold_blind_map.png`: Generated blind map.

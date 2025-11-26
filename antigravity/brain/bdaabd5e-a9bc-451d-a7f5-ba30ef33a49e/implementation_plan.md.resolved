# Implementation Plan - Kisalföld Educational App

## Goal
Create an interactive educational web page for 7th-grade students about "Kisalföld" (Little Hungarian Plain). The app will include a lesson summary, a quiz (True/False, Multiple Choice), a logic problem, and an interactive "blind map" task.

## User Review Required
- **Content Accuracy**: Please review the generated questions and logic problem for accuracy and difficulty level.
- **Map Quality**: The "blind map" will be generated AI. If the text removal is not perfect, we may need to adjust the strategy (e.g., covering labels with CSS blocks).

## Proposed Changes

### Directory Structure
`kisalfold_project/`
- `index.html`: Main entry point.
- `style.css`: Styling (Colorful, engaging, responsive).
- `script.js`: Application logic.
- `assets/`: Stores the processed map image.

### Content
**1. True/False Questions (5)**
- Based on the provided text (Location, Formation, Parts).

**2. Quiz Questions (5)**
- Multiple choice or short answer questions covering key facts.

**3. Logic Problem (1)**
- A text-based travel scenario requiring knowledge of the relative positions of the regions.

### Interactive Map
- **Image**: Processed version of the uploaded map with labels removed.
- **Interaction**: Drag-and-drop labels onto the correct regions on the map.
- **Implementation**:
    - Display the blind map.
    - Create draggable elements for: "Szigetköz", "Csallóköz", "Győri-medence", "Fertő-Hanság-medence", "Rábaköz", "Marcal-medence".
    - Define drop zones (using absolute positioning percentages) on the map image.

## Verification Plan
### Automated Tests
- None (Static site).

### Manual Verification
- Open `index.html` in the browser.
- Test all quiz questions for correct/incorrect feedback.
- Test the logic problem.
- Test the map drag-and-drop functionality (ensure labels snap to zones or validate correctly).

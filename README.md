# Chess Tracker

A computer vision–powered chess move tracker that detects moves from a physical chessboard and integrates with the Stockfish engine for analysis and AI play.

---

## Features
- Camera calibration: Interactive tool (`calibrate_manual_oriented.py`) to map board corners and save square coordinates (`sqdict.json`).
- Move detection: Uses OpenCV frame differencing and contour analysis to identify piece movement.
- Board orientation support: Handles multiple camera angles (TOP, BOTTOM, SIDE_L, SIDE_R).
- Stockfish integration: Plays against the computer with adjustable time limits.
- Visual overlays: Displays board state with highlighted moves using CairoSVG + Python‑Chess.
- Undo controls: Roll back one or two moves easily.
- Debug mode: Toggle detailed frame analysis.

---

## Project Structure
- `cv_chess_play.py` → Main tracker loop (camera + Stockfish integration)  
- `calibrate_manual_oriented.py` → Calibration tool to generate `sqdict.json`  
- `sqdict.json` → Saved board square coordinates  
- `stockfish-windows-x86-64-avx2.exe` → Chess engine binary  
- `requirements.txt` → Dependencies  

---

## Quick Controls
- `r` → Log a move (press twice)  
- `u` → Undo last move  
- `U` → Undo last two moves  
- `d` → Toggle debug mode  
- `q` → Quit  

---

## Getting Started
1. Clone the repo: 
   ```bash
   git clone https://github.com/yourusername/chess-tracker.git

   cd chess-tracker
  # Step 2: Install libraries
pip install -r requirements.txt

# Step 3: Install GTK+ for Windows Runtime Environment

# Download and install from:
# https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

# Step 4: Download Stockfish
# Get the latest Stockfish engine from:
# https://stockfishchess.org
# Place the downloaded executable (stockfish-windows-x86-64-avx2.exe) in the project folder

# Step 5: Run Python Scripts

# First calibrate the board
python calibrate_manual_oriented.py --rotate 270

# Then start the tracker
python cv_chess_play.py




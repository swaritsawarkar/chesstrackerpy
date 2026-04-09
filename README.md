# Chess Tracker

A computer vision–powered chess move tracker that detects moves from a physical chessboard and integrates with the Stockfish engine for analysis and AI play.

---

## Features
- **Camera calibration:** Interactive tool (`calibrate_manual_oriented.py`) to map board corners and save square coordinates (`sqdict.json`).
- **Move detection:** Uses OpenCV frame averaging, Gaussian blur, and contour analysis to identify piece movement reliably under varied lighting conditions.
- **Board orientation support:** Handles multiple camera angles (TOP, BOTTOM, SIDE_L, SIDE_R).
- **Game modes:** Choose at startup between playing against Stockfish or recording a 2 player game.
- **Stockfish integration:** Plays against the computer with adjustable time limits.
- **AI post-game analysis:** After every game, Stockfish evaluates every move and Llama3 via the Groq API explains in plain English what you did well, what your biggest mistakes were, and how they affected the game.
- **PGN export:** Every game is automatically saved as a `.pgn` file so you can replay it on chess.com or lichess.
- **Visual overlays:** Displays board state with highlighted moves using CairoSVG + Python-Chess.
- **Undo controls:** Roll back one or two moves easily.
- **Debug mode:** Toggle detailed frame analysis.

---

## Project Structure

| File | Description |
|------|-------------|
| `cv_chess_play.py` | Main tracker loop (camera + Stockfish + Groq integration) |
| `calibrate_manual_oriented.py` | Calibration tool to generate `sqdict.json` |
| `sqdict.json` | Saved board square coordinates |
| `stockfish-windows-x86-64-avx2.exe` | Chess engine binary (download separately) |
| `requirements.txt` | Dependencies |

---

## Quick Controls

| Key | Action |
|-----|--------|
| `r` (before move) | Take a snapshot of the board before touching a piece |
| `r` (after move) | Take a snapshot after placing the piece — detects the move |
| `u` | Undo last move |
| `U` | Undo last two moves |
| `d` | Toggle debug mode on/off |
| `q` | Quit the app |

---

## Getting Started

### Step 1: Clone the repo
```bash
git clone https://github.com/yourusername/chess-tracker.git
cd chess-tracker
```

### Step 2: Install libraries
```bash
pip install -r requirements.txt
```

### Step 3: Install GTK+ for Windows Runtime Environment
Download and install from:
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

### Step 4: Download Stockfish
Get the latest Stockfish engine from: https://stockfishchess.org
Place the downloaded executable (`stockfish-windows-x86-64-avx2.exe`) in the project folder.

### Step 5: Set up your Groq API key
Get a free API key from https://groq.com and paste it into the `GROQ_API_KEY` field in the config section of `cv_chess_play.py`:
```python
GROQ_API_KEY = "your-api-key-here"
```

### Step 6: Create the savegames folder
Create an empty folder called `savegames` in the project directory. The app will use this to store game saves.

### Step 7: Run Python scripts
```bash
# First calibrate the board
python calibrate_manual_oriented.py --rotate 270

# Then start the tracker
python cv_chess_play.py
```

### Step 8: Select your mode
When the app starts it will ask you to select a mode:
```
Select mode:
1 - Play vs Stockfish
2 - Record a game (2 players)
Enter 1 or 2:
```

---

## Tech Stack
- **Python** — OpenCV, NumPy, PIL, CairoSVG
- **Python-Chess** — board logic and move validation
- **Stockfish** — AI chess engine
- **Groq API + Llama3** — post-game analysis in plain English

---

## License

Free use

---

## Acknowledgments
- [Stockfish](https://stockfishchess.org) — world-class open-source chess engine
- [Python-Chess](https://python-chess.readthedocs.io) — chess logic and board utilities
- [OpenCV](https://opencv.org) — computer vision tools
- [Groq](https://groq.com) — fast inference API for Llama3

---

## Future Improvements
- [x] Add AI suggestions after each game to help players improve
- [x] Export completed games to PGN format
- [x] Improve robustness of move detection under varied lighting conditions
- [ ] Build a lightweight web interface for demo purposes

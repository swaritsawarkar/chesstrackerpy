# Chess Tracker

A computer vision–powered chess move tracker that detects moves from a physical chessboard and integrates with the Stockfish engine for analysis and AI play.

---

## Features
- **Camera calibration:** Interactive tool (`calibrate_manual_oriented.py`) to map board corners and save square coordinates (`sqdict.json`).
- **Move detection:** Uses OpenCV frame differencing and contour analysis to identify piece movement.
- **Board orientation support:** Handles multiple camera angles (TOP, BOTTOM, SIDE_L, SIDE_R).
- **Stockfish integration:** Plays against the computer with adjustable time limits.
- **Visual overlays:** Displays board state with highlighted moves using CairoSVG + Python-Chess.
- **Undo controls:** Roll back one or two moves easily.
- **Debug mode:** Toggle detailed frame analysis.

---

## Project Structure

| File | Description |
|------|-------------|
| `cv_chess_play.py` | Main tracker loop (camera + Stockfish integration) |
| `calibrate_manual_oriented.py` | Calibration tool to generate `sqdict.json` |
| `sqdict.json` | Saved board square coordinates |
| `stockfish-windows-x86-64-avx2.exe` | Chess engine binary (download separately) |
| `requirements.txt` | Dependencies |

---

## Quick Controls

| Key | Action |
|-----|--------|
| `r` | Log a move (press twice) |
| `u` | Undo last move |
| `U` | Undo last two moves |
| `d` | Toggle debug mode |
| `q` | Quit |

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

### Step 5: Run Python scripts
```bash
# First calibrate the board
python calibrate_manual_oriented.py --rotate 270

# Then start the tracker
python cv_chess_play.py
```

---

## Demo

[![Demo Screenshot](docs/demo-image.png)](https://your-video-link.com)

> Replace `docs/demo-image.png` with your screenshot path and `https://your-video-link.com` with your actual video link.

---

## Tech Stack
- **Python** — OpenCV, NumPy, PIL, CairoSVG
- **Python-Chess** — board logic and move validation
- **Stockfish** — AI chess engine

---

## License

This project is released under the MIT License. Feel free to use, modify, and share.

---

## Acknowledgments
- [Stockfish](https://stockfishchess.org) — world-class open-source chess engine
- [Python-Chess](https://python-chess.readthedocs.io) — chess logic and board utilities
- [OpenCV](https://opencv.org) — computer vision tools

---

## Future Improvements
- Add AI suggestions after each game to help players improve.
- Export completed games to PGN format.
- Build a lightweight web interface for demo purposes.
- Improve robustness of move detection under varied lighting conditions.

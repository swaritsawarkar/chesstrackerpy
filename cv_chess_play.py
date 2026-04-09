from groq import Groq
import cv2
import json
import numpy as np
import chess
import chess.engine
import chess.svg
import chess.pgn
from PIL import Image
import io
import random
import os
import sys
import cairosvg
import time

# === config ===
CALIB_JSON = "sqdict.json"
ENGINE_PATH = r"stockfish-windows-x86-64-avx2.exe"
MOVE_THRESHOLD = 25
MIN_CONTOUR_AREA = 250
CAM_INDEX = 0
BOARD_ORIENTATION = "TOP"  # "TOP", "BOTTOM", "SIDE_L", "SIDE_R"
GROQ_API_KEY = "your-api-key-here"

DEBUG_MODE = False  # Hit 'd' to flip debug ON/OFF

# === MODE SELECT ===
print("Select mode:")
print("1 - Play vs Stockfish")
print("2 - Record a game (2 players)")
mode = input("Enter 1 or 2: ").strip()
while mode not in ["1", "2"]:
    print("[WARN] Invalid choice, enter 1 or 2.")
    mode = input("Enter 1 or 2: ").strip()
mode = int(mode)
print(f"[INFO] Mode {mode} selected.")

# === ENGINE ===
if not os.path.exists(ENGINE_PATH):
    print(f"[OOPS] Can't find the chess engine at {ENGINE_PATH}")
    sys.exit(1)

engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
print(f"[INFO] Stockfish fired up from {ENGINE_PATH}")

# === LOAD JSON ===
if not os.path.exists(CALIB_JSON):
    print(f"[OOPS] Calibration file missing: {CALIB_JSON}")
    engine.quit()
    sys.exit(1)

with open(CALIB_JSON, "r") as f:
    sq_points = json.load(f)
print(f"[INFO] Pulled in {len(sq_points)} squares from {CALIB_JSON}")

# === ORIENTATION ===
files = 'abcdefgh'
ranks = '12345678'

def remap_square(square_name: str) -> str:
    f = square_name[0]
    r = square_name[1]
    fi = files.index(f)
    ri = ranks.index(r)
    if BOARD_ORIENTATION == "TOP":
        return square_name
    elif BOARD_ORIENTATION == "BOTTOM":
        return f"{files[7 - fi]}{ranks[7 - ri]}"
    elif BOARD_ORIENTATION == "SIDE_L":
        return f"{files[ri]}{ranks[7 - fi]}"
    elif BOARD_ORIENTATION == "SIDE_R":
        return f"{files[7 - ri]}{ranks[fi]}"
    else:
        return square_name

# === HELPERS ===
def poly_center(pts):
    a = np.array(pts, np.int32)
    M = cv2.moments(a)
    if M["m00"] == 0:
        return int(a[:, 0].mean()), int(a[:, 1].mean())
    return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])

def find_square(x, y):
    pt = (float(x), float(y))
    for sq, pts in sq_points.items():
        poly = np.array(pts, np.int32)
        if cv2.pointPolygonTest(poly, pt, False) >= 0:
            return sq
    return None

def overlay_poly(frame, poly_pts, color, alpha=0.45):
    overlay = frame.copy()
    pts = np.array(poly_pts, np.int32)
    cv2.fillPoly(overlay, [pts], color)
    return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

def draw_board_labels(base_frame):
    overlay = base_frame.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    for sq, pts in sq_points.items():
        p = np.array(pts, np.int32)
        cv2.polylines(overlay, [p], True, (255, 255, 255), 1)
        if sq == "a1":
            cx, cy = poly_center(pts)
            mapped = remap_square(sq)
            cv2.putText(overlay, mapped, (cx - 12, cy + 5), font, 0.45, (0, 255, 255), 1, cv2.LINE_AA)
    return overlay

def show_board(board, last_move=None):
    svg = chess.svg.board(board=board, lastmove=last_move, coordinates=True, size=450)
    png_data = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
    img = Image.open(io.BytesIO(png_data))
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    cv2.imshow("Board State", img_cv)
    cv2.waitKey(1)

def capture_stable_frame(cap, samples=5):
    frames = []
    for _ in range(samples):
        ret, f = cap.read()
        if ret:
            frames.append(f.astype(np.float32))
    if not frames:
        return None
    avg = np.mean(frames, axis=0).astype(np.uint8)
    return avg

def get_changed_squares(frame_before, frame_after):
    gray_before = cv2.cvtColor(frame_before, cv2.COLOR_BGR2GRAY)
    gray_after = cv2.cvtColor(frame_after, cv2.COLOR_BGR2GRAY)
    blur_before = cv2.GaussianBlur(gray_before, (5, 5), 0)
    blur_after = cv2.GaussianBlur(gray_after, (5, 5), 0)
    diff = cv2.absdiff(blur_before, blur_after)
    _, thresh = cv2.threshold(diff, MOVE_THRESHOLD, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    changed_squares = set()
    for cnt in contours:
        if cv2.contourArea(cnt) < MIN_CONTOUR_AREA:
            continue
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        sq = find_square(cx, cy)
        if sq:
            changed_squares.add(sq)
    return changed_squares

def analyze_game(move_history):
    print("\n[INFO] Analyzing your game, please wait...")

    client = Groq(api_key=GROQ_API_KEY)

    analysis_board = chess.Board()
    move_analysis = []

    for i, move in enumerate(move_history):
        info_before = engine.analyse(analysis_board, chess.engine.Limit(depth=15))
        score_before = info_before["score"].relative.score(mate_score=10000)
        best_move = info_before.get("pv", [None])[0]

        analysis_board.push(move)

        info_after = engine.analyse(analysis_board, chess.engine.Limit(depth=15))
        score_after = info_after["score"].relative.score(mate_score=10000)

        if score_before is not None and score_after is not None:
            delta = score_after - score_before
        else:
            delta = 0

        move_analysis.append({
            "move_number": i + 1,
            "played": move.uci(),
            "best": best_move.uci() if best_move else "unknown",
            "score_before": score_before,
            "score_after": score_after,
            "delta": delta
        })

    summary = "Here is a chess game move by move analysis from Stockfish:\n\n"
    for m in move_analysis:
        summary += f"Move {m['move_number']}: played {m['played']}, "
        summary += f"Stockfish best was {m['best']}, "
        summary += f"score before: {m['score_before']}, score after: {m['score_after']}, "
        summary += f"centipawn change: {m['delta']}\n"
    summary += "\nPlease explain in plain English what the player did well, what their biggest mistakes were, what they couldve done differently, and how those mistakes affected the game. Be specific per move where relevant."

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": summary}
        ],
        model="llama3-8b-8192",
    )

    print("\n===== GAME ANALYSIS =====")
    print(chat_completion.choices[0].message.content)
    print("=========================\n")

def save_pgn(move_history, mode):
    game = chess.pgn.Game()
    node = game
    for move in move_history:
        node = node.add_variation(move)
    game.headers["Event"] = "Casual Game"
    game.headers["Date"] = time.strftime("%Y.%m.%d")
    if mode == 1:
        game.headers["White"] = "Player"
        game.headers["Black"] = "Stockfish"
    else:
        game.headers["White"] = "Player 1"
        game.headers["Black"] = "Player 2"
    filename = f"game_{time.strftime('%Y%m%d_%H%M%S')}.pgn"
    with open(filename, "w") as f:
        print(game, file=f)
    print(f"[INFO] Game saved to {filename}")

# === CAMERA ===
cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("[OOPS] Camera didn't open.")
    engine.quit()
    sys.exit(1)

board = chess.Board()
ref_frame = None
last_move = None
comp_turn = False
move_history = []

print("[INFO] Quick controls: hit 'r' twice to log a move, 'u' to undo, 'U' to undo two moves, 'd' flips debug mode, 'q' bails out.")
show_board(board)

try:
    while not board.is_game_over():
        ret, frame_raw = cap.read()
        if not ret:
            continue

        display = draw_board_labels(frame_raw.copy())
        cv2.imshow("Chess Tracker", display)
        key = cv2.waitKey(1) & 0xFF

        # === Flip debug mode ===
        if key == ord('d'):
            DEBUG_MODE = not DEBUG_MODE
            state = "ON" if DEBUG_MODE else "OFF"
            print(f"[INFO] Debug mode now: {state}")

        # === Player move time (smash 'r' twice) ===
        if key == ord('r'):
            if ref_frame is None:
                ref_frame = capture_stable_frame(cap)
                print("[DEBUG] Saved the first frame. Now make your move, then press 'r' again.")
            else:
                print("[DEBUG] Got the second frame, crunching the move...")
                frame_after = capture_stable_frame(cap)
                changed_squares = get_changed_squares(ref_frame, frame_after)

                if DEBUG_MODE:
                    print(f"[DEBUG] Changed squares detected: {changed_squares}")

                move_found = False
                if len(changed_squares) >= 2:
                    changed_list = list(changed_squares)
                    for i in range(len(changed_list)):
                        for j in range(len(changed_list)):
                            if i == j:
                                continue
                            from_sq = changed_list[i]
                            to_sq = changed_list[j]
                            uci_str = from_sq + to_sq

                            for suffix in ["", "q"]:
                                try:
                                    mv = chess.Move.from_uci(uci_str + suffix)
                                    if mv in board.legal_moves:
                                        board.push(mv)
                                        move_history.append(mv)
                                        last_move = mv
                                        print(f"[YOU] Nice, you played: {mv.uci()}")
                                        show_board(board, last_move)
                                        if mode == 1:
                                            comp_turn = True
                                        move_found = True
                                        break
                                except Exception:
                                    continue
                            if move_found:
                                break
                        if move_found:
                            break

                if not move_found:
                    print(f"[WARN] Couldn't figure out the move from changed squares: {changed_squares}")
                    print("[INFO] Try again — press 'r' to set a new reference frame.")

                ref_frame = None

        # === Undo one move ===
        if key == ord('u'):
            if move_history:
                mv = move_history.pop()
                board.pop()
                print(f"[UNDO] Yanked last move: {mv}")
                show_board(board)
            else:
                print("[INFO] Nothing to undo.")

        # === Undo two moves ===
        if key == ord('U'):
            if len(move_history) >= 2:
                mv2 = move_history.pop()
                mv1 = move_history.pop()
                board.pop()
                board.pop()
                print(f"[UNDO] Yanked last two moves: {mv1}, {mv2}")
                show_board(board)
            else:
                print("[INFO] Not enough moves to undo twice.")

        # === Computer's turn (mode 1 only) ===
        if mode == 1 and comp_turn and not board.is_game_over():
            result = engine.play(board, chess.engine.Limit(time=random.uniform(0.4, 0.9)))
            mv = result.move
            board.push(mv)
            move_history.append(mv)
            last_move = mv
            print(f"[AI] My turn! I'm going with: {mv.uci()}")
            show_board(board, last_move)
            comp_turn = False

        if key == ord('q'):
            print("[INFO] Quitting out.")
            break

    print("[INFO] That's a wrap — game finished.")
    analyze_game(move_history)
    save_pgn(move_history, mode)

finally:
    cap.release()
    cv2.destroyAllWindows()
    engine.quit()
import cv2
import numpy as np
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--rotate", type=int, default=0,
                    choices=[0, 90, 180, 270],
                    help="Board rotation relative to camera (CW). "
                         "Example: camera from right = 90, from behind = 180, from left = 270.")
args = parser.parse_args()
CAM_ROT = args.rotate

points = []

def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            print(f"[INFO] Point {len(points)}: {x}, {y}")
        else:
            print("[INFO] Already 4 points. Press 'r' to reset or 's' to save.")

def remap_index(r_disp, c_disp, cam_rot):
    """Remap index (row, column) from camera display to standard board notation."""
    if cam_rot == 0:
        r_std, c_std = r_disp, c_disp
    elif cam_rot == 90:
        r_std, c_std = c_disp, 7 - r_disp
    elif cam_rot == 180:
        r_std, c_std = 7 - r_disp, 7 - c_disp
    elif cam_rot == 270:
        r_std, c_std = 7 - c_disp, r_disp
    else:
        r_std, c_std = r_disp, c_disp
    return r_std, c_std

# === CAMERA CALIBRATION ===
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print(" Camera cannot be opened.")
    exit()

cv2.namedWindow("Board Calibration")
cv2.setMouseCallback("Board Calibration", mouse_click)

print("📸 Instructions:")
print(" 1️⃣ Point the camera at the position you WILL use (e.g., from the side).")
print(" 2️⃣ Click 4 board corners (order: top-left, top-right, bottom-right, bottom-left).")
print(" 3️⃣ Press 'r' to reset, 's' to save result as sqdict.json, 'q' to quit.")
print(f"[INFO] Board rotation relative to camera: {CAM_ROT}° (CW)\n")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    vis = frame.copy()

    # Draw clicked points
    for idx, p in enumerate(points):
        cv2.circle(vis, p, 6, (0, 0, 255), -1)
        cv2.putText(vis, str(idx+1), (p[0]+8, p[1]-8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    if len(points) == 4:
        # Draw box & grid
        pts = np.array(points, dtype=np.int32)
        cv2.polylines(vis, [pts], True, (255,255,255), 2)

        src = np.array([[0,0],[8,0],[8,8],[0,8]], dtype=np.float32)
        dst = np.array(points, dtype=np.float32)
        H = cv2.getPerspectiveTransform(src, dst)

        src_grid = np.array([[[x,y] for x in range(9)] for y in range(9)], dtype=np.float32)
        dst_grid = cv2.perspectiveTransform(src_grid.reshape(-1,1,2), H).reshape(9,9,2)

        # Draw grid
        for r in range(9):
            cv2.polylines(vis, [dst_grid[r,:,:].astype(int)], False, (180,180,180), 1)
        for c in range(9):
            cv2.polylines(vis, [dst_grid[:,c,:].astype(int)], False, (180,180,180), 1)

        # === Show labels in standard board notation ===
        files = 'abcdefgh'
        ranks = '87654321'
        font = cv2.FONT_HERSHEY_SIMPLEX

        for r in range(8):
            for c in range(8):
                r_std, c_std = remap_index(r, c, CAM_ROT)
                file_letter = files[c_std]
                rank_char = ranks[r_std]
                label = f"{file_letter}{rank_char}"

                center = dst_grid[r, c] + (dst_grid[r+1, c+1] - dst_grid[r, c]) / 2
                cx, cy = int(center[0]), int(center[1])
                cv2.putText(vis, label, (cx-12, cy+5), font, 0.5, (0,255,255), 1, cv2.LINE_AA)

    cv2.imshow("Board Calibration", vis)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        print("Exit without saving.")
        break
    elif key == ord('r'):
        points = []
        print("[INFO] Reset points.")
    elif key == ord('s'):
        if len(points) != 4:
            print("[WARN] You must click 4 points before saving.")
            continue

        src = np.array([[0,0],[8,0],[8,8],[0,8]], dtype=np.float32)
        dst = np.array(points, dtype=np.float32)
        H = cv2.getPerspectiveTransform(src, dst)

        src_grid = np.array([[[x,y] for x in range(9)] for y in range(9)], dtype=np.float32)
        dst_grid = cv2.perspectiveTransform(src_grid.reshape(-1,1,2), H).reshape(9,9,2)

        displayed_squares = {}
        for r in range(8):
            for c in range(8):
                tl = dst_grid[r, c].tolist()
                tr = dst_grid[r, c+1].tolist()
                br = dst_grid[r+1, c+1].tolist()
                bl = dst_grid[r+1, c].tolist()
                displayed_squares[(r,c)] = [tl,tr,br,bl]

        # Remap board orientation to standard notation
        files = 'abcdefgh'
        ranks = '87654321'
        squares_std = {}
        for (r_disp, c_disp), poly in displayed_squares.items():
            r_std, c_std = remap_index(r_disp, c_disp, CAM_ROT)
            file_letter = files[c_std]
            rank_char = ranks[r_std]
            squares_std[f"{file_letter}{rank_char}"] = poly

        with open('sqdict.json', 'w') as f:
            json.dump(squares_std, f, indent=2)
        print(f"[✅] sqdict.json saved with board rotation {CAM_ROT}° (notation adjusted).")
        break

cap.release()
cv2.destroyAllWindows()

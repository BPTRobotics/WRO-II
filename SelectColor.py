# hsv_calibrator.py
from Camera import get_frame
import cv2
import numpy as np
import argparse
import sys
from yaml import safe_dump
from readConfig import config

# -----------------------------------------------------------------------------
# — HSV / RGB / HEX Conversion Helpers
# -----------------------------------------------------------------------------
def hsv_to_rgb(h, s, v):
    h, s, v = h/360.0, s/100.0, v/100.0
    c = v * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = v - c
    if 0 <= h < 1/6:
        r_, g_, b_ = c, x, 0
    elif 1/6 <= h < 2/6:
        r_, g_, b_ = x, c, 0
    elif 2/6 <= h < 3/6:
        r_, g_, b_ = 0, c, x
    elif 3/6 <= h < 4/6:
        r_, g_, b_ = 0, x, c
    elif 4/6 <= h < 5/6:
        r_, g_, b_ = x, 0, c
    else:
        r_, g_, b_ = c, 0, x
    def clamp255(vf): return int(max(0, min(255, round(vf * 255))))
    return clamp255(r_ + m), clamp255(g_ + m), clamp255(b_ + m)

def rgb_to_hsv(r, g, b):
    r_, g_, b_ = r/255.0, g/255.0, b/255.0
    c_max, c_min = max(r_, g_, b_), min(r_, g_, b_)
    d = c_max - c_min
    if d == 0:
        h = 0
    elif c_max == r_:
        h = (60 * ((g_ - b_) / d) + 360) % 360
    elif c_max == g_:
        h = (60 * ((b_ - r_) / d) + 120) % 360
    else:
        h = (60 * ((r_ - g_) / d) + 240) % 360
    s = 0 if c_max == 0 else (d / c_max) * 100
    v = c_max * 100
    return int(h), int(s), int(v)

def hsv_to_hex(h, s, v):
    r, g, b = hsv_to_rgb(h, s, v)
    hexcol = "#{:02X}{:02X}{:02X}".format(r, g, b)
    print(f"→ HSV=({h},{s},{v}) → RGB=({r},{g},{b}) → HEX={hexcol}")
    return hexcol

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def hex_to_hsv(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    hsv = rgb_to_hsv(r, g, b)
    print(f"← HEX={hex_color} → RGB=({r},{g},{b}) → HSV={hsv}")
    return hsv

if __name__ == "__main__":
    # -----------------------------------------------------------------------------
    # — Argument Parsing
    # -----------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description="HSV Color Calibration")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-left",  action="store_true", help="Calibrate left color")
    group.add_argument("-right", action="store_true", help="Calibrate right color")
    args = parser.parse_args()
    side    = "left"  if args.left  else "right"
    min_hsv = f"min_{side}_hsv"
    max_hsv = f"max_{side}_hsv"
    min_col = f"min_{side}_color"
    max_col = f"max_{side}_color"

    # -----------------------------------------------------------------------------
    # — Load Config via readConfig
    # -----------------------------------------------------------------------------
    colors = config["colors"]
    thresh = int(config.get("contour_threshold", 300))

    # Load HSV bounds
    if min_hsv in colors and max_hsv in colors:
        l_h, l_s, l_v = colors[min_hsv]
        u_h, u_s, u_v = colors[max_hsv]
    else:
        l_h, l_s, l_v = hex_to_hsv(colors[min_col])
        u_h, u_s, u_v = hex_to_hsv(colors[max_col])

    # -----------------------------------------------------------------------------
    # — OpenCV Trackbars
    # -----------------------------------------------------------------------------
    cv2.namedWindow("HSV Trackbars", cv2.WINDOW_NORMAL)
    for name, val, maxi in [
        ("L - H", l_h, 179),
        ("L - S", l_s, 255),
        ("L - V", l_v, 255),
        ("U - H", u_h, 179),
        ("U - S", u_s, 255),
        ("U - V", u_v, 255),
        ("Contour Thresh", thresh, 5000)
    ]:
        cv2.createTrackbar(name, "HSV Trackbars", val, maxi, lambda x: None)

    # -----------------------------------------------------------------------------
    # — Webcam Loop
    # -----------------------------------------------------------------------------
    cap = cv2.VideoCapture(0)
    kernel = np.ones((5, 5), np.uint8)
    print(f"Calibrating {side.upper()} — press 's' to save, 'q' to quit.")

    while True:
        frame = get_frame(cap)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Fetch trackbar positions
        l_h = cv2.getTrackbarPos("L - H", "HSV Trackbars")
        l_s = cv2.getTrackbarPos("L - S", "HSV Trackbars")
        l_v = cv2.getTrackbarPos("L - V", "HSV Trackbars")
        u_h = cv2.getTrackbarPos("U - H", "HSV Trackbars")
        u_s = cv2.getTrackbarPos("U - S", "HSV Trackbars")
        u_v = cv2.getTrackbarPos("U - V", "HSV Trackbars")
        thresh = cv2.getTrackbarPos("Contour Thresh", "HSV Trackbars")

        lower = np.array([l_h, l_s, l_v])
        upper = np.array([u_h, u_s, u_v])
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.dilate(mask, kernel)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # Draw contours
        cnts, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            if cv2.contourArea(c) > thresh:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(result, "Detected", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Mask", mask)
        cv2.imshow("Result", result)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            # Save exact HSV arrays + hex + threshold
            colors[min_hsv] = [l_h, l_s, l_v]
            colors[max_hsv] = [u_h, u_s, u_v]
            colors[min_col] = hsv_to_hex(l_h, l_s, l_v)
            colors[max_col] = hsv_to_hex(u_h, u_s, u_v)
            config["contour_threshold"] = thresh
            with open("config.yaml", "w") as f:
                safe_dump(config, f)
            print("→ Saved HSV arrays & hex to config.yaml")
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

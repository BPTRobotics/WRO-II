import asyncio
import numpy as np

from GetDistances import get_distances
from LineFollow_Motor import get_direction
from RobotMovementController import Move
from Motor import boost
from readConfig import config
from Camera import init_camera, get_frame, normalize_2_middle
from GetColorPositionFromCamera import find_color_objects
from ColorSensor import read_color,is_nearly_color
from YawManager import init_yaw,get_yaw_difference

# Global run flag
_should_go = True

# Obstacle threshold
NARROWNESS = (config["groundWidth"] - 20) / 1.5

# HSV ranges for right color
h1_r, s1_r, v1_r = config['colors']['min_right_hsv']
h2_r, s2_r, v2_r = config['colors']['max_right_hsv']
LO_R = np.array((h1_r, s1_r, v1_r), np.uint8)
HI_R = np.array((h2_r, s2_r, v2_r), np.uint8)

# HSV ranges for left color
h1_l, s1_l, v1_l = config['colors']['min_left_hsv']
h2_l, s2_l, v2_l = config['colors']['max_left_hsv']
LO_L = np.array((h1_l, s1_l, v1_l), np.uint8)
HI_L = np.array((h2_l, s2_l, v2_l), np.uint8)

line1_color = config['colors']['line1_color']


# Shared centroid offsets
cx_r = cy_r = None
cx_l = cy_l = None

blue_line_touch = 0
yaw_diff = 0

async def start_frame_gathering():
    global cx_r, cy_r, cx_l, cy_l

    cap = init_camera()
    if not cap:
        print("Error: Camera not found")
        return

    try:
        while _should_go:
            try:
                frame = get_frame(cap)
            except IOError as e:
                print("Warning: failed to read frame:", e)
                await asyncio.sleep(0.1)
                continue

            # Find right-colored objects
            objs_r = find_color_objects(frame, LO_R, HI_R)
            if objs_r:
                # take the first (or you could pick largest area, etc.)
                _cx_r, _cy_r = objs_r[0]['centroid']
                cx_r, cy_r = normalize_2_middle((_cx_r, _cy_r), frame)
            else:
                cx_r = cy_r = None

            # Find left-colored objects
            objs_l = find_color_objects(frame, LO_L, HI_L)
            if objs_l:
                _cx_l, _cy_l = objs_l[0]['centroid']
                cx_l, cy_l = normalize_2_middle((_cx_l, _cy_l), frame)
            else:
                cx_l = cy_l = None

            await asyncio.sleep(0)  # yield to the event loop
    finally:
        cap.release()
        print("Camera released")
async def start_control_loop():
    init_yaw()
    while _should_go:
        distances = get_distances()
        base_dir, speed = get_direction(*distances)

        # yaw_diff = get_yaw_difference()
        # print(f"Yaw difference: {yaw_diff:.2f} degrees [YET UNUSED]")

        # Decide which object to follow
        chosen = None
        if cy_r is not None and cy_l is not None:
            # pick the nearer one (smaller cy => nearer)
            chosen = 'right' if cy_r < cy_l else 'left'
        elif cy_r is not None:
            chosen = 'right'
        elif cy_l is not None:
            chosen = 'left'

        # apply the appropriate offset
        if chosen == 'right':
            direction = max(-1, min(
                base_dir * 2 + 2, 1))
            # boost(direction,True)
        elif chosen == 'left':
            direction = max(-1, min(
                base_dir * 2 - 2, 1))
            # boost(direction,True)
        else:
            # no object seen: just use base direction
            direction = base_dir

        direction += get_yaw_difference() / 16  # adjust direction based on yaw difference
        # speed adjustment (you could also factor in cy if desired)
        speed = max(0, min((speed * 2 - abs(direction / 16)), 1))

        print(
            f"Chosen: {chosen or 'none'}, "
            f"Base dir: {base_dir:.2f}, "
            f"Dir: {direction:.2f}, "
            f"Spd: {speed:.2f}, "
            f"Distances: {' '.join(f'{d:.1f}' for d in distances)}"
        )

        # obstacle check
        if any(d < NARROWNESS for d in distances):
            print("Obstacle detected, boosting backward!")
            boost()

############TEST########################################
        if blue_line_touch > 0:
            print(f"BLIE LINE DETECTED, FORCE STOPPING: {blue_line_touch}")
            stop()
            speed = 0
            direction = 0
############TEST########################################
        Move(speed, direction)
        await asyncio.sleep(0.05)
async def start_color_detection():
    while _should_go:
        _, r, g, b = read_color()
        is_blue = is_nearly_color(r, g, b, line1_color)

        global blue_line_touch
        if is_blue:
            blue_line_touch += 1
            print(f"Blue line touched {blue_line_touch} times")

        await asyncio.sleep(0.1)
def stop():
    global _should_go
    _should_go = False

async def main():
    frame_task   = asyncio.create_task(start_frame_gathering())
    control_task = asyncio.create_task(start_control_loop())
    color_task   = asyncio.create_task(start_color_detection())

    try:
        await asyncio.gather(frame_task, control_task, color_task)
    except KeyboardInterrupt:
        print("Stopping on user interrupt.")
        stop()
    finally:
        frame_task.cancel()
        control_task.cancel()
        await asyncio.gather(frame_task, control_task, color_task, return_exceptions=True)
        print("Shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Force stopping.")

import asyncio
import numpy as np
from colorama import init as colorama_init, Fore, Style

from GetDistances import get_distances
from LineFollow_Motor import get_direction
from RobotMovementController import Move
from readConfig import config
from Camera import init_camera, get_frame, normalize_2_middle
from GetColorPositionFromCamera import find_color_objects
from ColorSensor import read_color, is_red, is_red
from YawManager import init_yaw, add_yaw, get_yaw_difference, get_initial_yaw
import LED
import ButtonDirection
from Motor import boost

# Initialize colorama
colorama_init(autoreset=True)

# Global run flag
_should_go = True

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



# Shared centroid offsets
cx_r = cy_r = None
cx_l = cy_l = None

red_line_touch = 0
MAX_red_LINE_TOUCH = 9

line_touch_add = 90

yaw_diff = 0

BACK_THRESHOLD = config['back_threshold']

FINAL_DIRECTION = 'none'

from enum import Enum
class LedState_c(Enum):
    ALL_ON = 1
    ALL_OFF = 2
    LOADING = 3
    CHOOSE_LEFT = 4
    CHOOSE_RIGHT = 5
LedState = LedState_c.LOADING

async def updateFinalDirection():
    global FINAL_DIRECTION, LedState, line_touch_add
    while True:
        if ButtonDirection.isLeftPressed():
            FINAL_DIRECTION = 'left'
            LedState = LedState_c.CHOOSE_LEFT
            break
        elif ButtonDirection.isRightPressed():
            FINAL_DIRECTION = 'right'
            LedState = LedState_c.CHOOSE_RIGHT
            line_touch_add *= -1
            break
        else:
            print(Fore.YELLOW + "Waiting for button press...")
            await asyncio.sleep(.75)
    print(Fore.CYAN + f"Final direction updated: {FINAL_DIRECTION}")

async def start_frame_gathering():
    global cx_r, cy_r, cx_l, cy_l

    cap = init_camera()
    if not cap:
        print(Fore.RED + "Error: Camera not found")
        return

    try:
        while _should_go:
            try:
                frame = get_frame(cap)
            except IOError as e:
                print(Fore.RED + f"Warning: failed to read frame: {e}")
                await asyncio.sleep(0.1)
                continue

            objs_r = find_color_objects(frame, LO_R, HI_R)
            if objs_r:
                _cx_r, _cy_r = objs_r[0]['centroid']
                cx_r, cy_r = normalize_2_middle((_cx_r, _cy_r), frame)
            else:
                cx_r = cy_r = None

            objs_l = find_color_objects(frame, LO_L, HI_L)
            if objs_l:
                _cx_l, _cy_l = objs_l[0]['centroid']
                cx_l, cy_l = normalize_2_middle((_cx_l, _cy_l), frame)
            else:
                cx_l = cy_l = None

            await asyncio.sleep(0)
    finally:
        cap.release()
        print(Fore.GREEN + "Camera released")

async def start_control_loop():
    global LedState
    # await init_yaw()
    LedState = LedState_c.ALL_ON

    while _should_go:
        distances = get_distances()
        l, m, r, b = distances
        base_dir, speed = get_direction(l, m, r)

        chosen = None
        if cy_r is not None and cy_l is not None:
            chosen = 'right' if cy_r < cy_l else 'left'
        elif cy_r is not None:
            chosen = 'right'
        elif cy_l is not None:
            chosen = 'left'

        if chosen == 'right':
            direction = max(-1, min(base_dir * 2 + 2, 1))
        elif chosen == 'left':
            direction = max(-1, min(base_dir * 2 - 2, 1))
        else:
            direction = base_dir

        # yaw_diff = get_yaw_difference() 
        # direction += yaw_diff / 500

        direction = max(-1, min(direction, 1))

        # # base_dir += yaw_diff
        # direction = max(-1, min(base_dir, 1))
        
        speed = max(0.1, min((speed * 5 - abs(direction / 16)), 1))

        if (l < BACK_THRESHOLD or m < BACK_THRESHOLD or r < BACK_THRESHOLD) and b > BACK_THRESHOLD*5:
            boost()

        print(
            Fore.MAGENTA +
            f"Chosen: {chosen or 'none'}, "
            f"Base dir: {base_dir:.2f}, "
            f"Dir: {direction:.2f}, "
            f"Spd: {speed:.2f}, "
            f"Distances: {' '.join(f'{d:.1f}' for d in distances)}"
            f" Yaw diff: {yaw_diff:.2f} degrees"
            f"CX_R: {cx_r}, CY_R: {cy_r}, "
            f"CX_L: {cx_l}, CY_L: {cy_l}"
        )

        if FINAL_DIRECTION != 'none':
            Move(speed, direction)

        await asyncio.sleep(0.05)

async def led_manager():
    while _should_go:
        if LedState == LedState_c.ALL_ON:
            LED.all_on()
        elif LedState == LedState_c.ALL_OFF:
            LED.all_off()
        elif LedState == LedState_c.LOADING:
            await LED.loading()
        elif LedState == LedState_c.CHOOSE_LEFT:
            LED.choose_left()
        elif LedState == LedState_c.CHOOSE_RIGHT:
            LED.choose_right()
        else:
            print(Fore.RED + f"Unknown LED state: {LedState}")
            LED.all_off()
        print(Fore.BLUE + f"LED state: {LedState}")

        await asyncio.sleep(1)

async def start_color_detection():
    while _should_go:
        r, g, b = read_color()
        _is_red = is_red(r, g, b)

        global red_line_touch
        if _is_red:
            print(Fore.YELLOW + f"{get_initial_yaw()}")
            add_yaw(line_touch_add)
            print(Fore.YELLOW + f"Yaw adjusted by {line_touch_add} degrees, total yaw: {get_initial_yaw()} degrees")

            red_line_touch += 1
            print(Fore.LIGHTBLUE_EX + f"red line touched {red_line_touch} times")

            if red_line_touch >= MAX_red_LINE_TOUCH:
                print(Fore.RED + f"red LINE DETECTED, FORCE STOPPING: {red_line_touch}")
                stop()

            await asyncio.sleep(2)
        await asyncio.sleep(0.005)

def stop():
    global _should_go
    _should_go = False
    print(Fore.RED + "Stopping all tasks...")

async def main():
    frame_task = asyncio.create_task(start_frame_gathering())
    control_task = asyncio.create_task(start_control_loop())
    color_task = asyncio.create_task(start_color_detection())
    led_task = asyncio.create_task(led_manager())
    button_task = asyncio.create_task(updateFinalDirection())

    try:
        await asyncio.gather(button_task, led_task, frame_task, control_task, color_task)
    except KeyboardInterrupt:
        print(Fore.RED + "Stopping on user interrupt.")
        stop()
    finally:
        frame_task.cancel()
        control_task.cancel()
        color_task.cancel()
        led_task.cancel()
        button_task.cancel()

        await asyncio.gather(frame_task, control_task, color_task, return_exceptions=True)
        print(Fore.GREEN + "Shutdown complete.")

        from RPi.GPIO import cleanup
        cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.RED + "Force stopping.")

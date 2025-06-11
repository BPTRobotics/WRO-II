from YawManager import init_yaw, add_yaw, get_yaw_difference
from Motor import stop, setSpeed
from Steer import setDirection

if __name__ == "__main__":
    init_yaw()
    add_yaw(45)
    setDirection(.9)  # Scale yaw difference to servo range
    while True:
        try:
            yaw_diff = get_yaw_difference()

            speed = min(abs(yaw_diff),1)
            print(f"Difference: {yaw_diff:.2f}°; speed: {speed:.2f}")

            if abs(yaw_diff) < 10:
                stop()
                print("Stopping due to small yaw difference.")
                continue
            setSpeed(speed,yaw_diff > 0)
        except KeyboardInterrupt:
            print("\nExiting...")
            break

import time
import math
import IMU  # Use module import, NOT direct variable imports
import asyncio

imu = IMU.IMU()

initial_yaw = 0.0

async def init_yaw(timeout=10):
    global initial_yaw
    print("Calibrating initial yaw, please hold still...")
    initial_yaw = get_yaw()
    last_initial_yaw = initial_yaw
    start_time = time.time()

    while True:
        current_yaw = get_yaw()
        yaw_diff = current_yaw - last_initial_yaw
        correction = IMU.Kp * yaw_diff

        if abs(correction) < 0.01:
            break

        last_initial_yaw = current_yaw
        print(f"Yaw Correction: {correction:.2f}°")
        
        if time.time() - start_time > timeout:
            print("Timeout reached, using last known yaw.")
            break
        await asyncio.sleep(0.005)
        

    initial_yaw = current_yaw
    print(f"Initial Yaw set to: {initial_yaw:.2f}°")

def add_yaw(yaw):
    global initial_yaw
    initial_yaw += yaw
    initial_yaw = initial_yaw % 360  # Normalize to [0, 360)
def get_initial_yaw():
    global initial_yaw
    return initial_yaw

def get_yaw():
    """
    Get the current yaw angle from the IMU.
    Returns:
        float: The yaw angle in degrees.
    """

    imu.QMI8658_Gyro_Accel_Read()
    imu.AK09918_MagRead()
    imu.icm20948CalAvgValue()

    imu.imuAHRSupdate(
        IMU.MotionVal[0] * 0.0175, IMU.MotionVal[1] * 0.0175, IMU.MotionVal[2] * 0.0175,
        IMU.MotionVal[3], IMU.MotionVal[4], IMU.MotionVal[5],
        IMU.MotionVal[6], IMU.MotionVal[7], IMU.MotionVal[8]
    )

    # Read the updated quaternions directly from module
    q0 = IMU.q0
    q1 = IMU.q1
    q2 = IMU.q2
    q3 = IMU.q3

    # Compute yaw (in degrees)
    yaw = math.atan2(-2 * q1 * q2 - 2 * q0 * q3, 2 * q2 * q2 + 2 * q3 * q3 - 1) * 57.3
    return yaw

def get_yaw_difference():
    """
    Get the difference between the current yaw and the initial yaw.
    Returns:
        float: The yaw difference in degrees, normalized to [-180, 180].
    """
    current_yaw = get_yaw()
    return (current_yaw - initial_yaw + 180) % 360 - 180

if __name__ == "__main__":
    from asyncio import run as arun
    arun(init_yaw())
    while True:
        try:
            yaw_diff = get_yaw_difference()
            print(f"Difference: {yaw_diff:.2f}°")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

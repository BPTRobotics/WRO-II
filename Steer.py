from readConfig import config
from adafruit_servokit import ServoKit

pcapin  = config["pins"]["servo"]["pcapin"]


import time
import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)
while not i2c.try_lock():
    pass
i2c.unlock()

time.sleep(0.5)



kit = ServoKit(channels=8)

def setDirection(direction):
    if (direction > 1 or direction < -1):
        raise ValueError("Direction must be between -1 and 1")
    
    Direction = direction * -90 + 90
    print("Direction: ", Direction)
    kit.servo[pcapin].angle = Direction

if __name__ == "__main__":
    setDirection(0.0)
    time.sleep(1)
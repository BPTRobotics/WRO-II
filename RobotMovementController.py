from Motor import setSpeed
from Steer import setDirection


def Move(speed,direction):
    setSpeed(speed)
    setDirection(direction)

if __name__ == "__main__":
    for x in range(5000):
        Move(1, 0.2)
from Motor import setSpeed
from Steer import setDirection


def Move(speed, direction):
    if speed < 0:
        setSpeed(abs(speed), False)
    else:
        setSpeed(speed, True)

    setDirection(direction)

if __name__ == "__main__":
    for x in range(5000):
        Move(1, 0.2)
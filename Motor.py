from time import sleep
from Steer import setDirection
from readConfig import config
import RPi.GPIO as GPIO

ENA = config["pins"]["motor"]["ENA"]
IN1 = config["pins"]["motor"]["IN1"]
IN2 = config["pins"]["motor"]["IN2"]

GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

p=GPIO.PWM(ENA,1000)
p.start(25)

def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

def backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)

stop()

def setSpeed(speed):
    if speed < 0 or speed > 1:
        raise ValueError("Speed must be between 0 and 1")

    if speed > 0.1:
        forward()
    else:
        stop()

    p.ChangeDutyCycle(speed*100)

def boost(direction = 0,isForward = False):
    setDirection(direction)
    p.ChangeDutyCycle(100)
    if isForward:
        forward()
    else:
        backward()
    sleep(2)
    stop()

if __name__ == "__main__":
    for x in range(1000):
        setSpeed(0.9)
        sleep(0.1)
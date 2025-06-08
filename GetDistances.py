import RPi.GPIO as GPIO
import time
from readConfig import config

# trigger pin numbers
distance_sensor = config["pins"]["distance_sensor"]
TRIG1 = distance_sensor["TRIG1"]
TRIG2 = distance_sensor["TRIG2"]
TRIG3 = distance_sensor["TRIG3"]

ECHO1 = distance_sensor["ECHO1"]
ECHO2 = distance_sensor["ECHO2"]
ECHO3 = distance_sensor["ECHO3"]

# setup GPIO pins for ultrasonic sensors
for trig in [TRIG1, TRIG2, TRIG3]:
    print("Setting up TRIG pin:", trig)
    GPIO.setup(trig, GPIO.OUT)
for echo in [ECHO1, ECHO2, ECHO3]:
    print("Setting up ECHO pin:", echo)
    GPIO.setup(echo, GPIO.IN)


def get_distances():
    distances = []
    for trig, echo in [(TRIG1, ECHO1), (TRIG2, ECHO2), (TRIG3, ECHO3)]:
        GPIO.output(trig, False)
        time.sleep(0.01)

        GPIO.output(trig, True)
        time.sleep(0.00001)
        GPIO.output(trig, False)

        pulse_start = time.time()
        while GPIO.input(echo) == 0:
            pulse_start = time.time()

        while GPIO.input(echo) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17000
        distances.append(distance)

    return distances

if __name__ == "__main__":
    while True:
        distances = get_distances()
        print("Distances:", distances)
        time.sleep(1)
import RPi.GPIO as GPIO
import time

from readConfig import config

GPIO.setmode(GPIO.BCM)
pin = int(config['pins']['button'])
print(pin)

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enables internal pull-up

try:
    while True:
        print(GPIO.input(pin))
        time.sleep(0.1)
finally:
    GPIO.cleanup()
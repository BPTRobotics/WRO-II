import RPi.GPIO as GPIO
import asyncio
from readConfig import config

LED_PINS = config['pins']['led']

for x in LED_PINS:
    GPIO.setup(x, GPIO.OUT)

def all_on():
    for x in LED_PINS:
        GPIO.output(x, GPIO.HIGH)
def all_off():
    for x in LED_PINS:
        GPIO.output(x, GPIO.LOW)

async def blink(pin, duration=0.5):
    GPIO.output(pin, GPIO.HIGH)
    await asyncio.sleep(duration)
    GPIO.output(pin, GPIO.LOW)

async def loading(duration = 0.1):
    for x in LED_PINS:
        GPIO.output(x, GPIO.HIGH)
        await asyncio.sleep(duration)
    for x in LED_PINS:
        GPIO.output(x, GPIO.LOW)
        await asyncio.sleep(duration)

def choose_left():
    for x in LED_PINS:
        GPIO.output(x, GPIO.LOW)
    GPIO.output(LED_PINS[0], GPIO.HIGH)
    GPIO.output(LED_PINS[1], GPIO.HIGH)
def choose_right():
    for x in LED_PINS:
        GPIO.output(x, GPIO.LOW)
    GPIO.output(LED_PINS[-1], GPIO.HIGH)
    GPIO.output(LED_PINS[-2], GPIO.HIGH)

if __name__ == "__main__":
    asyncio.run(loading())
    all_off()
    print("LED test complete.")
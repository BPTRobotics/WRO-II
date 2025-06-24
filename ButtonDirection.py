import time
import RPi.GPIO as GPIO
from readConfig import config


GPIO.setmode(GPIO.BCM)
left_button = config['pins']['button'][0]
right_button = config['pins']['button'][1]

GPIO.setup(left_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(right_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Debounce settings
DEBOUNCE_CHECKS = 5     # Number of samples to confirm state change
DEBOUNCE_DELAY = 0.01   # Delay between samples (10ms)

class DebouncedButton:
    def __init__(self, pin):
        self.pin = pin
        self.state = False  # Last stable state (pressed = True)
    
    def update(self):
        """Update the button state using debounce logic."""
        pressed_count = 0
        for _ in range(DEBOUNCE_CHECKS):
            if GPIO.input(self.pin) == GPIO.LOW:
                pressed_count += 1
            time.sleep(DEBOUNCE_DELAY)
        
        if pressed_count == DEBOUNCE_CHECKS:
            self.state = True
        elif pressed_count == 0:
            self.state = False
        # If mixed readings, keep current state
        
        return self.state

# Create button instances
left = DebouncedButton(left_button)
right = DebouncedButton(right_button)

def isLeftPressed():
    return left.update()

def isRightPressed():
    return right.update()

if __name__ == "__main__":
    try:
        while True:
            if isLeftPressed():
                print("Left button pressed")
            if isRightPressed():
                print("Right button pressed")
            time.sleep(0.1)  # Polling interval
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()
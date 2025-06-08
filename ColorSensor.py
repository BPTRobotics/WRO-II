import smbus2
import time

# Bus number for software I2C on GPIO 23/24
bus_num = 4
i2c_address = 0x29  # TCS34725 address

bus = smbus2.SMBus(bus_num)

# TCS34725 register addresses (example)
ENABLE = 0x80
ATIME = 0x81
CONTROL = 0x8F
CDATAL = 0x94  # Clear data low byte
RDATAL = 0x96  # Red data low byte
GDATAL = 0x98  # Green data low byte
BDATAL = 0x9A  # Blue data low byte

def write_register(reg, value):
    bus.write_byte_data(i2c_address, reg, value)

def read_register(reg):
    return bus.read_byte_data(i2c_address, reg)

def read_word(reg):
    # Read low and high bytes and combine
    low = bus.read_byte_data(i2c_address, reg)
    high = bus.read_byte_data(i2c_address, reg + 1)
    return (high << 8) | low

# Initialize sensor (simplified)
def init_sensor():
    # Power on sensor (PON) and enable RGBC (AEN)
    write_register(ENABLE, 0x03)
    # Set integration time (example)
    write_register(ATIME, 0xEB)  # ~50 ms
    # Set gain
    write_register(CONTROL, 0x01)  # 4x gain

def read_color():
    clear = read_word(CDATAL)
    red = read_word(RDATAL)
    green = read_word(GDATAL)
    blue = read_word(BDATAL)
    return clear, red, green, blue

init_sensor()

import math

def color_distance(c1, c2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def is_nearly_color(r, g, b, reference, threshold=15):
    """
    Compares RGB value to known blue using Euclidean distance.
    """
    return color_distance((r, g, b), reference) < threshold


if __name__ == '__main__':
    known_blue = (69, 49, 38)
    while True:
        clear, r, g, b = read_color()
        is_blue = is_nearly_color(r, g, b, known_blue)
        print(f"Is Blue: {is_blue}  R: {r}, G: {g}, B: {b}")
        time.sleep(0.01)

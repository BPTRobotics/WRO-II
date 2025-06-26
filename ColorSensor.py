import smbus2
import time

# Bus and sensor setup
bus_num = 4
i2c_address = 0x29
bus = smbus2.SMBus(bus_num)

# TCS34725 register addresses
ENABLE = 0x80
ATIME = 0x81
CONTROL = 0x8F
CDATAL = 0x94
RDATAL = 0x96
GDATAL = 0x98
BDATAL = 0x9A

def write_register(reg, value):
    try:
        bus.write_byte_data(i2c_address, reg, value)
    except OSError:
        print(f"I2C Write Error: {reg:#04x} = {value:#04x}")

def read_word(reg):
    try:
        low = bus.read_byte_data(i2c_address, reg)
        high = bus.read_byte_data(i2c_address, reg + 1)
    except OSError:
        print(f"I2C Read Error: {reg:#04x}")
        return 0
    return (high << 8) | low

def init_sensor():
    write_register(ENABLE, 0x03)
    write_register(ATIME, 0xEB)
    write_register(CONTROL, 0x01)

def read_color():
    clear = read_word(CDATAL)
    r = read_word(RDATAL)
    g = read_word(GDATAL)
    b = read_word(BDATAL)
    clear = max(clear, 1)  # Avoid divide-by-zero
    return r / clear / 1.5, g / clear, b / clear

# Simple threshold: must be at least this high to be considered a color
MIN_BLUE_COLOR_VALUE = 0.44
MIN_RED_COLOR_VALUE = 0.29

def is_red(r, g, b):
    return r > g and r > b and r > MIN_RED_COLOR_VALUE

def is_blue(r, g, b):
    return b > r and b > g and b > MIN_BLUE_COLOR_VALUE

# Init on import
init_sensor()

if __name__ == "__main__":
    while True:
        r, g, b = read_color()
        if is_red(r, g, b):
            label = "RED"
        elif is_blue(r, g, b):
            label = "BLUE"
        else:
            label = "UNSURE"
        print(f"{label} - R: {r:.3f}, G: {g:.3f}, B: {b:.3f}")
        time.sleep(0.2)

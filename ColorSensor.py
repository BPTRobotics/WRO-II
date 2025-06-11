import smbus2
import time
# Bus number for software I2C on GPIO 23/24
bus_num = 4
i2c_address = 0x29 # TCS34725 address
bus = smbus2.SMBus(bus_num)
# TCS34725 register addresses (example)
ENABLE = 0x80
ATIME = 0x81
CONTROL = 0x8F
CDATAL = 0x94 # Clear data low byte
RDATAL = 0x96 # Red data low byte
GDATAL = 0x98 # Green data low byte
BDATAL = 0x9A # Blue data low byte

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

def read_raw_color():
    clear = read_word(CDATAL)
    red = read_word(RDATAL)
    green = read_word(GDATAL)
    blue = read_word(BDATAL)
    return clear, red, green, blue

def read_color():
    """
    Read color data from the TCS34725 sensor.
    Returns:
    tuple: (clear, red, green, blue) values
    """
    clear, red, green, blue = read_raw_color()
    return red / clear, green / clear, blue / clear

def read_averaged_color(history_size=5):
    """
    Read and average color data from the TCS34725 sensor.
    Returns:
    tuple: (clear, red, green, blue) values
    """
    # Initialize color history with first reading
    color_history = []
    
    # Fill history with initial readings
    for _ in range(history_size):
        clear, red, green, blue = read_raw_color()
        color_history.append((red/clear, green/clear, blue/clear))
    
    # Calculate averages
    avg_r = sum(x[0] for x in color_history) / len(color_history)
    avg_g = sum(x[1] for x in color_history) / len(color_history)
    avg_b = sum(x[2] for x in color_history) / len(color_history)
    
    return avg_r, avg_g, avg_b

init_sensor()

def is_blue(r,g,b,threshold):
    if b > r and b > g and b >= threshold:
        return True
    return False
def is_red(r,g,b,threshold):
    if r > g and r > b and r >= threshold:
        return True
    return False

if __name__ == '__main__':
    from readConfig import config
    blue_color_threshold = config['colors']['blue_color_threshold']
    red_color_threshold = config['colors']['red_color_threshold']
    
    while True:
        # Use averaged color readings
        r, g, b = read_averaged_color()
        _is_blue = is_blue(r, g, b, blue_color_threshold)
        _is_red = is_red(r, g, b, red_color_threshold)
        print(f"{('RED' if _is_red else 'BLUE' if _is_blue else 'NONE')}  R: {r}, G: {g}, B: {b}")
        time.sleep(0.01)
import ColorSensor
import time

def main():
    min_r = float('inf')
    min_g = float('inf')
    min_b = float('inf')
    max_r = float('-inf')
    max_g = float('-inf')
    max_b = float('-inf')

    print("Reading sensor data... Press CTRL+C to stop and show min/max.")

    try:
        while True:
            r, g, b = ColorSensor.read_color()
            min_r = min(min_r, r)
            min_g = min(min_g, g)
            min_b = min(min_b, b)
            max_r = max(max_r, r)
            max_g = max(max_g, g)
            max_b = max(max_b, b)
            time.sleep(0.05)  # Adjust delay as needed
    except KeyboardInterrupt:
        print("\nMeasurement stopped.")
        print(f"Minimum values: R={min_r:.4f}, G={min_g:.4f}, B={min_b:.4f}")
        print(f"Maximum values: R={max_r:.4f}, G={max_g:.4f}, B={max_b:.4f}")

if __name__ == "__main__":
    ColorSensor.init_sensor()  # Make sure sensor initialized
    main()

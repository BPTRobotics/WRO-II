if __name__ == "__main__":
    from Motor import setSpeed
    from ColorSensor import read_averaged_color, is_blue
    from readConfig import config
    from time import sleep
    
    blue_color_threshold = config['colors']['blue_color_threshold']
    
    while True:
        r, g, b = read_averaged_color()
        _is_blue = is_blue(r, g, b, blue_color_threshold)
        if _is_blue:
            print("Blue!")
            setSpeed(0.0)
            break
        setSpeed(.7)
        sleep(0.01)
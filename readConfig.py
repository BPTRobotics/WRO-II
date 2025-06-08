from RPi.GPIO import setmode, BOARD, BCM
from yaml import safe_load

config : object
with open("config.yaml", "r") as file:
    # print('File: """',file.read(),'"""')
    config = safe_load(file.read())
    print(config)


pinmode = str(config["pins"]["mode"]).upper()
if(pinmode == "BOARD"):
    setmode(BOARD)
elif (pinmode == "BCM"):
    setmode(BCM)
else:
    print("Invalid pin mode specified in the config file. Please use 'BOARD' or 'BCM'.")
    raise ValueError("Invalid pin mode specified in the config file. Please use 'BOARD' or 'BCM'.")
    # Optionally, you can exit the program if the pin mode is invalid
    exit(1)
import os

import RPi.GPIO as GPIO

 
REED_SWITCH_GPIO = os.getenv('REED_SWITCH_GPIO')

GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
GPIO.setup(REED_SWITCH_GPIO, GPIO.IN) # GPIO Assign mode
# GPIO.add_event_detect(REED_SWITCH_GPIO, GPIO.RISING, callback=)


def reed_switch_is_open() -> bool:
    return not GPIO.input(REED_SWITCH_GPIO)
    
import os

import RPi.GPIO as GPIO

 
REED_SWITCH_GPIO = int(os.getenv('REED_SWITCH_GPIO'))

GPIO.setmode(GPIO.BCM) # GPIO Numbers instead of board numbers
GPIO.setup(REED_SWITCH_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP) # GPIO Assign mode
# GPIO.add_event_detect(REED_SWITCH_GPIO, GPIO.RISING, callback=)


def reed_switch_is_open() -> bool:
    return not GPIO.input(REED_SWITCH_GPIO)


def reed_switch_is_open_int() -> int:
    return int(reed_switch_is_open())

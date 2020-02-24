#!/usr/bin/env python2.7

import hid
import time
from commands import *
from usb_comm import *





VID = 0x0451
PID = 0x4200


setup(VID,PID)
time.sleep(3)

get_data()
led_test(1)
time.sleep(3)
led_test(0)

import RPi.GPIO as GPIO
from time import sleep
import sys

motor_channel = (29,31,33,35)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(motor_channel, GPIO.OUT)

print('motor running\n')

while True:
	GPIO.output(motor_channel,(GPIO.HIGH,GPIO.LOW,GPIO.LOW,GPIO.HIGH))
	sleep(0.02)
	GPIO.output(motor_channel,(GPIO.HIGH,GPIO.HIGH,GPIO.LOW,GPIO.LOW))
	sleep(0.02)
	GPIO.output(motor_channel,(GPIO.LOW,GPIO.HIGH,GPIO.HIGH,GPIO.LOW))
	sleep(0.02)
	GPIO.output(motor_channel,(GPIO.LOW,GPIO.LOW,GPIO.HIGH,GPIO.HIGH))
	sleep(0.02)


import RPi.GPIO as GPIO
import time
import sys

motor_channel = (29,31,33,35)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(motor_channel, GPIO.OUT)

half_step_seq = [[1,0,0,0],[1,1,0,0],
                 [0,1,0,0],[0,1,1,0],
                 [0,0,1,0],[0,0,1,1],
                 [0,0,0,1],[1,0,0,1]]



while True:
    print('motor running forward\n')
    for step in range(0,25):
        for pos in range(0,8):
            GPIO.output(motor_channel,half_step[pos])
            print(half_step[pos])
            time.sleep(0.005)

    print('motor running backwards\n')
    for step in range(0,25):
        for pos in range(7,-1,-1):
            GPIO.output(motor_channel,half_step[pos])
            print(half_step[pos])
            time.sleep(0.005)
   
    
	


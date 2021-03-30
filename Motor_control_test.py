import RPi.GPIO as GPIO
import time
import sys

motor_channel = (29,31,33,35)
homing_pos = 36
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(motor_channel, GPIO.OUT)
GPIO.setup(homing_pos, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

half_step_seq = [[1,0,0,0],[1,1,0,0],
                 [0,1,0,0],[0,1,1,0],
                 [0,0,1,0],[0,0,1,1],
                 [0,0,0,1],[1,0,0,1]]

#Check for homing position
pos = 0

def setup():
    global pos
    print('Finding homing position')
    while GPIO.input(homing_pos) == GPIO.LOW:
        GPIO.output(motor_channel,half_step_seq[pos])
        pos = (pos + 1) & len(half_step_seq)
        time.sleep(0.005)
    print("homing pos @" + str(pos))

    
def run_motor():
    global pos
    count = 0
    while count < 5:
        print('motor running forward\n')
        for step in range(0,200):
            GPIO.output(motor_channel,half_step[pos])
            print(half_step[pos])
            pos = (pos + 1)  & len(half_step_seq)
            time.sleep(0.005)

        print('motor running backwards\n')
        for step in range(0,200):
            GPIO.output(motor_channel,half_step[pos])
            print(half_step[pos])
            pos = (pos - 1)  & len(half_step_seq)
            time.sleep(0.005)
        count = count + 1

setup()

while True:
    key = input("Start(s) or End(e): ")
    if (key == 's'):
        run_motor()
    elif(key == 'e'):
        print('Motor stoppped')
   
   
    
	


#!/usr/bin/env python3.6

import hid
import time
from commands import *
from usb_comm import *
import tkinter as tk
from tkinter import ttk
import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import threading
import RPi.GPIO as GPIO
import sys

gui = tk.Tk()

gui.title('DLP Nanoevm GUI')


'''********************************************'''
'''****************** Setup *******************'''
'''********************************************'''

# Setup NIR sensor

SCAN_DONE = 0
VID = 0x0451
PID = 0x4200

setup(VID,PID)
time.sleep(1)


# Setup i/o for motor control

pos = 0
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

setup_motor()

'''********************************************'''
'''**************** Functions *****************'''
'''********************************************'''

def led():
    led_test(1)   # Start Test
    time.sleep(3)
    led_test(0)   # Stop Test

def date():
    get_date()


def ver():
    get_ver()


def pga_gain():
    set_gain(gain.current())


def custom_config():
    set_scan_config(name.get(),start.get(),end.get(),repeat.get(), res.get())
    scan()


def default_config():
    set_active_config(0)
    scan()


def spectral_plot(df):
    # Plots the given spectral data frame

    df.plot(kind='line',x="wavelength",y="reflectance")
    plt.title('NIR Spectra')
    plt.xlabel('Wavelength')
    plt.ylabel('Reflectance')
    plt.show()


def spectral_scan():
    get_scan_config_id()    

    start_scan(0) 			# donot store in sd card
    
    results = get_results() 		# get scan results
    ref_scan = get_ref_data() 		# get reference values


    '''Convert the results into a dataframe'''
    
    values = {"wavelength":results["wavelength"],
              "intensity":results["intensity"],
              "reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[0:results["length"]]
    
    ''' Calculate Reflectance and absorption'''

    df.loc[df.intensity > 0, "reflectance"] = df['intensity']/df['reference'] #reflectance = sample/reference
    df['absorption'] = -(np.log10(df['reflectance']))                         #absorption = -log(reflectance)
     
    df.to_csv("spectral_data.csv")


def setup_motor():
    global pos
    print('Finding homing position')
    while GPIO.input(homing_pos) == GPIO.LOW:
        GPIO.output(motor_channel,half_step_seq[pos])
        pos = (pos + 1) & len(half_step_seq)
        time.sleep(0.005)
    print("homing pos @" + str(pos))

def motor_control():

    global SCAN_DONE
    global pos
   
    while SCAN_DONE == 0:
        print('motor running forward\n')
        for step in range(0,200):
            GPIO.output(motor_channel,half_step_seq[pos])
            #print(half_step_seq[pos])
            pos = (pos + 1) 
            if pos == 8:
                pos = 0
            time.sleep(0.005)

        print('motor running backwards\n')
        for step in range(0,200):
            GPIO.output(motor_channel,half_step_seq[pos])
            #print(half_step_seq[pos])
            pos = (pos - 1) 
            if pos == -1:
                pos = 7
            time.sleep(0.005)
  


def scan():
    global SCAN_DONE

    motor_start = threading.Thread(target=motor_control)
    scan_start = threading.Thread(target=spectral_scan)

    motor_start.start()
    scan_start.start()
    

    scan_start.join()
    SCAN_DONE = 1
    motor_start.join()
    SCAN_DONE = 0


'''********************************************'''
'''**************** GUI Setup *****************'''
'''********************************************'''


d = tk.Button(gui, text='Get Date', width=20, command=date)
l = tk.Button(gui, text='LED Test', width=20, command=led)
v = tk.Button(gui, text='Get Version', width=20, command=ver)
s = tk.Button(gui, text='Default Config scan', width=20,command=default_config)
c = tk.Button(gui, text='Custom Config scan', width=20, command=custom_config)




d.grid()
l.grid()
v.grid()
s.grid()

n = tk.StringVar()
gain = ttk.Combobox(gui,width = 20, textvariable = n)

gain['values'] = ('1','2','4','8','16','32','64')
gain.grid(column = 1, row = 5)
gain.current()

g = tk.Button(gui, text = "Set PGA Gain",width=20,command=pga_gain).grid(row=5,column = 0)

canvas = tk.Canvas(gui)
canvas.grid()
name = tk.Entry(gui)
canvas.create_window(300,120,window=name)
labeln = tk.Label(gui,text="Scan Name:")
canvas.create_window(100,120,window=labeln)

start = tk.Entry(gui)
canvas.create_window(300,140,window=start)
labels = tk.Label(gui,text="Start Wavelength nm:")
canvas.create_window(100,140,window=labels)

end = tk.Entry(gui)
canvas.create_window(300,160,window=end)
labele = tk.Label(gui,text="End Wavelength nm:")
canvas.create_window(100,160,window=labele)

repeat = tk.Entry(gui)
canvas.create_window(300,180,window=repeat)
labelr = tk.Label(gui,text="Num repeats:")
canvas.create_window(100,180,window=labelr)

res = tk.Entry(gui)
canvas.create_window(300,200,window=res)
labelre = tk.Label(gui,text="Resolution:")
canvas.create_window(100,200,window=labelre)


c.grid()

gui.mainloop()



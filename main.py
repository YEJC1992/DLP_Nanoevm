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

SCAN_DONE = 0
VID = 0x0451
PID = 0x4200

gui = tk.Tk()

gui.title('DLP Nanoevm GUI')

# Setup NIR sensor
setup(VID,PID)
#time.sleep(0.5)

# Setup i/o for motor control
motor_channel = (29,31,33,35)
homing_pos = 36
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(motor_channel, GPIO.OUT)
GPIO.setup(homing_pos, GPIO.IN)

''''''''''''''''''
''' Functions '''
''''''''''''''''''

def led():
    '''temp function for getting gpio input'''
    #led_test(1)   # Start Test
    #time.sleep(3)
    #led_test(0)   # Stop Test
    print(GPIO.input(homing_pos))


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
    
    ''' Calculate Relectance and absorption'''

    df.loc[df.intensity > 0, "reflectance"] = df['intensity']/df['reference'] #reflectance = sample/reference
    df['absorption'] = -(np.log10(df['reflectance']))                         #absorption = -log(reflectance)
     
    df.to_csv("spectral_data.csv")


def motor_control():

    global SCAN_DONE
    print('motor running\n')

    while SCAN_DONE == 0:
        GPIO.output(motor_channel,(GPIO.HIGH,GPIO.LOW,GPIO.LOW,GPIO.HIGH))
        sleep(0.02)
        GPIO.output(motor_channel,(GPIO.HIGH,GPIO.HIGH,GPIO.LOW,GPIO.LOW))
        sleep(0.02)
        GPIO.output(motor_channel,(GPIO.LOW,GPIO.HIGH,GPIO.HIGH,GPIO.LOW))
        sleep(0.02)
        GPIO.output(motor_channel,(GPIO.LOW,GPIO.LOW,GPIO.HIGH,GPIO.HIGH))
        sleep(0.02)


def scan():
    global SCAN_DONE

    motor_start = threading.Thread(target=motor_control)
    scan_start = threading.Thread(target=spectral_scan)

    motor_start.start()
    scan_start.start()
    

    scan_start.join()
    SCAN_DONE = 1
    motor_start.join()



d = tk.Button(gui, text='Get Date', width=20, command=date)
l = tk.Button(gui, text='LED Test', width=20, command=led)
v = tk.Button(gui, text='Get Version', width=20, command=ver)
c = tk.Button(gui, text='Custom Config scan', width=20, command=custom_config)
s = tk.Button(gui, text='Default Config scan', width=20,command=default_config)

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

'''
pattern = tk.Entry(gui)
canvas.create_window(300,220,window=pattern)
labelp = tk.Label(gui,text="Num patterns:")
canvas.create_window(100,220,window=labelp)
'''

c.grid()

gui.mainloop()



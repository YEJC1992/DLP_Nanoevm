#!/usr/bin/env python3.6

import hid
import time
from commands import *
from usb_comm import *
import tkinter as tk
import math
import matplotlib.pyplot as plt

VID = 0x0451
PID = 0x4200

gui = tk.Tk()

gui.title('DLP Nanoevm GUI')

setup(VID,PID)
time.sleep(1)

def led():
    led_test(1)   # Start Test
    time.sleep(3)
    led_test(0)   # Stop Test

def date():
    get_date()

def custom_config():

    set_scan_config()
    scan()

def default_config():
    set_active_config(0)
    scan()

def scan():

    get_scan_config_id()
  

    start_scan(0) # donot store in sd card

    results = get_results() # of scanData


    time.sleep(1)
    
    ref_scan = get_ref_data()
    
    #plot data

    # Plot wavelenght vs intensity
    x = results["wavelength"]
    y = results["intensity"]
    z = ref_scan["intensity"]
    #!!!clean up results, why do we get -ve values??
    wl = []
    itn = []   
    rs = []
    absb = []

    for i in range(0,results["length"]):
        if (y[i] > 0):
            itn.append(y[i])
            rs.append(z[i])
            wl.append(x[i]) 
            if z[i]/y[i] > 0:
                absorbance = math.log(z[i]/y[i])
                absb.append(absorbance)

    plt.plot(wl,itn,'b')
    plt.xlabel("wavelength")
    plt.ylabel("absorbance")
    plt.show()

d = tk.Button(gui, text='Get Date', width=20, command=date)
l = tk.Button(gui, text='LED Test', width=20, command=led)
c = tk.Button(gui, text='Custom Config scan', width=20, command=custom_config)
s = tk.Button(gui, text='Default Config scan', width=20, command=default_config)
d.grid()
l.grid()
c.grid()
s.grid()
gui.mainloop()



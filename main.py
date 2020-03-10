#!/usr/bin/env python2.7

import hid
import time
from commands import *
from usb_comm import *
import Tkinter as tk
import math

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
    get_data()

def scan():
    get_scan_config_id()
    set_active_config(0)


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
s = tk.Button(gui, text='Scan'    , width=20, command=scan)
d.grid()
l.grid()
s.grid()
gui.mainloop()



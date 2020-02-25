#!/usr/bin/env python2.7

import hid
import time
from commands import *
from usb_comm import *
import Tkinter as tk


VID = 0x0451
PID = 0x4200

gui = tk.Tk()

gui.title('DLP Nanoevm GUI')

setup(VID,PID)
time.sleep(1)

def led():
    led_test(1)
    time.sleep(3)
    led_test(0)

def date():
    get_data()

def scan():
    get_scan_config_id()
    set_active_config(0)


    start_scan(0) # donot store in sd card

    results = get_results() # of scanData


    time.sleep(1)

    get_ref_data()

    #plot data

    # Plot wavelenght vs intensity
    x = results["wavelength"]
    y = results["intensity"]
  
    #clean up results, why do we get random large values??
    wl = []
    itn = []   
    for i in range(0,results["length"]):
        if ((y[i] < 9999) & (y[i] > -10000)):
            wl.append(x[i])
            itn.append(y[i])
        
        

    plt.plot(wl,itn)
    plt.xlabel("wavelength")
    plt.ylabel("intensity")
    plt.show()


d = tk.Button(gui, text='Get Date', width=20, command=date)
l = tk.Button(gui, text='LED Test', width=20, command=led)
s = tk.Button(gui, text='Scan'    , width=20, command=scan)
d.grid()
l.grid()
s.grid()
gui.mainloop()



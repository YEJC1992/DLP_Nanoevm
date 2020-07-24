#!/usr/bin/env python3.6

import hid
import time
from commands import *
from usb_comm import *
import tkinter as tk
import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

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
    set_active_config(2)
    scan()

def spectral_plot(df):

    df.plot(kind='line',x="wavelength",y="reflectance")
    plt.title('NIR Spectra')
    plt.xlabel('Wavelength')
    plt.ylabel('Absorption')
    plt.show()

def scan():

    get_scan_config_id()

    start_scan(0) # donot store in sd card

    results = get_results() # get scan results

    ref_scan = get_ref_data() # get reference values



    # Convert the results into a dataframe

    values = {"wavelength":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[(df[['reference','intensity']] > 0).all(axis=1)] # drop values of 0
    df['absorption'] = np.log10(df['reference']/df['intensity']) #need to get rid of negative values in ref?
    df['reflectance'] =1/(10**(df['absorption']))  #check formula
    spectral_plot(df) # Plot wavelength vs intensity
    df.to_csv("spectral_data.csv")


d = tk.Button(gui, text='Get Date', width=20, command=date)
l = tk.Button(gui, text='LED Test', width=20, command=led)
c = tk.Button(gui, text='Custom Config scan', width=20, command=custom_config)
s = tk.Button(gui, text='Default Config scan', width=20, command=default_config)
d.grid()
l.grid()
c.grid()
s.grid()
gui.mainloop()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 11:35:50 2021

@author: rajesh
"""



import os
from datetime import datetime


import pandas as pd
import numpy as np
import hid
import time
from commands import *
from usb_comm import *
import math
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


VID = 0x0451
PID = 0x4200



setup(VID,PID)
time.sleep(1)
app = FastAPI(title='NIR Spectroscopy')
df=pd.DataFrame()
def scan(parent,child,res):

    get_scan_config_id()    

    start_scan(0) # donot store in sd card
    
    results = get_results() # get scan results
    ref_scan = get_ref_data() # get reference values

    # Convert the results into a dataframe
    
    values = {"Wavelength (nm)":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[0:results["length"]]
    df.loc[df.intensity > 0, "reflectance"] = df['intensity']/df['reference'] #reflectance = sample/reference
    df['absorption'] = -(np.log10(df['reflectance']))#absorption = -log(reflectance)
     
    df.to_csv("Referrence/"+parent+"/"+child+"/ref"+str(res)+".csv")
    df[df.columns[0]]=np.around(df[df.columns[0]])
    df[df.columns[1]]=np.around(df[df.columns[1]],decimals = 5)
    df=df.dropna()
    df=df[["Wavelength (nm)","absorption","reflectance"]]
    df=df[:444]
    df1=df.T.reset_index()
    df1.columns = np.arange(len(df1.columns))
    final_out=df.to_json(orient='records')
    final_out1=df1.to_json(orient='records')
      
    return {'table':final_out1,'graph':final_out}


@app.get("/scanSpectralData",tags=['Sensor Controller'])
   
def scan_config(parent: str, child: str, name: str,start: float,end: float, repeat: float, res: float):

    set_scan_config(name,start,end,repeat,res)
    res=scan(name,parent,child,res)
    return res
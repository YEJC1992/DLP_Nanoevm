
from flask import Flask, request,jsonify #import main Flask class and request object
import subprocess
import hid
import time
from commands import *
from usb_comm import *
#import Tkinter as tk
import pandas as pd
import math



app = Flask(__name__) #create the Flask app




@app.route('/postData',methods=['POST','GET'])
def sensor():

    set_active_config(0)
    get_scan_config_id()
    
    

    start_scan(0) # donot store in sd card
    
    results = get_results() # get scan results
    ref_scan = get_ref_data() # get reference values

    # Convert the results into a dataframe
    
    values = {"wavelength":results["wavelength"],"intensity":results["intensity"],"reference":ref_scan["intensity"]}
    df = pd.DataFrame(values)
    df = df[(df[['wavelength','intensity']] > 0).all(axis=1)].reset_index() # drop values of 0 or less
    df['reflectance'] = df['intensity']/df['reference'] #reflectance = sample/reference
    df['absorption'] = -(np.log10(df['reflectance']))#absorption = -log(reflectance)
    

    
    final_out=df.to_json(orient='records')
    return final_out




if __name__ == '__main__':
    a= 0x0451
    b = 0x4200


    setup(a,b)
    time.sleep(1)
    app.run(port=5000)

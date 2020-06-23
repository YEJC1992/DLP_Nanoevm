
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

    get_scan_config_id()
    set_active_config(0)


    start_scan(0) # donot store in sd card

    results = get_results() # of scanData
    print(results)


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
    
    final_results={'Wavelength':x,'Intensity':y,'Factory':z}

    df=pd.DataFrame(final_results)
    print(df)
    final_out=df.to_json(orient='records')
    return final_out




if __name__ == '__main__':
    a= 0x0451
    b = 0x4200


    #device_list = hid.enumerate(a,b)
    #h = hid.Device(a,b)
    #h = hid.device()
    #h.open(a,b)


    setup(a,b)
    time.sleep(1)
    app.run(port=5000)

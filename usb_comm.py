#!/usr/bin/env python2.7

import hid
import time
from ctypes import *
from commands import *
from scan import *
import matplotlib.pyplot as plt
import math


VID = 0x0451
PID = 0x4200
TIMEOUT = 1000
READ_FILE_SIZE = 0
FILE = []

def setup(VID,PID):
    device_list = hid.enumerate(VID,PID)
    print (device_list)
    


def send_info(cmd_name,cmd,ret_len):
     h.write(''.join(map(chr,cmd)))
     if ret_len != 0:
         data = h.read(ret_len)
         process_data(data,cmd_name)

def extract_flags(flag_byte):
    global FLG_STATUS
    FLG_STATUS["ERR"] = (ord(flag_byte) & 0x30) >> 4
    FLG_STATUS["R/W"] = (ord(flag_byte) & 0x80) >> 7
    FLG_STATUS["RDY"] = (ord(flag_byte) & 0x40) >> 6
    print(" R/W: " + str(FLG_STATUS["R/W"])  +
          " Rdy: " + str(FLG_STATUS["RDY"]) +
          " Err: " + str(FLG_STATUS["ERR"]) )
    return FLG_STATUS

def process_data(data,cmd_name):
    status = extract_flags(data[0])

    if status["ERR"] == 1:
        send_info(CMD_ERR_STAT[0],CMD_ERR_STAT[1:8],CMD_ERR_STAT[8])    #get error status
    elif status["R/W"] == 0 and len(data)>1:
        read_data_process(data[1:],cmd_name)
    elif status["R/W"] == 1:                      # read  transaction
        seq_no = ord(data[1])
        print("Seq_no: " + str(seq_no))
        length = ord(data[2]) + (ord(data[3]) << 8)
        print("Packet_Len: " + str(length))
        read_data_process(data[4:],cmd_name)
    else:
        print("\n")


def read_data_process(rd_data,cmd_name):

    if cmd_name == cmd.RED_FSZE:
        global READ_FILE_SIZE
        size = 0
        for i in range(len(rd_data)):
            size += ord(rd_data[i]) << (i*8)
        READ_FILE_SIZE = size
        print("READ FILE SIZE: " + str(READ_FILE_SIZE) + "\n")
    
    elif (cmd_name == cmd.CFG_APPY) or (cmd_name == cmd.ERR_STAT):
        for i in rd_data: 
            print(hex(ord(i)))

    elif cmd_name == cmd.GET_TDAT:
        print("{}-{}-{}  {}:{}:{}\n".format(ord(rd_data[2]),ord(rd_data[1]),
                                            ord(rd_data[0]),ord(rd_data[4]),
                                            ord(rd_data[5]),ord(rd_data[6])))

    elif cmd_name == cmd.LED_TEST:
        if ord(rd_data[0]) == 0:
            print("LED TEST PASSED\n")
        else:
            print("LED TEST FAIL\n")   

    elif cmd_name == cmd.NUM_CONF:
        print("NUM OF STORED SCAN CONFIGS: " + str(ord(rd_data[0])) + "\n")

    elif cmd_name == cmd.GET_SCON:
        print("ACTIVE SCAN CONFIG: " + str(ord(rd_data[0])) + "\n")

    elif cmd_name == cmd.DEV_STAT:
        print("Device Status: "+hex(ord(rd_data[0])) + "\n")

    elif cmd_name == cmd.SCN_TIME:
        time = 0
        for i in range(len(rd_data)):
           time += ord(rd_data[i]) << (i*8) 
        print("SCAN_TIME: " + str(time)+ "\n")
                                      



def read_burst_data(cmd_name,cmd,ret_len):
    global FILE 
    read_len = ret_len
    while len(FILE) < ret_len:
        h.write(''.join(map(chr,cmd))) 
        if read_len > 64:    
            data = h.read(64)
            read_len -= 64
        else:
            data = h.read(read_len)
            read_len = 0
        FILE.extend(data)
    process_data(FILE[0:4],cmd_name)
    for i in range(4):
        FILE.pop(0)
    f = open("scanresults.txt","w")
    for i in FILE:
        f.write(hex(ord(i)))
        f.write("\n")
    f.close()
    print("Data Fetched: " +str(len(FILE)))





setup(VID,PID)

h = hid.Device(VID,PID)
print("Product:  " + h.product +" Device:  " + h.manufacturer)
print("Serial Number:  " + str(h.serial) + "\n")

#Start LED Test
led_start = CMD_LED_TEST[1:8]
led_start.append(0x01)
send_info (CMD_LED_TEST[0], led_start, CMD_LED_TEST[8])  #start led Test

#Get Date and Time
send_info (CMD_GET_TDAT[0], CMD_GET_TDAT[1:8], CMD_GET_TDAT[8]) # Get time and date


#Stop LED Test
led_stop = CMD_LED_TEST[1:8]
led_stop.append(0x00)
send_info (CMD_LED_TEST[0], led_stop, CMD_LED_TEST[8])


#Send Scan Config

serial_scan_config = set_config()
serial_scan_config.insert(0,0x7C)
serial_scan_config.insert(0,0x0)


buf_len = len(serial_scan_config)
i = 0
j = 0
ret_len = 0
while buf_len != 0:

    data=[]
    data = CMD_CFG_APPY[1:8]
    data[2] = i
    if (j+58) < len(serial_scan_config):
        data.extend(serial_scan_config[j:j+58])
        buf_len = buf_len - 58
    else:
        data.extend(serial_scan_config[j:])
        buf_len = 0
        ret_len = 4+1
    send_info(CMD_CFG_APPY[0], data, ret_len)
    i += 1
    j += 58



# Scan Data
"""
send_info (CMD_NUM_CONF[0], CMD_NUM_CONF[1:8], CMD_NUM_CONF[8])
send_info (CMD_GET_SCON[0], CMD_GET_SCON[1:8], CMD_GET_SCON[8])

set_scan_config = CMD_SET_SCON[1:8]
set_scan_config.append(0x00)             # Select config 1
send_info (CMD_SET_SCON[0], set_scan_config, CMD_SET_SCON[8])

send_info (CMD_GET_SCON[0], CMD_GET_SCON[1:8], CMD_GET_SCON[8])


"""
#Scan Time
send_info (CMD_SCN_TIME[0], CMD_SCN_TIME[1:8], CMD_SCN_TIME[8]) 

#Start Scan

start_scan = CMD_STR_SCAN[1:8]
start_scan.append(0x00)
send_info (CMD_STR_SCAN[0], start_scan, CMD_STR_SCAN[8])

#Delay
time.sleep(3)

#Device Status
send_info (CMD_DEV_STAT[0], CMD_DEV_STAT[1:8], CMD_DEV_STAT[8]) 

# get file size of scan data
read_file_size = CMD_RED_FSZE[1:8]
read_file_size.append(0x00)   
print(read_file_size)
send_info (CMD_RED_FSZE[0], read_file_size, CMD_RED_FSZE[8])   

# Read scan data
read_burst_data (CMD_RED_FDAT[0], CMD_RED_FDAT[1:8], READ_FILE_SIZE+4) 

# Interpret Results
results = scan_interpret(FILE)





# Plot wavelenght vs intensity
x = results["wavelength"]
y = results["intensity"]

plt.plot(x,y)

plt.xlabel("wavelength")
plt.ylabel("intensity")

plt.show()


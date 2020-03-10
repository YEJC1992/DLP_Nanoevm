#!/usr/bin/env python2.7

import hid
import time
from ctypes import *
from commands import *
from scan import *
import matplotlib.pyplot as plt
import math


TIMEOUT = 1000
READ_FILE_SIZE = 0
FILE = []
h = 0
scanresults =scanResults()

#Open Devices
def setup(VID,PID):
    global h

    device_list = hid.enumerate(VID,PID)
    print (device_list)
    h = hid.Device(VID,PID)
    print("Product:  " + h.product +" Device:  " + h.manufacturer)
    print("Serial Number:  " + str(h.serial) + "\n")
    
#Sends commands to device and waits for read data back from device
def send_info(cmd_name,cmd,ret_len):
     global h

     h.write(''.join(map(chr,cmd)))
     time.sleep(0.01)
     if ret_len != 0:
         data = h.read(ret_len)
         process_data(data,cmd_name)

#Decodes the Flag byte
def extract_flags(flag_byte):
    global FLG_STATUS

    FLG_STATUS["ERR"] = (ord(flag_byte) & 0x30) >> 4
    FLG_STATUS["R/W"] = (ord(flag_byte) & 0x80) >> 7
    FLG_STATUS["RDY"] = (ord(flag_byte) & 0x40) >> 6
    print("R/W: " + str(FLG_STATUS["R/W"]) +
          " Rdy: " + str(FLG_STATUS["RDY"]) +
          " Err: " + str(FLG_STATUS["ERR"]) )
    return FLG_STATUS

#Decodes read message from device
def process_data(data,cmd_name):

    status = extract_flags(data[0])

    if status["ERR"] == 1:
        #get error status
        send_info(CMD_ERR_STAT[0],CMD_ERR_STAT[1:8],CMD_ERR_STAT[8])
        #Clear the error status
        #send_info(CMD_ERR_CLER[0],CMD_ERR_CLER[1:8],CMD_ERR_CLER[8])
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

# cmd specific decode of data
def read_data_process(rd_data,cmd_name):

    if cmd_name == cmd.RED_FSZE or cmd_name == cmd.SIZ_LIST:
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
        stat = ord(rd_data[0])
        print("Device Status: "+str(stat) + "\n")
        return stat

    elif cmd_name == cmd.SCN_TIME:
        time = 0
        for i in range(len(rd_data)):
           time += ord(rd_data[i]) << (i*8)
        print("SCAN_TIME: " + str(time)+ "\n")

    elif cmd_name == cmd.INT_STAT:
        return ord(rd_data[0])

    elif cmd_name == cmd.TIV_VERS:
        for i in rd_data:
            print(hex(ord(i))) 

# Gets scan data
def read_burst_data(cmd_name,cmd,ret_len):
    
    global FILE
    global h
    rfile = []
    while len(rfile) < ret_len:
        h.write(''.join(map(chr,cmd)))
        time.sleep(0.03)
        data = 1
        extra = []
        while data:
            data = 0
            data = h.read(64,10)
            extra.extend(data)
        process_data(extra[0:4],cmd_name)
        rfile.extend(extra[4:])
    FILE = rfile
    return FILE







#Get Version Numbers
def get_ver():
    send_info (CMD_TIV_VERS[0], CMD_TIV_VERS[1:8], CMD_TIV_VERS[8]) 

#Get Date and Time
def get_data():
    send_info (CMD_GET_TDAT[0], CMD_GET_TDAT[1:8], CMD_GET_TDAT[8]) # Get time and date

#Start LED Test
def led_test(start):
    led_start = CMD_LED_TEST[1:8]
    led_start.append(start)
    send_info (CMD_LED_TEST[0], led_start, CMD_LED_TEST[8])  #start led Test


def get_scan_config_id():
    send_info (CMD_NUM_CONF[0], CMD_NUM_CONF[1:8], CMD_NUM_CONF[8]) #Num of scan config
    send_info (CMD_GET_SCON[0], CMD_GET_SCON[1:8], CMD_GET_SCON[8]) #Current active config

def set_active_config(index):
    set_scan_config = CMD_SET_SCON[1:8]
    set_scan_config.append(index)             # Select config by user
    send_info (CMD_SET_SCON[0], set_scan_config, CMD_SET_SCON[8])

    send_info (CMD_GET_SCON[0], CMD_GET_SCON[1:8], CMD_GET_SCON[8])

def start_scan(store_in_sd):
    #Scan Time
    send_info (CMD_SCN_TIME[0], CMD_SCN_TIME[1:8], CMD_SCN_TIME[8])

    #Start Scan
    start_scan = CMD_STR_SCAN[1:8]
    start_scan.append(store_in_sd)
    send_info (CMD_STR_SCAN[0], start_scan, CMD_STR_SCAN[8])

    #Device Status
    send_info (CMD_DEV_STAT[0], CMD_DEV_STAT[1:8], CMD_DEV_STAT[8])     
    time.sleep(3) #scan every 3 sec
    send_info (CMD_DEV_STAT[0], CMD_DEV_STAT[1:8], CMD_DEV_STAT[8])
    

def read_data(type):
    # get file size of  data
    read_file_size = CMD_RED_FSZE[1:8]
    read_file_size.append(type)
    send_info (CMD_RED_FSZE[0], read_file_size, CMD_RED_FSZE[8])

    # Read  data
    Data = read_burst_data (CMD_RED_FDAT[0], CMD_RED_FDAT[1:8],READ_FILE_SIZE+4)

    return Data

def get_results():
    global scanresults
    scanData = read_data(0)
  
    f1 = open("scanResultsraw.txt",'w')
    for i in scanData:
        f1.write(i)
    f1.close()

    # Interpret Results
    scanresults = scan_interpret(scanData)
   
    results = unpack_fields(scanresults)

    f1 = open("scanResults.txt",'w')
    for key in results:
        f1.write(key + " ")
        f1.write(str(results[key]))
        f1.write("\n\n")
    f1.close()
    
    return results

def get_ref_data():
    global scanresults
    refData   = read_data(2)
    refMatrix = read_data(3)

  
    scan_ref = scan_Ref_interpret(refData,refMatrix,scanresults)
    
    ref_results = unpack_ref(scan_ref)

    f1 = open("refResults.txt",'w')
    for key in ref_results:
        f1.write(key + " ")
        f1.write(str(ref_results[key]))
        f1.write("\n\n")
    f1.close()

    return ref_results


"""
#Send Scan Config

serial_scan_config = set_config()

buf_len = len(serial_scan_config)

i = 0
j = 0
ret_len = 0
while buf_len != 0:
    print(buf_len)
    data=[]
    data = CMD_CFG_APPY[1:8]
    data[2] = i
    data[3] = buf_len + 2
    if (j+57) < len(serial_scan_config):
        data.extend(serial_scan_config[j:j+57])
        buf_len = buf_len - 57
        j += 57
    else:
        data.extend(serial_scan_config[j:])
        buf_len = 0
        ret_len = 4+1
    print(data)
    send_info(CMD_CFG_APPY[0], data, ret_len)
    i += 1


"""

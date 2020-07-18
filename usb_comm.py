#!/usr/bin/env python3.6

import hid
import time
from ctypes import *
from commands import *
from scan import *
import matplotlib.pyplot as plt
import math
import datetime

TIMEOUT = 1000
READ_FILE_SIZE = 0
FILE = []
h = 0
scan_interpret_done = 0
scanresults =scanResults()
finalscanresults = scanResults()

#Open Devices
def setup(VID,PID):
    global h

    device_list = hid.enumerate(VID,PID)
    print (device_list)
    h = hid.device()
    h.open(VID,PID)
    #print("Product:  " + h.product +" Device:  " + h.manufacturer)
    #print("Serial Number:  " + str(h.serial) + "\n")
    set_date()

#Sends commands to device and waits for read data back from device
def send_info(cmd_name,cmd,ret_len):
     global h

     h.write(cmd)
     time.sleep(0.05)
     if ret_len != 0:
         data = h.read(ret_len)
         process_data(data,cmd_name)

#Decodes the Flag byte
def extract_flags(flag_byte):
    global FLG_STATUS

    FLG_STATUS["ERR"] = (flag_byte & 0x30) >> 4
    FLG_STATUS["R/W"] = (flag_byte & 0x80) >> 7
    FLG_STATUS["RDY"] = (flag_byte & 0x40) >> 6
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
        seq_no = data[1]
        print("Seq_no: " + str(seq_no))
        length = data[2] + (data[3] << 8)
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
            size += rd_data[i] << (i*8)
        READ_FILE_SIZE = size
        print("READ FILE SIZE: " + str(READ_FILE_SIZE) + "\n")

    elif (cmd_name == cmd.CFG_APPY) or (cmd_name == cmd.ERR_STAT):
        for i in rd_data:
            print(hex(i))

    elif cmd_name == cmd.GET_TDAT:
        print("{}-{}-{}  {}:{}:{}\n".format(rd_data[2],rd_data[1],
                                            rd_data[0],rd_data[4],
                                            rd_data[5],rd_data[6]))

    elif cmd_name == cmd.LED_TEST:
        if rd_data[0] == 0:
            print("LED TEST PASSED\n")
        else:
            print("LED TEST FAIL\n")

    elif cmd_name == cmd.NUM_CONF:
        print("NUM OF STORED SCAN CONFIGS: " + str(rd_data[0]) + "\n")

    elif cmd_name == cmd.GET_SCON:
        print("ACTIVE SCAN CONFIG: " + str(rd_data[0]) + "\n")

    elif cmd_name == cmd.DEV_STAT:
        stat = rd_data[0]
        print("Device Status: "+str(stat) + "\n")
        return stat

    elif cmd_name == cmd.SCN_TIME:
        time = 0
        for i in range(len(rd_data)):
           time += rd_data[i] << (i*8)
        print("SCAN_TIME: " + str(time)+ "\n")

    elif cmd_name == cmd.INT_STAT:
        global scan_interpret_done
        scan_interpret_done = rd_data[0]
        print("SCAN INTERPRET" +str(rd_data[0]))

    elif cmd_name == cmd.TIV_VERS:
        for i in rd_data:
            print(hex(i))


# Gets scan data
def read_burst_data(cmd_name,cmd,ret_len):

    global FILE
    global h
    rfile = []
    while len(rfile) < ret_len:
        h.write(cmd)
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


def write_file(filename,data):
    f1 = open(filename,'w')
    for key in data:
        f1.write(key + " ")
        f1.write(str(data[key]))
        f1.write("\n\n")
    f1.close()


#Get Version Numbers
def get_ver():
    send_info (CMD_TIV_VERS[0], CMD_TIV_VERS[1:8], CMD_TIV_VERS[8])

#Set Date and Time
def set_date():
    cur_tdat = CMD_SET_TDAT[1:8]
    now = datetime.datetime.now()
    year = int(str(now.year)[2:])
    weekday = datetime.date(now.year,now.month,now.day).weekday()
    cur_tdat.extend([year,now.month,now.day,weekday,now.hour,now.minute,now.second])

    send_info (CMD_SET_TDAT[0], cur_tdat, CMD_SET_TDAT[8]) # Set time and date

#Get Date and Time
def get_date():
    send_info (CMD_GET_TDAT[0], CMD_GET_TDAT[1:8], CMD_GET_TDAT[8]) # Get time and date

#Start LED Test
def led_test(start):
    led_start = CMD_LED_TEST[1:8]
    led_start.append(start)
    send_info (CMD_LED_TEST[0], led_start, CMD_LED_TEST[8])  #start led Test

# Get number of scan configs available and current active config
def get_scan_config_id():
    send_info (CMD_NUM_CONF[0], CMD_NUM_CONF[1:8], CMD_NUM_CONF[8]) #Num of scan config
    send_info (CMD_GET_SCON[0], CMD_GET_SCON[1:8], CMD_GET_SCON[8]) #Current active config


# Pick Active config
def set_active_config(index):
    set_scan_config = CMD_SET_SCON[1:8]
    set_scan_config.append(index)             # Select config by user
    send_info (CMD_SET_SCON[0], set_scan_config, CMD_SET_SCON[8])

    send_info (CMD_GET_SCON[0], CMD_GET_SCON[1:8], CMD_GET_SCON[8])

#Start the scan
def start_scan(store_in_sd):
    global scan_interpret_done

    #Scan Time
    send_info (CMD_SCN_TIME[0], CMD_SCN_TIME[1:8], CMD_SCN_TIME[8])



    #Start Scan
    start_scan = CMD_STR_SCAN[1:8]
    start_scan.append(store_in_sd)
    send_info (CMD_STR_SCAN[0], start_scan, CMD_STR_SCAN[8])

    #Device Status
    send_info (CMD_DEV_STAT[0], CMD_DEV_STAT[1:8], CMD_DEV_STAT[8])
    time.sleep(4) #scan every 4 sec
    send_info (CMD_DEV_STAT[0], CMD_DEV_STAT[1:8], CMD_DEV_STAT[8])




#read scan data
def read_data(type):
    # get file size of  data
    read_file_size = CMD_RED_FSZE[1:8]
    read_file_size.append(type)
    send_info (CMD_RED_FSZE[0], read_file_size, CMD_RED_FSZE[8])

    # Read  data
    Data = read_burst_data (CMD_RED_FDAT[0], CMD_RED_FDAT[1:8],READ_FILE_SIZE+4)

    return Data

#convert scan raw data to python dict
def get_results():
    global scanresults
    global scan_interpret_done

    scanData = read_data(0)   # 0: scan_data, 8: scan_interpret_data

    # Interpret Results
    scanresults = scan_interpret(scanData,0)  # 0: interpret and format, 1: only format

    results = unpack_fields(scanresults)

    write_file("scanResults.txt",results) # write to text file

    #Scan Interpret
    send_info (CMD_STR_SINT[0], CMD_STR_SINT[1:8], CMD_STR_SINT[8])

    while scan_interpret_done != 1:
        send_info (CMD_INT_STAT[0], CMD_INT_STAT[1:8], CMD_INT_STAT[8])
    scan_interpret_done = 0

    scanInterpretData = read_data(8)  # 8: scan_interpret_data
    finalscanresults = scan_interpret(scanInterpretData,1,scanresults) # 1: only format

    results1 = unpack_ref(finalscanresults)

    write_file("finalscanResults.txt",results1)

    return results

#Get ref raw data
def get_ref_data():
    global finalscanresults
    global scanresults
    refData   = read_data(2)
    refMatrix = read_data(3)


    scan_ref = scan_Ref_interpret(refData,refMatrix,scanresults)

    ref_results = unpack_ref(scan_ref)

    write_file("refResults.txt",ref_results)

    return ref_results


#Set custom Scan Config
def set_scan_config():

    serial_scan_config = set_config()

    buf_len = len(serial_scan_config)
    data = []
    data = CMD_CFG_APPY[1:8]
    data[3] = buf_len + 2

    data.extend(serial_scan_config)
    send_info(CMD_CFG_APPY[0], data, CMD_CFG_APPY[8])

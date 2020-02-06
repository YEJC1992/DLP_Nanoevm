#!/usr/bin/env python2.7

import hid
import time
from ctypes import *
from commands import *


VID = 0x0451
PID = 0x4200
TIMEOUT = 1000

def setup(VID,PID):
    device_list = hid.enumerate(VID,PID)
    print (device_list)
    


def send_info(cmd_name,cmd,ret_len):
     h.write(''.join(map(chr,cmd)))
     data = h.read(ret_len)
     process_data(data,cmd_name)

def extract_flags(flag_byte):
    err = (ord(flag_byte) & 0x30) >> 4
    rw =  (ord(flag_byte) & 0x80) >> 7
    rdy = (ord(flag_byte) & 0x40) >> 6
    print("R/W: " + str(rw)  +
          " Rdy: " + str(rdy) +
          " Err: " + str(err) )
    return rw

def process_data(data,cmd_name):
    rw = extract_flags(data[0])

    if rw == 0 and len(data)>1:
        read_data_process(data[1:],cmd_name)
    else:                      # read  transaction
        seq_no = ord(data[1])
        print("Seq_no: " + str(seq_no))
        length = ord(data[2]) + (ord(data[3]) << 8)
        print("Packet_Len: " + str(length))
        read_data_process(data[4:],cmd_name)


def read_data_process(rd_data,cmd_name):

    if cmd_name == cmd.RED_FSZE:
        for i in len(rd_data):
            read_file_size += ord(rd_data[i]) << (i*8)
    elif cmd_name == cmd.GET_TDAT:
        print("{}-{}-{}  {}:{}:{}\n" . format(ord(rd_data[2]),ord(rd_data[1]),ord(rd_data[0]),
                                            ord(rd_data[4]),ord(rd_data[5]),ord(rd_data[6])))
    elif cmd_name == cmd.LED_TEST:
        if ord(rd_data[0]) == 0:
            print("LED TEST PASSED\n")
        else:
            print("LED TEST FAIL\n")                                            







setup(VID,PID)

h = hid.Device(VID,PID)
print("Product:  " + h.product +" Device:  " + h.manufacturer)
print("Serial Number:  " + str(h.serial) + "\n")

led_start = CMD_LED_TEST[1:8]
led_start.append(0x01)
send_info (CMD_LED_TEST[0], led_start, CMD_LED_TEST[8])  #start led Test

send_info (CMD_GET_TDAT[0], CMD_GET_TDAT[1:8], CMD_GET_TDAT[8]) # Get time and date
time.sleep(3)

led_stop = CMD_LED_TEST[1:8]
led_stop.append(0x00)
send_info (CMD_LED_TEST[0], led_stop, CMD_LED_TEST[8]) # Stop led test

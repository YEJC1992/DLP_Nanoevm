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
    global  h = hid.Device(VID,PID)
    print("Product:  " + h.product +" Device:  " + h.manufacturer)
    print("Serial Number:  " + str(h.serial))


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

    if rw == 0:
        for i in range(1,len(data)):
            print(hex(ord(data[i])))
    else:                      # read  transaction
        seq_no = ord(data[1])
        print("Seq_no: " + str(seq_no))
        length = ord(data[2]) + (ord(data[3]) << 8)
        print("Packet_Len: " + str(length))
        read_data_process(data[4:],cmd_name)


def read_data_process(data,cmd_name):

    if cmd_name == cmd.RED_FSZE:
        for i in len(data):
            read_file_size += ord(data[i]) << (i*8)
    elif cmd_name == cmd.GET_TDAT:
        print("{}-{}-{}  {}:{}:{}" . format(ord(data[2]),ord(data[1]),ord(data[0]),
                                            ord(data[4]),ord(data[5]),ord(data[6])))
    elif cmd_name == cmd.LED_TEST:
        if ord(data[0]) == 0:
            print("LED TEST PASSED")
        else:
            print("LED TEST FAIL")                                            







setup(VID,PID)

send_info (CMD_LED_TEST[0], CMD_LED_TEST[1:7].append(0x01), CMD_LED_TEST[8])  #start led Test
send_info (CMD_GET_TDAT[0], CMD_GET_TDAT[1:7], CMD_GET_TDAT[8]) # Get time and date
time.sleep(3)
print(CMD_LED_TEST)
send_info (CMD_LED_TEST[0], CMD_LED_TEST[1:7].append(0x00), CMD_LED_TEST[8])

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
     process_data(data)

def extract_flags(flag_byte):
    err = (ord(flag_byte) & 0x30) >> 4
    rw =  (ord(flag_byte) & 0x80) >> 7
    rdy = (ord(flag_byte) & 0x40) >> 6
    print("R/W: " + str(rw)  +
          " Rdy: " + str(rdy) +
          " Err: " + str(err) )
    return rw

def process_data(data):
    rw = extract_flags(data[0])

    if rw == 0 and len(data) > 1:
        print(hex(ord(data)))
    else:                      # read  transaction
        seq_no = ord(data[1])
        print("Seq_no: " + str(seq_no))
        length = ord(data[2]) + (ord(data[3]) << 8)
        print("Packet_Len: " + str(length))
        read_data_process(data[4:])








setup(VID,PID)

send_info (CMD_PRF_CSUM[0], CMD_PRF_CSUM[1:7], CMD_PRF_CSUM[8])

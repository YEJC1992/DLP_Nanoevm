#!/usr/bin/env python2.7

import hid
import time
from ctypes import *
from commands import *


VID = 0x0451
PID = 0x4200

TIMEOUT = 1000

scan_data_size = 0

data = [ ]
ver_cmd  =      [USB_HEADER,CMD_FLAGS_READ,SEQ_ZERO,0x02,0x00,CMD_TIVA_VER_CB,CMD_TIVA_VER_GB]
dat_cmd  =      [USB_HEADER,CMD_FLAGS_READ,SEQ_ZERO,0x02,0x00,0x0C,0x03]
ser_cmd  =      [USB_HEADER,CMD_FLAGS_READ,SEQ_ZERO,0x02,0x00,0x33,0x02]
led_test_start =[USB_HEADER,CMD_FLAGS_WRITE,SEQ_ZERO,0x03,0x00,0x0B,0x01,0x01]
led_test_stop  =[USB_HEADER,CMD_FLAGS_WRITE,SEQ_ZERO,0x03,0x00,0x0B,0x01,0x00]
start_scan     =[USB_HEADER,CMD_FLAGS_WRITE,SEQ_ZERO,0x03,0x00,0x18,0x02,0x00]
 
read_file_size =[USB_HEADER,CMD_FLAGS_READ,SEQ_ZERO,0x03,0x00,0x2D,0x00,0x00]
read_scan_data =[USB_HEADER,CMD_FLAGS_READ,SEQ_ZERO,0x02,0x00,0x2E,0x00]

device_list = hid.enumerate(VID,PID)
print (device_list)

h = hid.Device(VID,PID)

def send_info(cmd,ret_len):
     h.write(''.join(map(chr,cmd)))
     process_data(ret_len)


def process_data(ret_len):
     length = 0
     read_len = ret_len
     burst = False

     while (read_len != 0):
         print("READ_LEN: " + str(read_len))
         if read_len > 64:
             read_len -= 64
             data = h.read(64)
         else:
             data = h.read(read_len)
             read_len -= read_len
         print("\nData len: " + str(len(data)))
         for i in range(len(data)):
             if (i !=0 and rw == 0) or burst == True:         
                 print(hex(ord(data[i])))
             elif i == 0:
                 err = (ord(data[i]) & 0x30) >> 4
                 rw =  (ord(data[i]) & 0x80) >> 7
                 rdy = (ord(data[i]) & 0x40) >> 6
                 
                 print("R/W: " + str(rw)  +
                       " Rdy: " + str(rdy) +
                       " Err: " + str(err) )
             else:                             # read  transaction
                 if i == 1:
    	             seq_no = ord(data[i])
                     print("Seq_no: " + str(seq_no))
                 elif i == 2:
                     length += ord(data[i])
                 elif i == 3:
                     length += ord(data[i]) << 8
                     print("Packet_Len: " + str(length))
                     if len(data) != ret_len:
                         burst = True
                 else:
                     print(hex(ord(data[i]))) 
	


print("Product:  " + h.product +" Device:  " + h.manufacturer)
print("Serial Number:  " + str(h.serial))
    





send_info(led_test_start,2)                       # start led test  
#send_info(ver_cmd,CMD_TIVA_VER_OB+4)             # get version no
#print("\n") 
#send_info(dat_cmd,11)                            # get date
#print("\n") 
#send_info(ser_cmd,12)	                          # get serial no
#print("\n") 
#time.sleep(5)                                    # 10 sec delay

print ("Test #2\n")
send_info(led_test_stop,2)                        # stop led test

print ("Test #3\n")
send_info(start_scan,1)
time.sleep(5)

print ("Test #4\n")
send_info(read_file_size,8)
print("Test #5\n")
send_info(read_scan_data,512)


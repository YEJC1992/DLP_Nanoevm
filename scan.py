#!/usr/bin/env python2.7


import ctypes
import os


class scanConfigHead(ctypes.Structure):
    _fields_ = [
                ("scan_type", ctypes.c_uint8),
                ("scanConfigIndex", ctypes.c_uint16),
                ("ScanConfig_snum", ctypes.c_char * 8),
                ("config_name", ctypes.c_char * 40)
               ]


class scanConfigStub(ctypes.Structure):
    _fields_ = [
                ("wavelength_start_nm", ctypes.c_uint16),
                ("wavelength_end_nm", ctypes.c_uint16),
                ("width_px", ctypes.c_uint8),
                ("num_patterns", ctypes.c_uint16),
                ("num_repeats", ctypes.c_uint16)
               ]


class scanConfig(ctypes.Structure):
    _fields_ = [
                ("head",scanConfigHead),
                ("Stub",scanConfigStub)
               ]

class calibCoeffs(ctypes.Structure):
    _fields_  = [
                 ("ShiftVectorCoeffs",       ctypes.c_double *3),
                 ("PixelToWavelengthCoeffs", ctypes.c_double *3)
                ]

class slewScanSection(ctypes.Structure):
    _fields_ = [
                ("section_scan_type",ctypes.c_uint8),
                ("width_px", ctypes.c_uint8),
                ("wavelenght_start_nm",  ctypes.c_uint16),
                ("wavelenght_end_nm", ctypes.c_uint16),
                ("num_patterns", ctypes.c_uint16),
                ("exposure_time", ctypes.c_uint16)
              ]

class slewScanConfigHead(ctypes.Structure):
    _fields_ = [
                ("scan_type", ctypes.c_uint8),
                ("scanConfigIndex",ctypes.c_uint16),
                ("scanConfig_serial_number",ctypes.c_char * 8),
                ("config_name",ctypes.c_char*40),
                ("num_repeats",ctypes.c_uint16),
                ("num_sections",ctypes.c_uint8)
               ]

class slewScanConfig(ctypes.Structure):
    _fields_=[
              ("head",slewScanConfigHead),
              ("section", slewScanSection*5)
             ]

class scanResults(ctypes.Structure):

    _fields_ = [
                ("header_version",   ctypes.c_uint32),
                ("scan_name",        ctypes.c_char * 20),
                ("year",             ctypes.c_uint8),
                ("month",            ctypes.c_uint8),
                ("day",              ctypes.c_uint8),
                ("day_of_week",      ctypes.c_uint8),
                ("hour",             ctypes.c_uint8),
                ("minute",           ctypes.c_uint8),
                ("second",           ctypes.c_uint8),
                ("system_temp_100",  ctypes.c_uint16),
                ("detector_temp_100",ctypes.c_uint16),
                ("humidity_100",     ctypes.c_uint16),
                ("lamp_pd",          ctypes.c_uint16),
                ("scanDataIndex",    ctypes.c_uint32),
                ("calib_coeffs",     calibCoeffs),
                ("Serial_number",    ctypes.c_char *8),
                ("adc_data_length",  ctypes.c_uint16),
                ("black_ptrn_first", ctypes.c_uint8),
                ("black_ptrn_period",ctypes.c_uint8),
                ("pga",              ctypes.c_uint8),
                ("cfg",              slewScanConfig),
                ("wavelength",       ctypes.c_double * 864),
                ("intensity",        ctypes.c_int * 864),
                ("length",           ctypes.c_int)
               ]

dlp_nano_lib = ctypes.CDLL("src/libtest.dylib")
dlp_nano_lib.dlpspec_scan_interpret.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(scanResults)]
dlp_nano_lib.dlpspec_scan_read_configuration = [ctypes.c_void_p, ctypes.c_size_t]

def unpack_fields(input):

    dict = {}
    for field_name, field_type in input._fields_:
        try:
            dict[field_name] = unpack_fields(getattr(input, field_name))
        except Exception as error:
            value = getattr(input, field_name)
           
            if type(value) == type(bytes()):
                value = value.decode("utf-8")
            elif type(value) not in [type(int()), type(float), type(long())]:
                newval = []
                for i in value:
                    try:
                        newval.append(unpack_fields(i))
                    except Exception as error:
                        newval.append(i)
                value = newval
            dict[field_name] = value
    return dict

def scan_interpret(file):

    """while 1:
        byte = f.read(1)
        if not byte:
            break"""

    buffer =  ctypes.create_string_buffer(len(file))
  
    for counter, byte in enumerate(file):
        buffer[counter] = byte

    buffer_pointer = ctypes.pointer(buffer)

    size_number = ctypes.c_size_t(len(file))

    results = scanResults()

    res_pointer = ctypes.byref(results)

    err = dlp_nano_lib.dlpspec_scan_interpret(buffer_pointer,size_number,res_pointer)
    print(err)
    unpack = unpack_fields(results)
    f1 = open("formatted.txt",'w')
    for key in unpack:
        f1.write(key + " ")
        f1.write(str(unpack[key]))
        f1.write("\n\n")
    f1.close()   
    return unpack
    


    

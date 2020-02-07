import ctypes



NUM_SHIFT_VECTOR_COEFFS = 3
NUM_PIXEL_NM_COEFFS = 3


class calibCoeffs(ctypes.Structure):
    _fields_  = [
                 ("ShiftVectorCoeffs",       ctypes.c_double * NUM_SHIFT_VECTOR_COEFFS),
                 ("PixelToWavelengthCoeffs", ctypes.c_double * NUM_PIXEL_NM_COEFFS)
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

class slewScanConfig(ctypes.structure):
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
                ("cfg",              slewScanconfig),
                ("wavelength",       ctypes.c_double * 864),
                ("intensity",        ctypes.c_int * 864),
                ("length",           ctypes.c_int)
               ]

    

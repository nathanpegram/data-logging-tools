#!/usr/bin/python3

import smbus
import time
import sys
PASCO_ADDR = 0x28
MUX_ADDR = 0x70

#channels = [4,5,6,7]
channels = [5]
#registers
DEV_ID = 0x00
SENS_STS = 0x01
MEAS_RATE_H = 0x02
MEAS_RATE_L = 0x03
MEAS_CFG = 0x04
CO2PPM_H = 0x05
CO2PPM_L = 0x06
MEAS_STS = 0x07
ALARM_TYP = 0x08
ALARM_TH_H = 0x09
ALARM_TH_L = 0x0A
PRES_REF_H = 0x0B
PRES_REF_L = 0x0C
CALIB_REF_H = 0x0D
CALIB_REF_L = 0x0E
SENS_RST = 0x10

bus = smbus.SMBus(1)

try:
    reference_ppm = int(sys.argv[1])
except:
    reference_ppm = 400

def read_info():
    #read id
    device_id  = bus.read_i2c_block_data(PASCO_ADDR, DEV_ID, 1)
    sys.stderr.write(hex(device_id[0]))

    #read status
    status = bus.read_i2c_block_data(PASCO_ADDR, SNS_STS, 1)
    sys.stderr.write(hex(status[0]))

def start_forced_calibration():
    #idle mode
    bus.write_i2c_block_data(PASCO_ADDR, MEAS_CFG, [0x00])
    time.sleep(0.2)
    #set measurement rate to 10 s
    bus.write_i2c_block_data(PASCO_ADDR, 0x02, [0x00, 0x0A])
    time.sleep(0.2)
    #write calibration reference
    bus.write_i2c_block_data(PASCO_ADDR, CALIB_REF_H, [reference_ppm//256])
    time.sleep(0.2)
    bus.write_i2c_block_data(PASCO_ADDR, CALIB_REF_L, [reference_ppm%256])
    time.sleep(0.2)
    bus.write_i2c_block_data(PASCO_ADDR, MEAS_CFG, [0b1010])

def end_forced_calibration():
    #idle mode
    bus.write_i2c_block_data(PASCO_ADDR, MEAS_CFG, [0x00])
    time.sleep(0.2)
    bus.write_i2c_block_data(PASCO_ADDR, SENS_RST, [0xCF])

def initiate_single_shot():
    bus.write_i2c_block_data(PASCO_ADDR, MEAS_CFG, [0x01])

def read_measurement():
    while(True):
        try:
            measurement_status = bus.read_i2c_block_data(PASCO_ADDR, MEAS_STS, 1)
            time.sleep(0.1)
            if measurement_status[0] == 0x10:
                sys.stderr.write("reading value\r\n")
                value = bus.read_i2c_block_data(PASCO_ADDR, CO2PPM_H, 2)
                co2_concentration = value[0] * 256 + value[1]
                sys.stderr.write("%d ppm\r\n" % co2_concentration) 
                return co2_concentration
            else:
                sys.stderr.write('waiting\r\n')
        except Exception as e:
            sys.stderr.write(str(e))
            pass
        time.sleep(0.2)

for channel in channels:
    print("start calibration on channel %d" % channel)
    bus.write_byte(MUX_ADDR, 1<<channel)
    #time.sleep(0.05)
    start_forced_calibration()
    time.sleep(0.2)

for i in range(3):
    results = {}
    for channel in channels:
        print("read %d of 3 on channel %d" % (i+1, channel))
        bus.write_byte(MUX_ADDR, 1<<channel)
        time.sleep(0.2)
        results[channel] = read_measurement()
        time.sleep(0.2)

    sys.stderr.write(str(results) + '\r\n')

for channel in channels:
    print("end calibration on channel %d" % channel)
    bus.write_byte(MUX_ADDR, 1<<channel)
    #time.sleep(0.05)
    end_forced_calibration()
    time.sleep(0.2)

time.sleep(1.0)
print("measure again")

for channel in channels:
    bus.write_byte(MUX_ADDR, 1<<channel)
    #time.sleep(0.05)
    initiate_single_shot()
    time.sleep(0.2)

results = {}

for channel in channels:
    bus.write_byte(MUX_ADDR, 1<<channel)
    time.sleep(0.2)
    results[channel] = read_measurement()
    time.sleep(0.2)

sys.stderr.write(str(results) + '\r\n')

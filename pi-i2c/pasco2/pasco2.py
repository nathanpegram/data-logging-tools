#!/usr/bin/python3

import smbus
import time
import sys
PASCO_ADDR = 0x28
MUX_ADDR = 0x70
channels = [4,5,6,7]


bus = smbus.SMBus(1)

#read id
#device_id  = bus.read_i2c_block_data(ADDR, 0x00, 1)
#sys.stderr.write(hex(device_id[0]))

#read status
#status = bus.read_i2c_block_data(ADDR, 0x01, 1)
#sys.stderr.write(hex(status[0]))

#idle mode
#bus.write_i2c_block_data(ADDR, 0x04, [0x00])
#time.sleep(0.5)
#set measurement rate to 10 s
#bus.write_i2c_block_data(ADDR, 0x02, [0x00, 0x0A])

def initiate_single_shot():
    bus.write_i2c_block_data(PASCO_ADDR, 0x04, [0x01])

def read_measurement():
    while(True):
        try:
            measurement_status = bus.read_i2c_block_data(PASCO_ADDR, 0x07, 1)
            time.sleep(0.1)
            if measurement_status[0] == 0x10:
                sys.stderr.write("reading value\r\n")
                value = bus.read_i2c_block_data(PASCO_ADDR, 0x05, 2)
                co2_concentration = value[0] * 256 + value[1]
                sys.stderr.write("%d ppm\r\n" % co2_concentration ) 
                return co2_concentration
            else:
                sys.stderr.write('waiting\r\n')
        except Exception as e:
            sys.stderr.write(str(e))
            pass
        time.sleep(0.2)

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
fields = ",".join([f"co2_{k}={v}" for k, v in results.items()])
print( "weathering " + fields)

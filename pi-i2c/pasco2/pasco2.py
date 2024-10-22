#!/usr/bin/python

import smbus
import time
import sys
ADDR = 0x28

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

#continuous mode
bus.write_i2c_block_data(ADDR, 0x04, [0x01])
time.sleep(0.5)

co2_concentration = 0

while(True):
    try:
        measurement_status = bus.read_i2c_block_data(ADDR, 0x07, 1)
        time.sleep(0.1)
        sys.stderr.write(hex(measurement_status[0]))
        if measurement_status[0] == 0x10:
            sys.stderr.write("reading value\r\n")
            value = bus.read_i2c_block_data(ADDR, 0x05, 2)
            co2_concentration = value[0] * 256 + value[1]
            sys.stderr.write("%d ppm\r\n" % co2_concentration ) 
            break
        else:
            sys.stderr.write('waiting\r\n')
    except Exception, e:
        sys.stderr.write(str(e))
        pass
    time.sleep(2.0)

print "weathering co2=%.1f" % co2_concentration

#!/usr/bin/python

import smbus
import time
ADDR1 = 0x4A
ADDR2 = 0x4B

bus = smbus.SMBus(1)

def read(addr):
    bus.write_i2c_block_data(addr, 0x2C, [0x06])
    time.sleep(0.5)
    data = bus.read_i2c_block_data(addr, 0x00, 2)
    temp = data[0] * 256 + data[1]
    cTemp = -45 + 175 * temp / 65535.0
    return cTemp


#print "stf_vestfrost_test temp1=%.2f,temp2=%.2f" % (read(ADDR1),read(ADDR2))
print "stf_vestfrost_test temp2=%.2f" % (read(ADDR1))

#!/usr/bin/python
import serial

p = serial.Serial('/dev/ttyUSB0', 56000,timeout=10.0)
p.readline()
line = p.readline().strip()
print line
p.close()

#!/usr/bin/python
import serial

p = serial.Serial('/dev/ttyUSB0', 56000,timeout=10.0)
p.readline()
line = p.readline().strip()
line = line.replace('],',':')
line = line.replace('[','')
line = line.replace(']','')
sensors = line.split(':')
fields = []
for sensor in sensors:
    (id,value,token) = sensor.split(',')
    fields.append( "%s=%s" %(id.strip(),value.strip()))

print "stf_vestfrost_test " + ','.join(fields)
p.close()

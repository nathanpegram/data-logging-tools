#!/usr/bin/python
import smbus
import time


MUX_ADDR = 0x70
channels = [5,7]

# Constants
AHT20_DEFAULT_ADDRESS = 0x38
sfe_aht20_reg_initialize = 0xBE
sfe_aht20_reg_measure = 0xAC
sfe_aht20_reg_reset = 0xBA

class AHT20:
    def __init__(self, i2c_bus):
        self._deviceAddress = AHT20_DEFAULT_ADDRESS
        self.bus = i2c_bus
        self.sensorData = {'temperature': 0, 'humidity': 0}
        self.sensorQueried = {'temperature': True, 'humidity': True}
        self.measurementStarted = False
    
    def begin(self):
        if not self.isConnected():
            return False

        time.sleep(0.04)  # Wait 40 ms after power-on
        if not self.isCalibrated():
            self.initialize()
            self.triggerMeasurement()
            time.sleep(0.075)

            counter = 0
            while self.isBusy():
                time.sleep(0.001)
                if counter > 100:
                    return False
                counter += 1

            if not self.isCalibrated():
                return False

        if not self.isCalibrated():
            return False

        self.sensorQueried['temperature'] = True
        self.sensorQueried['humidity'] = True

        return True

    def isConnected(self):
        try:
            self.bus.write_quick(self._deviceAddress)
            return True
        except IOError:
            time.sleep(0.02)
            try:
                self.bus.write_quick(self._deviceAddress)
                return True
            except IOError:
                return False

    def getStatus(self):
        try:
            return self.bus.read_byte(self._deviceAddress)
        except IOError:
            return 0

    def isCalibrated(self):
        return (self.getStatus() & (1 << 3)) != 0

    def isBusy(self):
        return (self.getStatus() & (1 << 7)) != 0

    def initialize(self):
        try:
            self.bus.write_i2c_block_data(self._deviceAddress, sfe_aht20_reg_initialize, [0x08, 0x00])
            return True
        except IOError:
            return False

    def triggerMeasurement(self):
        try:
            self.bus.write_i2c_block_data(self._deviceAddress, sfe_aht20_reg_measure, [0x33, 0x00])
            return True
        except IOError:
            return False

    def readData(self):
        try:
            data = self.bus.read_i2c_block_data(self._deviceAddress, 0x00, 6)
            incoming = (data[1] << 16) | (data[2] << 8) | (data[3])
            self.sensorData['humidity'] = incoming >> 4

            temp_raw = (data[3] << 16) | (data[4] << 8) | data[5]
            self.sensorData['temperature'] = temp_raw & 0xFFFFF

            self.sensorQueried['temperature'] = False
            self.sensorQueried['humidity'] = False
        except IOError:
            pass

    def available(self):
        if not self.measurementStarted:
            self.triggerMeasurement()
            self.measurementStarted = True
            return False

        if self.isBusy():
            return False

        self.readData()
        self.measurementStarted = False
        return True

    def softReset(self):
        try:
            self.bus.write_byte(self._deviceAddress, sfe_aht20_reg_reset)
            return True
        except IOError:
            return False

    def getTemperature(self):
        if self.sensorQueried['temperature']:
            self.triggerMeasurement()
            time.sleep(0.075)

            counter = 0
            while self.isBusy():
                time.sleep(0.001)
                if counter > 100:
                    return False
                counter += 1

            self.readData()

        tempCelsius = ((float(self.sensorData['temperature']) / 1048576) * 200) - 50
        self.sensorQueried['temperature'] = True
        return tempCelsius

    def getHumidity(self):
        if self.sensorQueried['humidity']:
            self.triggerMeasurement()
            time.sleep(0.075)

            counter = 0
            while self.isBusy():
                time.sleep(0.001)
                if counter > 100:
                    return False
                counter += 1

            self.readData()

        relHumidity = ((float(self.sensorData['humidity']) / 1048576) * 100)
        self.sensorQueried['humidity'] = True
        return relHumidity

# Main testing section
if __name__ == "__main__":
    bus = smbus.SMBus(1)
    sensor = AHT20(bus)
    fields = []

    for channel in channels:
        bus.write_byte(MUX_ADDR, 1<<channel)
        #time.sleep(0.05)
        sensor.begin()
        time.sleep(0.2)

    results = {}
    for channel in channels:
        bus.write_byte(MUX_ADDR, 1<<channel)
        time.sleep(0.2)
        fields.append("temperature_{channel}={value:.2f}".format(channel=channel, value=sensor.getTemperature()))
        fields.append("humdity_{channel}={value:.2f}".format(channel=channel, value=sensor.getHumidity()))
        time.sleep(0.2)

fields = ",".join(fields)
print( "weathering2 " + fields)




#!/bin/python
import time
import math
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

class MQ():

    CLK  = 23
    MISO = 21
    MOSI = 19
    CS   = 24
    mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

    SPI_PORT   = 0
    SPI_DEVICE = 0
    mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


    RL_VALUE = 5
    RO_CLEAN_AIR_FACTOR = 9.83


    CALIBARAION_SAMPLE_TIMES = 50
    CALIBRATION_SAMPLE_INTERVAL = 500

    READ_SAMPLE_INTERVAL = 50
    READ_SAMPLE_TIMES = 5


    GAS_LPG = 0
    GAS_CO = 1
    GAS_SMOKE = 2

    def __init__(self, Ro=3.46, analogPin=0):
        self.Ro = Ro
        self.MQ_PIN = analogPin

        self.LPGCurve = [2.3, 0.21, -0.47]
        self.COCurve = [2.3, 0.72, -0.34]
        self.SmokeCurve = [2.3, 0.53, -0.44]

        print("Calibrating...")
        self.Ro = self.MQCalibration(self.MQ_PIN)
        print("Calibration is done...\n")
        print("Ro=%f kohm" % self.Ro)

    def MQPercentage(self):
        val = {}
        read = self.MQRead(self.MQ_PIN)
        val["GAS_LPG"] = self.MQGetGasPercentage(read / self.Ro, self.GAS_LPG)
        val["CO"] = self.MQGetGasPercentage(read / self.Ro, self.GAS_CO)
        val["SMOKE"] = self.MQGetGasPercentage(read / self.Ro, self.GAS_SMOKE)
        return val

    def MQResistanceCalculation(self, raw_adc):
        return float(self.RL_VALUE * (1023.0 - raw_adc) / float(raw_adc));


    def MQCalibration(self, mq_pin):
        val = 0.0
        for i in range(self.CALIBARAION_SAMPLE_TIMES):
            val += self.MQResistanceCalculation(self.mcp.read_adc(mq_pin))
            time.sleep(self.CALIBRATION_SAMPLE_INTERVAL / 1000.0)

        val = val / self.CALIBARAION_SAMPLE_TIMES

        val = val / self.RO_CLEAN_AIR_FACTOR

        return val;


    def MQRead(self, mq_pin):
        rs = 0.0

        for i in range(self.READ_SAMPLE_TIMES):
            rs += self.MQResistanceCalculation(self.mcp.read_adc(mq_pin))
            time.sleep(self.READ_SAMPLE_INTERVAL / 1000.0)

        rs = rs / self.READ_SAMPLE_TIMES

        return rs


    def MQGetGasPercentage(self, rs_ro_ratio, gas_id):
        if (gas_id == self.GAS_LPG):
            return self.MQGetPercentage(rs_ro_ratio, self.LPGCurve)
        elif (gas_id == self.GAS_CO):
            return self.MQGetPercentage(rs_ro_ratio, self.COCurve)
        elif (gas_id == self.GAS_SMOKE):
            return self.MQGetPercentage(rs_ro_ratio, self.SmokeCurve)
        return 0


    def MQGetPercentage(self, rs_ro_ratio, pcurve):
        return (math.pow(10, (((math.log(rs_ro_ratio) - pcurve[1]) / pcurve[2]) + pcurve[0])))


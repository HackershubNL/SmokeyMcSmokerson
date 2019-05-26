#!/usr/bin/python
# coding: utf8

import time

import Adafruit_GPIO.SPI as SPI
import MAX6675.MAX6675 as MAX6675

CLK_pin = 21
DO_pin = 19

TC1_CS_pin = 6
TC2_CS_pin = 16
TC3_CS_pin = 12
TC4_CS_pin = 7
TC5_CS_pin = 24

TC1 = MAX6675.MAX6675(CLK_pin, TC1_CS_pin, DO_pin)
TC2 = MAX6675.MAX6675(CLK_pin, TC2_CS_pin, DO_pin)
TC3 = MAX6675.MAX6675(CLK_pin, TC3_CS_pin, DO_pin)
TC4 = MAX6675.MAX6675(CLK_pin, TC4_CS_pin, DO_pin)
TC5 = MAX6675.MAX6675(CLK_pin, TC5_CS_pin, DO_pin)

TC1_temp = TC1.readTempC()
time.sleep(1000)
TC2_temp = TC2.readTempC()
time.sleep(1000)
TC3_temp = TC3.readTempC()
time.sleep(1000)
TC4_temp = TC4.readTempC()
time.sleep(1000)
TC5_temp = TC5.readTempC()

print("Thermocouple 1 temperature: " + TC1_temp + " Celcius")
print("Thermocouple 2 temperature: " + TC2_temp + " Celcius")
print("Thermocouple 3 temperature: " + TC3_temp + " Celcius")
print("Thermocouple 4 temperature: " + TC4_temp + " Celcius")
print("Thermocouple 5 temperature: " + TC5_temp + " Celcius")
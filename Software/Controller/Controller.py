#!/usr/bin/python
# coding: utf8

import time
from simple_pid import PID
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import MAX6675.MAX6675 as MAX6675

#pins
CLK_pin = 21
DO_pin = 19
TC1_CS_pin = 6
TC2_CS_pin = 16
TC3_CS_pin = 12
TC4_CS_pin = 7
TC5_CS_pin = 24

#Fan variables
fan_frequency = 25000
fan_pin = 12

#Agressive Pid Tuning
aggressive_kp = 8
aggressive_ki = 0.2
aggressive_kd = 1

#Conservative Pid Tuning
conservative_kp = 2
conservative_ki = 0.1
conservative_kd = 0.5

#Target Temperature
barrel_target_temp = 125
meat_target_temp = 95

#Initialize Temperatures
TC5_temp_last = 25
temp_weighted_avg_last = 25

#Initialize Pid
pid = PID(Kp=aggressive_kp, Ki=aggressive_ki, Kd=aggressive_kd, setpoint=barrel_target_temp, sample_time=1, output_limits=(0, 100), auto_mode=True, proportional_on_measurement=False)

#Initialize Fan
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
fan = GPIO.PWM(fan_pin, fan_frequency)
fan.start(100)

#initialize thermocouples
TC1 = MAX6675.MAX6675(CLK_pin, TC1_CS_pin, DO_pin)
TC2 = MAX6675.MAX6675(CLK_pin, TC2_CS_pin, DO_pin)
TC3 = MAX6675.MAX6675(CLK_pin, TC3_CS_pin, DO_pin)
TC4 = MAX6675.MAX6675(CLK_pin, TC4_CS_pin, DO_pin)
TC5 = MAX6675.MAX6675(CLK_pin, TC5_CS_pin, DO_pin)


while(1):
    #read sensors
    TC1_temp = TC1.readTempC()
    time.sleep(100)
    TC2_temp = TC2.readTempC()
    time.sleep(100)
    TC3_temp = TC3.readTempC()
    time.sleep(100)
    TC4_temp = TC4.readTempC()
    time.sleep(100)
    TC5_temp = TC5.readTempC()

    #Calculations
    temp_weighted_avg = ((TC1_temp + TC2_temp + TC3_temp + TC4_temp) / 4) + 45 #From SmokeyTheBarrel: temperature compensation
    temp_weighted_avg_last=(2 * temp_weighted_avg_last + temp_weighted_avg) / 3
    temperature_gap = barrel_target_temp - temp_weighted_avg_last
    TC5_temp_last=(2 * TC5_temp_last + TC5_temp)/3;
    tempBelowTarget = meat_target_temp - TC5_temp_last

    #Meat has reached temperature
    if (tempBelowTarget < 1):
        print("Meat is ready")
        fan.stop()
        GPIO.cleanup()
        exit()

    #Barrel Target Temperature reached
    if (temperature_gap <= 0):
        fan.ChangeDutyCycle(0)

    #Small gap
    elif (temperature_gap > 0  and temperature_gap <= 10):
        #apply conservative tunings
        pid.Kp = conservative_kp
        pid.Ki = conservative_ki
        pid.Kd = conservative_kd

        pid_output = pid(temp_weighted_avg_last)
        fan.ChangeDutyCycle(pid_output)

    #Big gap
    else:
        #Set the tunings to aggresive
        pid.Kp = aggressive_kp
        pid.Ki = aggressive_ki
        pid.Kd = aggressive_kd

        pid_output = pid(temp_weighted_avg_last)
        fan.ChangeDutyCycle(pid_output)

    #sleep for a second
    time.sleep(1000)
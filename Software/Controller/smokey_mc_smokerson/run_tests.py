import time
from simple_pid import PID
import globals
import MAX6675
import Adafruit_GPIO as GPIO

try:
    platform = GPIO.Platform.platform_detect()
    assert(platform == 1)
except:
    print('[+] Platform is not a Raspberry Pi, exiting...')
    exit()


def test_thermocouples():
    counter = 0
    print("[+] Testing Thermocouples")

    CLK_pin = config['pin_outs']['thermocouple_clk']
    DO_pin = config['pin_outs']['thermocouple_do']
    TC1_CS_pin = config['pin_outs']['thermocouple_1_cs']
    TC2_CS_pin = config['pin_outs']['thermocouple_2_cs']
    TC3_CS_pin = config['pin_outs']['thermocouple_3_cs']
    TC4_CS_pin = config['pin_outs']['thermocouple_4_cs']
    TC5_CS_pin = config['pin_outs']['thermocouple_5_cs']

    TC1 = MAX6675.MAX6675(CLK_pin, TC1_CS_pin, DO_pin)
    TC2 = MAX6675.MAX6675(CLK_pin, TC2_CS_pin, DO_pin)
    TC3 = MAX6675.MAX6675(CLK_pin, TC3_CS_pin, DO_pin)
    TC4 = MAX6675.MAX6675(CLK_pin, TC4_CS_pin, DO_pin)
    TC5 = MAX6675.MAX6675(CLK_pin, TC5_CS_pin, DO_pin)

    while (counter != 5):

        TC1_temp = TC1.readTempC()
        print("Thermocouple 1 temperature: " + TC1_temp + " Celcius")
        time.sleep(1000)
        TC2_temp = TC2.readTempC()
        print("Thermocouple 2 temperature: " + TC2_temp + " Celcius")
        time.sleep(1000)
        TC3_temp = TC3.readTempC()
        print("Thermocouple 3 temperature: " + TC3_temp + " Celcius")
        time.sleep(1000)
        TC4_temp = TC4.readTempC()
        print("Thermocouple 4 temperature: " + TC4_temp + " Celcius")
        time.sleep(1000)
        TC5_temp = TC5.readTempC()
        print("Thermocouple 5 temperature: " + TC5_temp + " Celcius")
        print("")
        print("-----")
        print("")
        counter += 1


def test_fan():
    print("[+] Starting Fan Test")
    fan1_frequency = 25000
    fan1_pin = config['pin_outs']['fan_1']
    fan2_frequency = 25000
    fan2_pin = config['pin_outs']['fan_2']

    pwm = GPIO.PWM.get_platform_pwm()

    pwm.start(fan1_pin, globals.fan_speed, fan1_frequency)
    if(fan2_pin) :
        pwm.start(fan2_pin, globals.fan_speed, fan2_frequency)

    while(globals.fan_speed != 100):
        print("[+] Fan Speed at {}%".format(globals.fan_speed))
        time.sleep(1)
        globals.fan_speed += 1
        pwm.set_duty_cycle(fan1_pin, globals.fan_speed)
        if (fan2_pin):
            pwm.set_duty_cycle(fan2_pin, globals.fan_speed)

    pwm.set_duty_cycle(fan1_pin, 0)
    if (fan2_pin):
        pwm.set_duty_cycle(fan2_pin, 0)

    
if __name__ == "__main__":
    print("[+] Running hardware tests...")
    test_thermocouples()
    test_fan()
    print("[+] Finished running hardware tests")
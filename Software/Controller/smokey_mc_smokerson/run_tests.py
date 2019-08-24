import time
import globals
import MAX6675
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.PWM as PWMLib

try:
    platform = GPIO.Platform.platform_detect()
    assert(platform == 1)
except:
    print('[+] Platform is not a Raspberry Pi, exiting...')
    exit()

config = globals.config

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
        print("Thermocouple 1 temperature: {} Celcius".format(TC1_temp))
        time.sleep(2)
        TC2_temp = TC2.readTempC()
        print("Thermocouple 2 temperature: {} Celcius".format(TC2_temp))
        time.sleep(2)
        TC3_temp = TC3.readTempC()
        print("Thermocouple 3 temperature: {} Celcius".format(TC3_temp))
        time.sleep(2)
        TC4_temp = TC4.readTempC()
        print("Thermocouple 4 temperature: {} Celcius".format(TC4_temp))
        time.sleep(2)
        TC5_temp = TC5.readTempC()
        print("Thermocouple 5 temperature: {} Celcius".format(TC5_temp))
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

    pwm = PWMLib.get_platform_pwm()

    pwm.start(fan1_pin, globals.fan_speed, fan1_frequency)
    if(fan2_pin) :
        pwm.start(fan2_pin, globals.fan_speed, fan2_frequency)

    while(globals.fan_speed != 100):
        print("[+] Fan Speed at {}%".format(globals.fan_speed))
        time.sleep(5)
        globals.fan_speed += 10
        pwm.set_duty_cycle(fan1_pin, globals.fan_speed)
        if (fan2_pin):
            pwm.set_duty_cycle(fan2_pin, globals.fan_speed)

    pwm.stop(fan1_pin)
    if (fan2_pin):
        pwm.stop(fan2_pin)

    
if __name__ == "__main__":
    print("[+] Running hardware tests...")
    test_thermocouples()
    test_fan()
    print("[+] Finished running hardware tests")
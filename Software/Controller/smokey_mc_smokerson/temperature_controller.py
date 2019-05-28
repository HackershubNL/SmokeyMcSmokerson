import time
from simple_pid import PID
import globals

try:
    import RPi.GPIO as GPIO
    import Adafruit_GPIO.SPI as SPI
    import MAX6675.MAX6675 as MAX6675
    simulated_mode = False
except:
    simulated_mode = True
    print("Couldn't load GPIO libraries, running in simulated mode")

config = globals.config

#pins
CLK_pin = config['pin_outs']['thermocouple_clk']
DO_pin = config['pin_outs']['thermocouple_do']
TC1_CS_pin = config['pin_outs']['thermocouple_1_cs']
TC2_CS_pin = config['pin_outs']['thermocouple_2_cs']
TC3_CS_pin = config['pin_outs']['thermocouple_3_cs']
TC4_CS_pin = config['pin_outs']['thermocouple_4_cs']
TC5_CS_pin = config['pin_outs']['thermocouple_5_cs']

#Fan variables
fan1_frequency = 25000
fan1_pin = config['pin_outs']['fan_1']
fan2_frequency = 25000
fan2_pin = config['pin_outs']['fan_2']

#Agressive Pid Tuning
aggressive_kp = config['pid_tunings']['aggressive']['kp']
aggressive_ki = config['pid_tunings']['aggressive']['ki']
aggressive_kd = config['pid_tunings']['aggressive']['kd']

#Conservative Pid Tuning
conservative_kp = config['pid_tunings']['conservative']['kp']
conservative_ki = config['pid_tunings']['conservative']['ki']
conservative_kd = config['pid_tunings']['conservative']['kd']

def set_fan_speed(fan_speed):
    if (simulated_mode == False):
        fan1.ChangeDutyCycle(fan_speed)
        if (fan2):
            fan2.ChangeDutyCycle(fan_speed)

    globals.fan_speed = fan_speed

def run_temperature_controller():

    #Initialize Pid
    pid = PID(Kp=aggressive_kp, Ki=aggressive_ki, Kd=aggressive_kd, setpoint=globals.target_barrel_temp, output_limits=(0, 100), auto_mode=True, proportional_on_measurement=False)

    if (simulated_mode == False):
        #Initialize Fan
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(12, GPIO.OUT)
        fan1 = GPIO.PWM(fan1_pin, fan1_frequency)
        fan1.start(globals.fan_speed)

        if(fan2_pin) :
            fan2 = GPIO.PWM(fan1_pin, fan1_frequency)
            fan2.start(globals.fan_speed)

        #initialize thermocouples
        TC1 = MAX6675.MAX6675(CLK_pin, TC1_CS_pin, DO_pin)
        TC2 = MAX6675.MAX6675(CLK_pin, TC2_CS_pin, DO_pin)
        TC3 = MAX6675.MAX6675(CLK_pin, TC3_CS_pin, DO_pin)
        TC4 = MAX6675.MAX6675(CLK_pin, TC4_CS_pin, DO_pin)
        TC5 = MAX6675.MAX6675(CLK_pin, TC5_CS_pin, DO_pin)

        #Initialize Temperatures
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

    else:
        TC1_temp = 20
        TC2_temp = 20
        TC3_temp = 20
        TC4_temp = 20
        TC5_temp = 20

    TC5_temp_last = TC5_temp
    temp_weighted_avg_last = ((TC1_temp + TC2_temp + TC3_temp + TC4_temp) / 4)

    while(1):
        #update setpoint
        pid.setpoint = globals.target_barrel_temp

        #read sensors
        if (simulated_mode == False):
            TC1_temp = TC1.readTempC()
            time.sleep(100)
            TC2_temp = TC2.readTempC()
            time.sleep(100)
            TC3_temp = TC3.readTempC()
            time.sleep(100)
            TC4_temp = TC4.readTempC()
            time.sleep(100)
            TC5_temp = TC5.readTempC()
        else:
            if (globals.fan_speed > 80):
                TC1_temp += 0.8
                TC2_temp += 0.8
                TC3_temp += 0.8
                TC4_temp += 0.8

            if (globals.fan_speed > 60 and globals.fan_speed < 80):
                TC1_temp += 0.4
                TC2_temp += 0.4
                TC3_temp += 0.4
                TC4_temp += 0.4

            if (globals.fan_speed > 30 and globals.fan_speed < 60):
                TC1_temp += 0.2
                TC2_temp += 0.2
                TC3_temp += 0.2
                TC4_temp += 0.2

            if (globals.fan_speed < 30 and globals.fan_speed > 20):
                TC1_temp += 0.1
                TC2_temp += 0.1
                TC3_temp += 0.1
                TC4_temp += 0.1

            if (globals.fan_speed < 20 and globals.fan_speed > 10):
                TC1_temp -= 0.1
                TC2_temp -= 0.1
                TC3_temp -= 0.1
                TC4_temp -= 0.1

            if (globals.fan_speed < 10):
                TC1_temp -= 0.2
                TC2_temp -= 0.2
                TC3_temp -= 0.2
                TC4_temp -= 0.2

            TC5_temp += 0.01

        #Calculations
        temp_weighted_avg = ((TC1_temp + TC2_temp + TC3_temp + TC4_temp) / 4) # + 45 From SmokeyTheBarrel: temperature compensation
        temp_weighted_avg_last=(2 * temp_weighted_avg_last + temp_weighted_avg) / 3
        globals.current_barrel_temp = temp_weighted_avg_last
        temperature_gap = globals.target_barrel_temp - temp_weighted_avg_last
        globals.current_temp_gap = temperature_gap
        TC5_temp_last=(2 * TC5_temp_last + TC5_temp)/3;
        globals.current_meat_temp = TC5_temp_last
        tempBelowTarget = globals.target_meat_temp - TC5_temp_last

        #Small gap
        if (temperature_gap >= -10  and temperature_gap <= 10):

            if (globals.pid_profile_override == False):
                pid.Kp = conservative_kp
                pid.Ki = conservative_ki
                pid.Kd = conservative_kd
                globals.current_pid_kp = conservative_kp
                globals.current_pid_ki = conservative_ki
                globals.current_pid_kd = conservative_kd
                globals.current_pid_profile = "Conservative"

            else:
                globals.current_pid_kp = globals.manual_pid_kp
                globals.current_pid_ki = globals.manual_pid_ki
                globals.current_pid_kd = globals.manual_pid_kd

                pid.Kp = globals.manual_pid_kp
                pid.Ki = globals.manual_pid_ki
                pid.Kd = globals.manual_pid_kd

                globals.current_pid_profile = "Manual Override"

            pid_output = pid(temp_weighted_avg_last)
            set_fan_speed(pid_output)

        #Big gap
        else:

            if (globals.pid_profile_override == False):
                pid.Kp = aggressive_kp
                pid.Ki = aggressive_ki
                pid.Kd = aggressive_kd
                globals.current_pid_kp = aggressive_kp
                globals.current_pid_ki = aggressive_ki
                globals.current_pid_kd = aggressive_kd
                globals.current_pid_profile = "Aggressive"

            else:
                globals.current_pid_kp = globals.manual_pid_kp
                globals.current_pid_ki = globals.manual_pid_ki
                globals.current_pid_kd = globals.manual_pid_kd

                pid.Kp = globals.manual_pid_kp
                pid.Ki = globals.manual_pid_ki
                pid.Kd = globals.manual_pid_kd

                globals.current_pid_profile = "Manual Override"

            pid_output = pid(temp_weighted_avg_last)
            set_fan_speed(pid_output)

        #sleep for a second
        time.sleep(1)
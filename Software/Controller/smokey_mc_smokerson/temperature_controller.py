import time
from simple_pid import PID
import globals
import MAX6675
import Adafruit_GPIO as GPIO

try:
    platform = GPIO.Platform.platform_detect()
    assert(platform == 1)
    simulated_mode = False
except:
    simulated_mode = True
    globals.log('warning', "Temperature Controller - Platform is not a Raspberry Pi, running in simulated mode")

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

def set_fan_speed(pwm, fan_speed):
    if (simulated_mode == False):
        pwm.set_duty_cycle(fan1_pin, fan_speed)
        if (fan2_pin):
            pwm.set_duty_cycle(fan2_pin, fan_speed)

    globals.fan_speed = fan_speed

def simulate_temperature(simulated_temp):
    if (globals.fan_speed > 80):
        simulated_temp += 0.8

    if (globals.fan_speed > 60 and globals.fan_speed < 80):
        simulated_temp += 0.4

    if (globals.fan_speed > 30 and globals.fan_speed < 60):
        simulated_temp += 0.2

    if (globals.fan_speed < 30 and globals.fan_speed > 20):
        simulated_temp += 0.1

    if (globals.fan_speed < 20 and globals.fan_speed > 10):
        simulated_temp -= 0.1

    if (globals.fan_speed < 10):
        simulated_temp -= 0.2

    return simulated_temp

def set_pid_profile(pid, profile):

    if (globals.pid_profile_override == True):
        if (globals.current_pid_profile != "Manual Override"):
            globals.log('debug', 'Temperature Controller - Switched to PID Profile Manual Override')

        pid.Kp = globals.manual_pid_kp
        pid.Ki = globals.manual_pid_ki
        pid.Kd = globals.manual_pid_kd
            
        globals.current_pid_kp = globals.manual_pid_kp
        globals.current_pid_ki = globals.manual_pid_ki
        globals.current_pid_kd = globals.manual_pid_kd
        globals.current_pid_profile = "Manual Override"

    else:
        if (profile == 'aggressive'):
            if (globals.current_pid_profile != "Aggressive"):
                globals.log('debug', 'Temperature Controller - Switched to Aggressive PID profile')

            pid.Kp = aggressive_kp
            pid.Ki = aggressive_ki
            pid.Kd = aggressive_kd

            globals.current_pid_kp = aggressive_kp
            globals.current_pid_ki = aggressive_ki
            globals.current_pid_kd = aggressive_kd

            globals.current_pid_profile = "Aggressive"

        elif (profile == 'conservative'):
            if (globals.current_pid_profile != "Conservative"):
                globals.log('debug', 'Temperature Controller - Switched to Conservative PID profile')

            pid.Kp = conservative_kp
            pid.Ki = conservative_ki
            pid.Kd = conservative_kd

            globals.current_pid_kp = conservative_kp
            globals.current_pid_ki = conservative_ki
            globals.current_pid_kd = conservative_kd
            globals.current_pid_profile = "Conservative"

def run_temperature_controller():
    
    globals.log('info', 'Temperature Controller Started')

    #Initialize Pid
    pid = PID(Kp=aggressive_kp, Ki=aggressive_ki, Kd=aggressive_kd, setpoint=globals.target_barrel_temp, output_limits=(0, 100), auto_mode=True, proportional_on_measurement=False)

    if (simulated_mode == False):
        #Initialize Fan
        pwm = GPIO.PWM.get_platform_pwm()
        pwm.start(fan1_pin, globals.fan_speed, fan1_frequency)

        #if a second fan is defined, initialize that as well
        if(fan2_pin) :
            pwm.start(fan2_pin, globals.fan_speed, fan2_frequency)

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
        #if in simulated mode, set to 20 degrees baseline
        TC1_temp = 20
        TC2_temp = 20
        TC3_temp = 20
        TC4_temp = 20
        TC5_temp = 20

        #and create empty pwm object
        pwm = None

    #set variables used in the loop
    TC5_temp_last = TC5_temp
    temp_weighted_avg_last = ((TC1_temp + TC2_temp + TC3_temp + TC4_temp) / 4)

    #keep looping until instructed otherwise
    while(globals.stop_threads == False):
        #update setpoint if it differs
        if (pid.setpoint != globals.target_barrel_temp):
            globals.log('debug', 'Temperature Controller - PID Setpoint changed to: {}'.format(globals.target_barrel_temp))
            pid.setpoint = globals.target_barrel_temp

        #read sensors and if in simulated mode, calculate based on fan speed
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
            simulated_temp = simulate_temperature(TC1_temp)
            TC1_temp = TC2_temp = TC3_temp = TC4_temp = simulated_temp
            TC5_temp += 0.01

        #Calculations
        temp_weighted_avg = ((TC1_temp + TC2_temp + TC3_temp + TC4_temp) / 4) # + 45 From SmokeyTheBarrel: temperature compensation between outside and center of the barrel
        temp_weighted_avg_last=(2 * temp_weighted_avg_last + temp_weighted_avg) / 3
        globals.current_barrel_temp = temp_weighted_avg_last
        temperature_gap = globals.target_barrel_temp - temp_weighted_avg_last
        globals.current_temp_gap = temperature_gap

        TC5_temp_last=(2 * TC5_temp_last + TC5_temp)/3;
        globals.current_meat_temp = TC5_temp_last

        #use conservative pid profile for small temperature differences
        if (temperature_gap >= -10  and temperature_gap <= 10):
            set_pid_profile(pid, 'conservative')

        #otherwise use the aggresive profile
        else:
            set_pid_profile(pid, 'aggressive')

        #calculate new fan speed and set the fan speed
        pid_output = pid(temp_weighted_avg_last)
        set_fan_speed(pwm, pid_output)

        #sleep for a second
        time.sleep(1)

    if (simulated_mode == False):
        pwm.stop(fan1_pin)
        if (fan2_pin):
            pwm.stop(fan2_pin)

    globals.log('info', 'Temperature Controller Stopped')

if __name__ == "__main__":
    globals.log('error', 'Start the temperature controller with ./smokey_mc_smokerson.py')
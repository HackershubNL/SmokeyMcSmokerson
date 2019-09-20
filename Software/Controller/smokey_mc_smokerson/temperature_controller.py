import time
from simple_pid import PID
import globals
import MAX6675
import Adafruit_GPIO
import Adafruit_GPIO.PWM as PWM
import Adafruit_GPIO.GPIO as GPIO

try:
    platform = Adafruit_GPIO.Platform.platform_detect()
    assert(platform == 1)
    gpio_platform = GPIO.get_platform_gpio()
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
lid_switch_pin = config['pin_outs']['lid_switch']

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

def calibrate_temperature_offset(TC1, TC2, TC3, TC4, TC5, pwm):
    
    globals.log('debug', 'Temperature Calibration - Running fan at 10% for a minute')

    #Run the fan at 10% for a minute
    set_fan_speed(pwm, 10)
    time.sleep(60)

    globals.log('debug', 'Temperature Calibration - Soaking for 2 minutes')
    #Kill the fan and soak for 2 minutes
    set_fan_speed(pwm, 0)
    time.sleep(120)

    #Measure temps
    TC1_temp = TC1.readTempC()
    time.sleep(0.1)
    TC2_temp = TC2.readTempC()
    time.sleep(0.1)
    TC3_temp = TC3.readTempC()
    time.sleep(0.1)
    TC4_temp = TC4.readTempC()
    time.sleep(0.1)
    TC5_temp = TC5.readTempC()

    #Average out the outside sensors and calculate the difference
    outside_temp_average = ((TC1_temp + TC2_temp + TC3_temp + TC4_temp) / 4)
    temperature_offset = TC5_temp - outside_temp_average

    globals.log('info', 'Temperature Calibration - Average edge temperature: {}, Inside temperature: {}, Temperature offset set at: {}'.format(outside_temp_average, TC5_temp, temperature_offset))

    globals.calibrate_temperature = False

    return temperature_offset

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
    pid = PID(Kp=aggressive_kp, Ki=aggressive_ki, Kd=aggressive_kd, setpoint=globals.target_barrel_temp, output_limits=(0, 100), auto_mode=True, proportional_on_measurement=True) # See documentation on proportial on measurement flag

    #Initialize temperature offset
    temperature_offset = 0

    if (simulated_mode == False):
        #Initialize Fan
        pwm = PWM.get_platform_pwm()
        pwm.start(fan1_pin, globals.fan_speed, fan1_frequency)

        #if a second fan is defined, initialize that as well
        if(fan2_pin):
            pwm.start(fan2_pin, globals.fan_speed, fan2_frequency)

        #if lid switch pin is defined, set it up as input
        if(lid_switch_pin):
            gpio_platform.setup(lid_switch_pin, GPIO.IN)

        #initialize thermocouples
        TC1 = MAX6675.MAX6675(CLK_pin, TC1_CS_pin, DO_pin)
        TC2 = MAX6675.MAX6675(CLK_pin, TC2_CS_pin, DO_pin)
        TC3 = MAX6675.MAX6675(CLK_pin, TC3_CS_pin, DO_pin)
        TC4 = MAX6675.MAX6675(CLK_pin, TC4_CS_pin, DO_pin)
        TC5 = MAX6675.MAX6675(CLK_pin, TC5_CS_pin, DO_pin)

        #Initialize Temperatures
        #read sensors
        TC1_temp = TC1.readTempC()
        time.sleep(0.1)
        TC2_temp = TC2.readTempC()
        time.sleep(0.1)
        TC3_temp = TC3.readTempC()
        time.sleep(0.1)
        TC4_temp = TC4.readTempC()
        time.sleep(0.1)
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
            time.sleep(0.1)
            TC2_temp = TC2.readTempC()
            time.sleep(0.1)
            TC3_temp = TC3.readTempC()
            time.sleep(0.1)
            TC4_temp = TC4.readTempC()
            time.sleep(0.1)
            TC5_temp = TC5.readTempC()
        else:
            simulated_temp = simulate_temperature(TC1_temp)
            TC1_temp = TC2_temp = TC3_temp = TC4_temp = simulated_temp
            TC5_temp += 0.01

        #Calculations
        temp_weighted_avg = ((TC1_temp + TC2_temp + TC3_temp + TC4_temp) / 4) + temperature_offset # + 45 From SmokeyTheBarrel: temperature compensation between outside and center of the barrel
        temp_weighted_avg_last = (2 * temp_weighted_avg_last + temp_weighted_avg) / 3
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

        #if lid switch pin is defined, check its state. If the lid is open, kill the fan. If the pin is not defined calculate and set the speed as required
        if (lid_switch_pin):
            lid_state = gpio_platform.input(lid_switch_pin)

            if (lid_state == GPIO.HIGH):
                set_fan_speed(pwm, 0)
                globals.lid_open = True
            else:
                #calculate new fan speed and set the fan speed
                #only do the pid calculation when the lid is closed to prevent confusing the pid
                pid_output = pid(temp_weighted_avg_last)
                set_fan_speed(pwm, pid_output)
                globals.lid_open = False

        else:
            #calculate new fan speed and set the fan speed
            pid_output = pid(temp_weighted_avg_last)
            set_fan_speed(pwm, pid_output)

        #if the calibrate option has been selected
        if (globals.calibrate_temperature == True):

            globals.log('info', 'Temperature Calibration Started, stopping PID controller')

            #stop the pid
            pid.auto_mode = False

            #run the calibrate function
            temperature_offset = calibrate_temperature_offset(TC1, TC2, TC3, TC4, TC5, pwm)

            #reenable the pid
            pid.auto_mode = True
            globals.log('info', 'Temperature Calibration Finished, PID controller started')

        #sleep for a second
        time.sleep(1)

        ###### End of loop

    if (simulated_mode == False):
        pwm.stop(fan1_pin)
        if (fan2_pin):
            pwm.stop(fan2_pin)

    globals.log('info', 'Temperature Controller Stopped')

if __name__ == "__main__":
    globals.log('error', 'Start the temperature controller with ./smokey_mc_smokerson.py')
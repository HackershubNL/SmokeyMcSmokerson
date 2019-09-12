import blynklib
import time
import blynktimer
from datetime import datetime
from datetime import timedelta  
import globals
import os

#Set Globals
config = globals.config
cooking_dict = globals.cooking_dict

#Connect to Blynk server
if (config['blynk']['server'] == ''):
    blynk = blynklib.Blynk(config['blynk']['auth'])
    
else:
    blynk = blynklib.Blynk(config['blynk']['auth'], server=config['blynk']['server'], port=config['blynk']['server_port'])

#Initialize Blynk Timer
timer = blynktimer.Timer()

#Set base strings
recipe_info_string = "Recipe: {}\n\nMeat Type: {}\n\nSmoker Temperature: {}C\n\nTarget Meat Temperature: {}C\n\nCooking Time: {}\n\nInfo:\n{}"

#Set base variable
cooking_start = None
cooking_end = None
selected_profile = 1
init_loop = True
manual_timer_hours = 0
manual_timer_minutes = 0
timer_notification_sent = False
meat_ready_notification_sent = False

#Set Blynk Vpins
current_barrel_temp_vpin = config['blynk']['vpins']['current_barrel_temp']['pin']
current_meat_temp_vpin = config['blynk']['vpins']['current_meat_temp']['pin']
target_barrel_temp_vpin = config['blynk']['vpins']['target_barrel_temp']['pin']
target_meat_temp_vpin = config['blynk']['vpins']['target_meat_temp']['pin']
recipe_selector_vpin = config['blynk']['vpins']['recipe_selector']['pin']
status_text_vpin = config['blynk']['vpins']['status_text']['pin']
fan_speed_vpin = config['blynk']['vpins']['fan_speed']['pin']
recipe_description_vpin = config['blynk']['vpins']['recipe_description']['pin']
cook_time_remaining_vpin = config['blynk']['vpins']['cook_time_remaining']['pin']
manual_timer_hours_vpin = config['blynk']['vpins']['manual_timer_hours']['pin']
manual_timer_minutes_vpin = config['blynk']['vpins']['manual_timer_minutes']['pin']
confirm_recipe_vpin = config['blynk']['vpins']['confirm_recipe']['pin']
set_manual_timer_vpin = config['blynk']['vpins']['set_manual_timer']['pin']
mode_selector_vpin = config['blynk']['vpins']['mode_selector']['pin']
current_pid_kp_vpin = config['blynk']['vpins']['current_pid_kp']['pin']
current_pid_ki_vpin = config['blynk']['vpins']['current_pid_ki']['pin']
current_pid_kd_vpin = config['blynk']['vpins']['current_pid_kd']['pin']
current_pid_profile_vpin = config['blynk']['vpins']['current_pid_profile']['pin']
current_temp_gap_vpin = config['blynk']['vpins']['current_temp_gap']['pin']
manual_pid_kp_vpin = config['blynk']['vpins']['manual_pid_kp']['pin']
manual_pid_ki_vpin = config['blynk']['vpins']['manual_pid_ki']['pin']
manual_pid_kd_vpin = config['blynk']['vpins']['manual_pid_kd']['pin']
pid_profile_override_vpin = config['blynk']['vpins']['pid_profile_override']['pin']
system_shutdown_vpin = config['blynk']['vpins']['system_shutdown']['pin']

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    d["hours"] = str(d["hours"]).rjust(2, '0')
    d["minutes"] = str(d["minutes"]).rjust(2, '0')
    d["seconds"] = str(d["seconds"]).rjust(2, '0')
    return fmt.format(**d)
          
@timer.register(interval=5, run_once=False)
def update_ui():
    global timer_notification_sent
    global meat_ready_notification_sent

    blynk.virtual_write(current_barrel_temp_vpin, int(globals.current_barrel_temp))
    blynk.virtual_write(current_meat_temp_vpin, int(globals.current_meat_temp))
    blynk.virtual_write(fan_speed_vpin, globals.fan_speed)
    blynk.virtual_write(current_pid_kp_vpin, globals.current_pid_kp)
    blynk.virtual_write(current_pid_ki_vpin, globals.current_pid_ki)
    blynk.virtual_write(current_pid_kd_vpin, globals.current_pid_kd)
    blynk.virtual_write(current_pid_profile_vpin, globals.current_pid_profile)
    blynk.virtual_write(current_temp_gap_vpin, int(globals.current_temp_gap))

    if (cooking_end):
        time_delta = cooking_end - datetime.now()
        if (time_delta.days >= 0):
            message = strfdelta(time_delta, "{hours}:{minutes}:{seconds}")
        else:
            message = "Ready"
            if (timer_notification_sent == False):
                blynk.notify("Timer Expired")
                globals.log('debug', 'Blynk - Sent Timer Expired Push Notification')
                timer_notification_sent = True
        
        blynk.virtual_write(cook_time_remaining_vpin, message)


    if ((globals.target_meat_temp - globals.current_meat_temp) < 1 and meat_ready_notification_sent == False):
        blynk.notify("Food is Ready!")
        globals.log('debug', 'Blynk - Sent Food is Ready Push Notification')
        meat_ready_notification_sent = True

@blynk.handle_event('write V{}'.format(target_barrel_temp_vpin))
def write_target_barrel_temp_handler(pin, value):
    globals.log('debug', 'Blynk - Target Smoker Temperature Set to: {}'.format(value[0]))

    globals.target_barrel_temp = int(value[0])

@blynk.handle_event('write V{}'.format(target_meat_temp_vpin))
def write_target_meat_temp_handler(pin, value):
    global meat_ready_notification_sent
    globals.log('debug', 'Blynk - Target Meat Temperature Set to: {}'.format(value[0]))
    meat_ready_notification_sent = False
    globals.target_meat_temp = int(value[0])

@blynk.handle_event('write V{}'.format(recipe_selector_vpin))
def write_recipe_selector_handler(pin, value):
    global selected_profile
    index = value[0]
    selected_profile = index
    globals.log('debug', 'Blynk - Recipe Selector Changed to: {}'.format(value[0]))

    blynk.virtual_write(recipe_description_vpin, 'clr')
    blynk.virtual_write(recipe_description_vpin, recipe_info_string.format(cooking_dict[index]['name'], cooking_dict[index]['meat_type'], cooking_dict[index]['barrel_temp'], cooking_dict[index]['meat_temp'], time.strftime('%H:%M:%S', time.gmtime(cooking_dict[index]['cooking_time'])), cooking_dict[index]['description']))

@blynk.handle_event('write V{}'.format(confirm_recipe_vpin))
def write_confirm_recipe_handler(pin, value):
    global cooking_end
    global cooking_start
    global timer_notification_sent
    global meat_ready_notification_sent

    if(value[0] == "1"):
        index = selected_profile
        if (cooking_dict[index]['recipe_type'] == "cooking"):   
            blynk.virtual_write(target_barrel_temp_vpin, cooking_dict[index]['barrel_temp'])
            globals.target_barrel_temp = cooking_dict[index]['barrel_temp']
            blynk.virtual_write(target_meat_temp_vpin, cooking_dict[index]['meat_temp'])
            globals.target_meat_temp = cooking_dict[index]['meat_temp']
            blynk.virtual_write(status_text_vpin, 'Cooking: {} - {}'.format(cooking_dict[index]['meat_type'], cooking_dict[index]['name']))
            blynk.virtual_write(recipe_description_vpin, '\n\n[+] Auto Mode Set')
            blynk.virtual_write(mode_selector_vpin, '2')

            cooking_end = datetime.now() + timedelta(seconds=cooking_dict[index]['cooking_time'])
            cooking_start = datetime.now()
            timer_notification_sent = False
            meat_ready_notification_sent = False
            globals.log('debug', 'Blynk - Recipe Set')
        else:
            globals.log('debug', 'Blynk - Tried to set a recipe heading or preparation recipe')
    
@blynk.handle_event('write V{}'.format(manual_timer_hours_vpin))
def write_manual_timer_hours_handler(pin, value):
    global manual_timer_hours
    manual_timer_hours = int(value[0])
    globals.log('debug', 'Blynk - Manual Timer Hours Set to: {}'.format(value[0]))

@blynk.handle_event('write V{}'.format(manual_timer_minutes_vpin))
def write_manual_timer_minutes_handler(pin, value):
    global manual_timer_minutes
    manual_timer_minutes = int(value[0])
    globals.log('debug', 'Blynk - Manual Timer Minutes Set to: {}'.format(value[0]))

@blynk.handle_event('write V{}'.format(set_manual_timer_vpin))
def write_set_manual_timer_handler(pin, value):
    global cooking_end
    global cooking_start
    global timer_notification_sent

    if(value[0] == "1"):

        globals.log('debug', 'Blynk - Manual Timer Set')
        blynk.virtual_write(mode_selector_vpin, '1')
        blynk.virtual_write(status_text_vpin, 'Manual Mode')

        cooking_end = datetime.now() + timedelta(hours=manual_timer_hours, minutes=manual_timer_minutes)
        cooking_start = datetime.now()
        timer_notification_sent = False

@blynk.handle_event('write V{}'.format(manual_pid_kp_vpin))
def write_manual_pid_kp_val_handler(pin, value):
    globals.log('debug', 'Blynk - Manual PID Kp Set to: {}'.format(value[0]))
    globals.manual_pid_kp = float(value[0])

@blynk.handle_event('write V{}'.format(manual_pid_ki_vpin))
def write_manual_pid_ki_val_handler(pin, value):
    globals.log('debug', 'Blynk - Manual PID Ki Set to: {}'.format(value[0]))
    globals.manual_pid_ki = float(value[0])

@blynk.handle_event('write V{}'.format(manual_pid_kd_vpin))
def write_manual_pid_KD_val_handler(pin, value):
    globals.log('debug', 'Blynk - Manual PID Kd Set to: {}'.format(value[0]))
    globals.manual_pid_kd = float(value[0])

@blynk.handle_event('write V{}'.format(pid_profile_override_vpin))
def write_pid_override_handler(pin, value):
    if (int(value[0]) == 1):
        globals.pid_profile_override = True
        globals.log('debug', 'Blynk - PID Manual Overrride Turned On')

    elif (int(value[0]) == 0):
        globals.pid_profile_override = False
        globals.log('debug', 'Blynk - PID Manual Override Turned Off')

@blynk.handle_event('write V{}'.format(system_shutdown_vpin))
def write_system_shutdown_handler(pin, value):
    if(value[0] == "1"):
        globals.log('debug', 'Blynk - System Shutdown')
        os.system('sudo poweroff')

@blynk.handle_event("connect")
def connect_handler():
    menu_list = []
    for menu_item in cooking_dict:
        menu_list.append(cooking_dict[menu_item]['name'])
    menu_string = '"' + '","'.join(map(str, menu_list)) + '"'
    blynk.set_property(recipe_selector_vpin, "labels", *menu_list)
    blynk.notify("Received new menu")


def run_blynk():
    global init_loop
    globals.log('info', 'Blynk Interface Started')
    #keep looping until instructed otherwise
    while (globals.stop_threads == False):
        blynk.run()
        timer.run()
        if (init_loop == True):
            #on the first loop, set baseline variables
            blynk.virtual_write(status_text_vpin, 'Warming up')
            blynk.virtual_write(cook_time_remaining_vpin, '-')
            blynk.virtual_write(mode_selector_vpin, '1')
        
            blynk.virtual_write(manual_timer_hours_vpin, '0')
            blynk.virtual_write(manual_timer_minutes_vpin, '0')

            blynk.virtual_write(target_barrel_temp_vpin, globals.target_barrel_temp)
            blynk.virtual_write(target_meat_temp_vpin, globals.target_meat_temp)

            blynk.virtual_write(manual_pid_kp_vpin, globals.manual_pid_kp)
            blynk.virtual_write(manual_pid_ki_vpin, globals.manual_pid_ki)
            blynk.virtual_write(manual_pid_kd_vpin, globals.manual_pid_kd)
            blynk.virtual_write(pid_profile_override_vpin, 0)
            blynk.virtual_write(recipe_selector_vpin, 1)
            blynk.virtual_write(recipe_description_vpin, 'clr')

            init_loop = False

        
    globals.log('info', 'Blynk Interface Stopped')


if __name__ == "__main__":
    globals.log('error', 'Start the Blynk Interface with ./smokey_mc_smokerson.py')
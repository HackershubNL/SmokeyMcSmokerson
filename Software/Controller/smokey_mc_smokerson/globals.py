import json
from datetime import datetime

def log(type, message):
    cur_time = datetime.now().strftime("%H:%M:%S")
    if (type == "warning"):
        print_message = '[+] {} - Warning - {}'.format(cur_time, message)
    elif (type == "error"):
        print_message = '[+] {} - Error - {}'.format(cur_time, message)
    elif (type == "info"):
        print_message = '[+] {} - Info - {}'.format(cur_time, message)
    elif (type == "debug" and config['logging']['debug_mode'] == True):
        print_message = '[+] {} - Debug - {}'.format(cur_time, message)
    else:
        print_message = '[+] {} - {}'.format(cur_time, message)

    if (config['logging']['log_to_console'] == True):
        print(print_message)

    if (config['logging']['log_to_file'] == True):
        log_file = open(config['logging']['log_file_name'], 'a')
        log_file.write(print_message + '\n')
        log_file.close()

def load_config():
    global config
    config_file = open('config.json')
    config = json.load(config_file)
    config_file.close()

def load_recipes():
    global cooking_dict
    recipe_file = open('recipes.json')
    cooking_dict = json.load(recipe_file)
    recipe_file.close()

def initialize_globals():
    global target_barrel_temp
    global target_meat_temp
    global current_barrel_temp
    global current_meat_temp
    global fan_speed
    global current_pid_kp
    global current_pid_ki
    global current_pid_kd
    global current_pid_profile
    global current_temp_gap
    global pid_profile_override
    global manual_pid_kp
    global manual_pid_ki
    global manual_pid_kd
    global stop_threads

    target_barrel_temp = 120
    target_meat_temp = 80
    current_barrel_temp = 20
    current_meat_temp = 20
    fan_speed = 0
    current_pid_kp = 1
    current_pid_ki = 1
    current_pid_kd = 1
    current_pid_profile = "Aggressive"
    current_temp_gap = 0
    pid_profile_override = False
    manual_pid_kp = config['pid_tunings']['aggressive']['kp']
    manual_pid_ki = config['pid_tunings']['aggressive']['ki']
    manual_pid_kd = config['pid_tunings']['aggressive']['kd']
    stop_threads = False

load_config()
load_recipes()
initialize_globals()
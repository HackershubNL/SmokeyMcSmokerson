import json

def load_config():
    global config
    config_file = open('config.json')
    config = json.load(config_file)
    config_file.close()

def load_recipes():
    global cooking_dict
    recipe_file = open('recipes.txt')
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

    target_barrel_temp = 120
    target_meat_temp = 80
    current_barrel_temp = 20
    current_meat_temp = 20
    fan_speed = 10
    current_pid_kp = 1
    current_pid_ki = 1
    current_pid_kd = 1
    current_pid_profile = "Aggressive"
    current_temp_gap = 0
    pid_profile_override = False
    manual_pid_kp = config['pid_tunings']['aggressive']['kp']
    manual_pid_ki = config['pid_tunings']['aggressive']['ki']
    manual_pid_kd = config['pid_tunings']['aggressive']['kd']

load_config()
load_recipes()
initialize_globals()
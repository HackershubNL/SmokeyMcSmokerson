import globals
import blynk_interface
import temperature_controller
import blynktimer
import random
import threading
import time
import sys

def shutdown():
    print("[+] Shutting Down")
    sys.exit(0)

def main():
    print("[+] Starting Smokey Mc Smokerson")
    blynk_thread = threading.Thread(target=blynk_interface.run_blynk, daemon=True)
    blynk_thread.start()
    controller_thread = threading.Thread(target=temperature_controller.run_temperature_controller, daemon=True)
    controller_thread.start()
    
    while True:
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        shutdown()
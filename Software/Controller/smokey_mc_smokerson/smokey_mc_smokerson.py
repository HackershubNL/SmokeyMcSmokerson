import globals
import blynk_interface
import temperature_controller
import blynktimer
import random
import threading
import time
import sys
import signal

def shutdown(signum, frame):
    globals.log('info', 'Stopping Threads...')
    globals.stop_threads = True
    globals.log('info', 'Waiting for Threads to Finish...')
    while (threading.active_count() > 1):
        time.sleep(0.1)
    sys.exit(0)

def main():
    globals.log('info', 'Starting Smokey Mc Smokerson')
    blynk_thread = threading.Thread(target=blynk_interface.run_blynk)
    blynk_thread.start()
    controller_thread = threading.Thread(target=temperature_controller.run_temperature_controller)
    controller_thread.start()
    signal.signal(signal.SIGTERM, shutdown)
    globals.log('info', 'Smokey Mc Smokerson Started, you can stop it with Ctrl+C')
    
    while True:
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        shutdown(1,1)
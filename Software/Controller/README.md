# Smokey Mc Smokerson - Controller Software

## Introduction

Currently work in progress, this is conceptual code right now as the hardware has not been delivered yet. Simulated mode is built-in to show the usage.


## Running the thing

For full info check the wiki.

### Setup

Install dependencies with:  
`sudo bash ./setup.sh`

In `config.json` set your API key and optionally your Blynk server address. If the server address is an empty string, it will use the public Blynk Servers.

### Usage

Run the hardware tests with:  
`python3 ./smokey_mc_smokerson/run_tests.py`  
This will test the thermocouples and fan(s).

When using the setup script, it will install the controller as a service which starts on boot.  
To start and stop the service you can use:  
```
sudo /etc/init.d/smokey_service start
and
sudo /etc/init.d/smokey_service stop
```

Alternatively you can run it separately:  
`python3 ./smokey_mc_smokerson/smokey_mc_smokerson.py`  

The startup temperature values are located in `globals.py`, these can be changed using the Blynk app later on.

If it is run on anything but a Raspberry Pi, it will go into a simulated mode.
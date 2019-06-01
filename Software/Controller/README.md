# Smokey Mc Smokerson - Controller Software

## Introduction

Currently work in progress, this is conceptual code right now as the hardware has not been delivered yet. Simulated mode is built-in to show the usage.


## Running the thing

For full info check the wiki.

### Setup

Install dependencies with:  
`sudo bash ./setup.sh`

Rename `sample_config.json` to `config.json` and set your API key and optionally your Blynk server address. If the server address is an empty string, it will use the public Blynk Servers.

### Usage

Run the hardware tests with:  
`python ./smokey_mc_smokerson/smokey_mc_smokerson.py`  
This will test the thermocouples and fan(s).

Start the controller with:  
`python ./smokey_mc_smokerson/smokey_mc_smokerson.py`  

The startup temperature values are located in `globals.py`, these can be changed using the Blynk app later on.

If it is run on anything but a Raspberry Pi, it will go into a simulated mode.
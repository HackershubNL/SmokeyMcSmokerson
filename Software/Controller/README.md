# Smokey Mc Smokerson - Controller Software

## Introduction

Currently work in progress, this is conceptual code right now as the hardware has not been delivered yet. Simulated mode is built-in to show the usage.

## Running the thing

### Setup

Install dependencies with:  
`sudo bash ./setup.sh`

Rename `sample_config.json` to `config.json` and set your API key and optionally your Blynk server address. If the server address is an empty string, it will use the public Blynk Servers.

(Optional) Download Blynk server with:  
`sudo bash ./setup_blynk_server.sh`

### Usage

Run the tests with:  
`python ./run_tests.py`  
For now it only tests the thermocouples.

(Optional) Start the Blynk server with:  
`java -jar server-0.41.6-java8.jar -dataFolder /tmp/blynk`

Start the controller with:  
`python ./smokey_mc_smokerson/smokey_mc_smokerson.py`  

The startup temperature values are located in `globals.py`, these can be changed using the Blynk app later on. (Blynk code will we uploaded soon)  

If it is run on a PC (Raspberry Pi GPIO libs cannot be loaded), it will go into a simulated mode.
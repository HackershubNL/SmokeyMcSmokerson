# Smokey Mc Smokerson - Controller Software

## Introduction

Currently work in progress, this is conceptual code right now as the hardware has not been delivered yet.

## Running the thing

### Setup

Install dependencies with:  
`sudo bash ./setup.sh`

### Usage

Run the tests with:  
`python ./run_tests.py`  
For now it only tests the thermocouples.

Start the controller with:  
`python ./Controller.py`  
Currently it will only ramp up the temperature to 125 degrees celcius and hold. And will finish when the meat has reached 95 degrees.
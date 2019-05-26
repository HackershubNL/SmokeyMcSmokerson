# Smokey Mc Smokerson - Controller Hardware


## Intro

This is revision number one, already some improvement points have been identified such as using standard fan connectors instead of screw terminals and additional smoothing capacitors need to be included.

## Design Decisions

The SN74AHCT125N Buffer is added to level shift the PWM signal from 3.3v to 5v. This has been done for better compatibility with different fans. Certain ones seem to accept 3.3v PWM signal but most 12V fans seem to require a 5v signal.

Plans for the controller housing can be found in Hardware/Smoker.

Additional GPIO pins are available through the 6 pin header for future usage.

The fan which will be used is the Sanyo Denki 9GA0412P6G001*, this is chosen due to the high static pressure because it will need to blow through a hose and the airflow spreader.  
*https://nl.farnell.com/sanyo-denki/9ga0412p6g001/axial-fan-40mm-12vdc-14-8cfm-47dba/dp/2768815 

## Bill of Materials  

Farnell shopping cart csv is included but the following items are not on the list:  
- V7805-1000 Regulator (Farnell doesn't carry this item)
- Raspberry Pi + SD card (Assuming you have one)
- Thermocouple boards and probes, see link to Aliexpress below
- Fans

And some items have a minimum order quantity so you will get more than required.

### Main board

- 5x 5-pin female headers
- 2x 3-pin screw terminals 
- 1x 6-pin male header
- 1x 4-pin male header
- 1x 2-pin male header
- 1x 2-pin Molex Mini Fit Jr Header
- 1x 5.5mm Barrel Jack 
- 1x 14-pin DIP socket
- 1x 40-pin female GPIO header  
- 1x V7805-1000 Regulator, this is the 1A version, might need the 2A version (V7805-2000)
- 1x 10uF capacitor  
- 1x 22uF capacitor  
- 1x 220 ohm resistor  
- 1x SN74AHCT125N

### Raspberry Pi

- 1x Raspberry Pi Zero W  
- 1x 40-pin male GPIO header

### Control Panel

- 1x Adafruit LCD display with I2C board
- 1x Panel mount led indicator
- 1x Rocker Switch 
- 1x 2 pin Molex Mini Fit Jr Receptacle  
- 2x Molex Crimp Contacts  
- 2x female jumper wire soldered to led indicator  
- 4x female - female jumper wires for display to main board
- 8x 11mm M2.5 standoffs
- 8x M2.5 - 6mm screws
- 8x M2.5 nuts

### Sensors

- 5x MAX6675 Thermocouple boards with probe - https://nl.aliexpress.com/item/MAX6675-Module-K-Type-Thermocouple-Thermocouple-Senso-Temperature-Degrees-Module-for-arduino/32841448771.html

### Other

- 1 or 2 12V PWM fans (according to barbecue forums a single 10CFM fan should be sufficient)

# Hardware
- Grideye AMG8833
- Grideye MLX90640
- [PIR Sensor HC-SR501](http://www.datasheetcafe.com/hc-sr501-datasheet-detector/)
- ESP32
- ESP8266

## ESP8266
[Nice link](https://medium.com/@cgrant/using-the-esp8266-wifi-module-with-arduino-uno-publishing-to-thingspeak-99fc77122e82)

Refer to [ESP 8266 instruction set](ESP8266/esp8266_at_instruction_set_en.pdf) for commands

Here is an overview of the more important commands that we have used so far.

![](screenshots/esp8266&#32;instruction&#32;set&#32;overview.jpg)
- AT
  - get OK response if serial communication works
- AT+CWJAP="network-ssid","network-password"
  - for connecting to an access point
- AT+CWLAP
  - to get list of access points around

:warning: If you can't run any of the commands above try setting the mode of the ESP8266 by sending a message "AT+CWMODE_CUR=3"

If used as a standalone board, can wire to arduino and short the reset and ground pins on the arduino. Remember to remove the short if flashing arduino sketches.

# Install necessary packages 
```python
pip install -r requirements.txt
```

#### Matplotlib Visualization

> For Ubuntu WSL users, please [install XMING X server](https://sourceforge.net/projects/xming/) and run `export DISPLAY=:0` for the matplotlib visualization to work.

## Useful Resources
- [Arduino Delay vs Python Delay](https://arduino.stackexchange.com/questions/12808/handle-reading-timing-in-python-using-pyserial)
- [Pyserial API](https://arduino.stackexchange.com/questions/12808/handle-reading-timing-in-python-using-pyserial)
- [Resolving Lag in Matplotlib Realtime Visualization](https://bastibe.de/2013-05-30-speeding-up-matplotlib.html)
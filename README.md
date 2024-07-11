This is something i have been playing with for a little while now and I thought I'd put it out there to see if anyone else is interested in experimenting with it too! 

I'm calling this LRms (Long Range messaging system)

It's a pretty simple system which uses UART LoRa transcievers available from the company Reyax, in particular the RYLR993 Lite (with IPEX Antenna socket) and the RYLR998 (built in antenna) these tiny transceivers are capable of 100mW output and they simply use AT commands to configure them and to send and receive short messages over the air using LoRa, other youtubers have found the range of these devices to be extraordinary as we would expect from anything that uses LoRa

The devices are available from here:
RYLR 993 LITE (with antenna socket) https://amzn.to/3zDHwzR
RYLR 998 (built in Antenna) https://amzn.to/462SCKL

Store
https://mpowered247.com/

These devices run on 3.3V and can be powered directly from a Raspberry Pi or any other MCU that has 3.3V available. Once Vcc and GND is connected the only other pins that need to be connected are Rx and Tx serial pins. These are connected to the corresponding pins on the Rasperry Pi, I used the serial port ttyS0 which is the main UART on the Pi (there are sometimes timing issues with this port but I have found these devices to work well, probably because the data throughput is quite low)

I have written a few simple python scripts, please forgive me for any inefficient code or errors as I am not a coder and used ChatGPT to create a lot of it! 
These python scripts are available on my github:
https://github.com/RikomagicCloudsto/LRms

LRms-beaconmaster.py is a simple script that sends out a beacon at a defined interval (set in the script) the beacon text can be changed when the program is running by pressing B, the program will also monitor the UART port that the RYLR device is connected to and display incoming messages with a timestamp. the incoming messages are plain test and they contain the RSSI and Signal to Noise Ratio as well as the ID of the station that sent the message.

LRms-messenger.py is a program that allows you to send and receive messages at will. Python has a UART buffer which will hold the most recent messages. Press G to get the latest messages, press S to send a message (user can input text and press enter to send) There are no beacon features in this program.

LRms-repeater.py is a micro-python program for the Raspberry Pi Pico, you can easily install this to any Pico running micro-python firmware using Thonny to upload the micro-python script.
The program communicates with the RYLR module on the GPIO pins 0 and 1 and will listen for packets from nodes, if the packet includes the text flag "RPT" it will repeat broadcast the message.

All messages are sent as broadcast messages so all nodes will receive all messages, nodes will not receive RPT flagged messages intended for a repeater UNLESS they are a repeater.

As I say this is all work in progress and it is designed to encourage experimentation, fun and learning how to use these fascinating devices alongside simple but powerful scripting to achieve messaging and other tasks independent of the Internet.

The scripts will attempt to setup the Reyax LoRa modules each time they start. You can familiarise yourself with the AT command set for these modules by downloading the AT guide from the Reyax website here:

https://reyax.com//upload/products_download/download_file/LoRa_AT_Command_RYLR998_RYLR498_EN.pdf

NOTES ON ENCRYPTION
These modules do feature encryption which is enabled by way of an 8 digit hex password. LRms is not using encryption as it is meant to be a hobbyiest system. Any encryption should not be taken as competely secure without full control of the software/hardware used.

I hope you enjoy this and I looks forward to seeing you on my discord:
https://discord.com/invite/6hrAp8dFGb

import machine
import time
from machine import Pin

# Define GPIO pins
led = Pin(25, Pin.OUT)
gpio2 = Pin(2, Pin.OUT)  # Assuming GPIO 2 is available and not in use

# Initialize LED
led.value(1)

# Serial port configuration
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))

# Send AT commands to configure the RYLR993 or RYLR998

uart.write(b'AT+RESET\r\n')  # Reset Module
print("Reset RYLR Module Wait...")
time.sleep(2)
data = uart.readline().decode('utf-8').strip()
print(data)

uart.write(b'AT+OPMODE=10\r\n')  # Set RYLR993 to poprietary mode - not needed for RYLR998
print("Set RYLR993 to proprietary mode")
time.sleep(2)
data = uart.readline().decode('utf-8').strip()
print(data)
data = uart.readline().decode('utf-8').strip()
print(data)

uart.write(b'AT+RESET\r\n')  # Reset Module
print("Reset RYLR Module")
time.sleep(2)
data = uart.readline().decode('utf-8').strip()
print(data)

uart.write(b'AT+BAND=867500000\r\n') # Set LoRa frequency
print("Setting RF Frequency to 867.500MHZ")
time.sleep(1)
data = uart.readline().decode('utf-8').strip()
print(data)
data = uart.readline().decode('utf-8').strip()
print(data)

uart.write(b'AT+ADDRESS=1\r\n') # Set node ID
print("Setting Node ID to 1")
time.sleep(1)
data = uart.readline().decode('utf-8').strip()
print(data)
data = uart.readline().decode('utf-8').strip()
print(data)
data = uart.readline().decode('utf-8').strip()
print(data)

uart.write(b'AT+CRFOP=22\r\n')  # Set TX power
print("Setting TX power to 22dBm")
time.sleep(1)
data = uart.readline().decode('utf-8').strip()
print(data)
data = uart.readline().decode('utf-8').strip()
print(data)

uart.write(b'AT+PARAMETER=9,7,1,12\r\n') # Set LoRa parameters - see RYLR documentation
print("Setting LoRa Parameters for LRms")
time.sleep(1)
data = uart.readline().decode('utf-8').strip()
print(data)
data = uart.readline().decode('utf-8').strip()
print(data)
# Define your station ID
my_ID = "55"

# Continuous loop to read from serial port
while True:
    # Read data until a complete message is received or timeout occurs
    start_time = time.ticks_ms()
    received_data = b''
    while not received_data.endswith(b'\r\n'):
        new_data = uart.read()
        if new_data is not None:
            received_data += new_data
        # Check if timeout has occurred (5000 ms = 5 seconds)
        if time.ticks_diff(time.ticks_ms(), start_time) > 5000:
            break
    
    # Print received data
    print("Received:", received_data.decode().strip())
    led.value(1)
    time.sleep(1)
    led.value(0)
    
    # Check if received data contains "RPT"
    if b"RPT" in received_data:
        # Remove "RPT" from the received data
        received_data = received_data.replace(b"RPT", b"").strip()  # Remove leading and trailing spaces after removing "RPT"
        
        # Extract station ID
        station_ID = received_data.split(b"+RCV=")[1].split(b",")[0]
        
        # Extract message text
        message_text = received_data.split(b",")[2].strip()  # Remove leading and trailing spaces from message text
        
        # Count number of characters in message text
        num_characters = len(message_text)
        
        # Calculate total number of characters including station ID, "VIA", and my_ID
        total_characters = num_characters + len(station_ID) + len(b" ") + len(b"VIA") + len(my_ID.encode())
        
        # Assemble message to be sent
        send_message = "AT+SEND=0,{},{} {}VIA{}\r\n".format(total_characters, message_text.decode(), station_ID.decode(), my_ID)
        
        # Print message to be sent
        print("Sending:", send_message)
        
        # Turn on GPIO 2
#         gpio2.value(1)
        
        # Send message to serial port
        uart.write(send_message.encode())
        
        # Turn off GPIO 2
#         time.sleep(2)
#         gpio2.value(0)



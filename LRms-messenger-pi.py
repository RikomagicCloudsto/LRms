import RPi.GPIO as GPIO
import serial
import time
import sys

# Initialize GPIO
# GPIO.setmode(GPIO.BCM)
# BACKLIGHT_PIN = 42
# GPIO.setup(BACKLIGHT_PIN, GPIO.OUT)

# Initialize UART
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)

# Send AT commands to configure the RYLR993 or RYLR998

uart.write(b'AT+RESET\r\n')  # Reset Module
print("Reset RYLR Module Wait...")
time.sleep(2)
data = uart.readline().decode('utf-8').strip()
print(data)

uart.write(b'AT+OPMODE=1\r\n')  # Set RYLR993 to poprietary mode - not needed for RYLR998
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


def toggle_screen():
    if GPIO.input(BACKLIGHT_PIN):
        print("Turning screen off...")
        GPIO.output(BACKLIGHT_PIN, GPIO.LOW)
    else:
        print("Turning screen on...")
        GPIO.output(BACKLIGHT_PIN, GPIO.HIGH)

def parse_received_message(received_data):
    if "+RCV" in received_data:
        # Extract stationid, msgcontent, rssi, and snr from the received message
        data_parts = received_data.split(",")
        stationid = data_parts[0].split("=")[1]
        msgcontent = data_parts[2]
        rssi = data_parts[3]
        snr = data_parts[4]
        
        # Check if the message content contains "RPT", if yes, ignore the message
        if "RPT" in msgcontent:
            return

        # Print the formatted message
        print("-" * 45)
        print("Message from: {}".format(stationid))
        print("RSSI: {} SNR: {}".format(rssi, snr))
        print(msgcontent)
        print("-" * 45)

        # Check if the message content contains "ACK"
        # if "ACK" not in msgcontent:
        #     send_message_ack(stationid)

def send_message_ack(stationid):
    message = "ACK {}".format(stationid)
    message_length = len(message)
    message_to_send = "AT+SEND=0,{},{}\r\n".format(message_length, message)
    uart.write(message_to_send.encode())
    print("ACK sent!")
    time.sleep(1)  # Wait for 1 second before sending the next ACK

def get_messages():
    messages_received = False
    while uart.in_waiting > 0:
        received_data = uart.readline().decode().strip()
        messages_received = True
        parse_received_message(received_data)
    
    if not messages_received:
        print("There are no messages...")

def send_message():
    message = input("Enter your message: ")
    message_length = len(message)
    message_to_send = "AT+SEND=0,{},{}\r\n".format(message_length, message)
    uart.write(message_to_send.encode())
    print("Message sent!")

def get_battery_voltage():
    # This is a placeholder function. Replace it with actual ADC reading if available.
    # For demonstration purposes, we will return a dummy voltage value.
    voltage = 3.7  # Dummy value for battery voltage
    return voltage

def menu():
    while True:
        # Get battery voltage
        voltage = get_battery_voltage()

        # Print menu with battery voltage spaced 45 characters to the right
        print("\nLRms Messenger Menu:                           Battery: {:.2f} volts".format(voltage))
        print("1. Press G to get messages")
        print("2. Press S to send a message")
        print("3. Press Q to quit")

        choice = input("Enter your choice: ")

        if choice == "G" or choice == "g":
            get_messages()
        elif choice == "S" or choice == "s":
            send_message()
        elif choice == "B" or choice == "b":
            toggle_screen()
        elif choice == "Q" or choice == "q":
            print("Exiting program...")
            #GPIO.cleanup()  # Clean up GPIO
            sys.exit()  # Exit the program
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
       #GPIO.cleanup()
        sys.exit()

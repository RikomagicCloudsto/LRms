import serial
import threading
import time
import curses
from datetime import datetime

# Serial port configuration
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)

# Send AT commands to configure the RYLR993 or RYLR998

ser.write(b'AT+RESET\r\n')  # Reset Module
print("Reset RYLR Module Wait...")
time.sleep(2)
data = ser.readline().decode('utf-8').strip()
print(data)

ser.write(b'AT+OPMODE=1\r\n')  # Set RYLR993 to poprietary mode - not needed for RYLR998
print("Set RYLR993 to proprietary mode")
time.sleep(2)
data = ser.readline().decode('utf-8').strip()
print(data)
data = ser.readline().decode('utf-8').strip()
print(data)

ser.write(b'AT+RESET\r\n')  # Reset Module
print("Reset RYLR Module")
time.sleep(2)
data = ser.readline().decode('utf-8').strip()
print(data)

ser.write(b'AT+BAND=867500000\r\n') # Set LoRa frequency
print("Setting RF Frequency to 867.500MHZ")
time.sleep(1)
data = ser.readline().decode('utf-8').strip()
print(data)
data = ser.readline().decode('utf-8').strip()
print(data)

ser.write(b'AT+ADDRESS=1\r\n') # Set node ID
print("Setting Node ID to 1")
time.sleep(1)
data = ser.readline().decode('utf-8').strip()
print(data)
data = ser.readline().decode('utf-8').strip()
print(data)
data = ser.readline().decode('utf-8').strip()
print(data)

ser.write(b'AT+CRFOP=22\r\n')  # Set TX power
print("Setting TX power to 22dBm")
time.sleep(1)
data = ser.readline().decode('utf-8').strip()
print(data)
data = ser.readline().decode('utf-8').strip()
print(data)

ser.write(b'AT+PARAMETER=12,7,1,4\r\n') # Set LoRa parameters - see RYLR documentation
print("Setting LoRa Parameters for LRms")
time.sleep(1)
data = ser.readline().decode('utf-8').strip()
print(data)
data = ser.readline().decode('utf-8').strip()
print(data)

# Initialize curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
stdscr.clear()
stdscr.refresh()

# Define screen layout parameters
serial_lines = curses.LINES - 5  # Number of lines reserved for serial output, user input, and timestamps
menu_line = curses.LINES - 4  # Line number for the menu
input_line = curses.LINES - 2  # Line number for user input prompt

# Circular buffer for storing recent serial output lines with timestamps
output_buffer = []

# Global variables for user input
user_input = ""
user_input_chars = 0  # Initialize user_input_chars

# Flag to track whether the input field is active
input_active = False

# Function to read from serial port and update UI
def update_ui(stdscr):
    header_text = " Welcome to LRms Beacon Master V1.0 by Andy Kirby "
    stdscr.addstr(0, 0, header_text.center(curses.COLS), curses.A_REVERSE)  # Inverted header
    stdscr.addstr(1, 0, "-" * (curses.COLS - 1))  # Separator line

    line_num = 2  # Starting line number for serial output

    while True:
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current timestamp
                output_buffer.append(f"[{timestamp}] {data}")  # Add data with timestamp to the circular buffer

                # Update the visible portion of the screen with buffer content
                for idx, line in enumerate(output_buffer[-serial_lines:]):
                    stdscr.addstr(line_num + idx, 0, line.ljust(curses.COLS - 1))

                stdscr.refresh()

                # Move cursor to menu line to prevent overwrite
                stdscr.move(menu_line, 0)
                stdscr.clrtoeol()  # Clear line to prevent overwrite

        except serial.SerialException as e:
            # Handle serial port errors
            stdscr.addstr(line_num, 0, f"Error: {e}")
            stdscr.refresh()
            break  # Exit the loop on error

# Function to send AT command with "Beaconing" every 60 seconds
def send_at_command():
    global user_input_chars  # Use the global variable

    while True:
        command = f'AT+SEND=0,{user_input_chars},{user_input}\r\n'
        ser.write(command.encode('utf-8'))  # Send the updated AT command
        output_buffer.append(f"Beaconing: {user_input}")  # Add beaconing info to the circular buffer
        time.sleep(60)  # Sleep for 60 seconds

# Function to get user input
def get_user_input(stdscr):
    global user_input, user_input_chars, input_active
    stdscr.addstr(input_line, 0, "Enter Beacon Text (Max 50 chars): ")
    stdscr.move(input_line, len("Enter Beacon Text (Max 50 chars): "))  # Move cursor after the colon
    stdscr.refresh()
    curses.echo()
    user_input = stdscr.getstr(input_line, len("Enter Beacon Text (Max 50 chars): "), 50).decode('utf-8')[:50]  # Limit input to 50 chars
    curses.noecho()
    user_input_chars = len(user_input)  # Get the number of characters entered
    input_active = False  # Reset input_active flag

# Main function to setup curses and run application
def main(stdscr):
    global input_active
    stdscr.clear()
    curses.curs_set(1)  # Show cursor
    stdscr.addstr(curses.LINES - 3, 0, "Menu:")
    stdscr.addstr(curses.LINES - 2, 0, "- Beacon Text (Press 'b')")
    stdscr.addstr(curses.LINES - 1, 0, "Press 'q' to quit")
    stdscr.refresh()

    try:
        # Start updating the UI in a separate thread
        ui_thread = threading.Thread(target=update_ui, args=(stdscr,))
        ui_thread.daemon = True
        ui_thread.start()

        # Start sending AT command with "Beaconing" in a separate thread
        at_thread = threading.Thread(target=send_at_command)
        at_thread.daemon = True
        at_thread.start()

        while True:
            key = stdscr.getch()
            if key == ord('q'):
                break  # Exit on 'q' key press
            elif key == ord('b'):
                # Toggle input field visibility when 'b' is pressed
                if input_active:
                    stdscr.move(input_line, len("Enter Beacon Text (Max 50 chars): "))
                    stdscr.clrtoeol()  # Clear input field
                    input_active = False
                else:
                    get_user_input(stdscr)
                    input_active = True

    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        ser.close()

if __name__ == "__main__":
    curses.wrapper(main)

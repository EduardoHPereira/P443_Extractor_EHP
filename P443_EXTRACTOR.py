# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:59:33 2024

@author: GEDT
"""

import serial
import time
import csv
import os
from datetime import datetime
import threading

# Constants
BAUDRATE = 19200
TIMEOUT = 5
DIRECTORY = 'C:/Write/your/directory/here'

# Hexadecimal package to send (example: "68 e3 e3 68")
hex_package = """
68 03 03 68 40 01 00 41 16 
68 07 07 68 7b 01 00 07 14 04 00 9b 16 
68 07 07 68 5b 01 00 07 14 05 00 7c 16 
68 07 07 68 7b 01 00 07 14 06 00 9d 16 
68 07 07 68 5b 01 00 07 14 11 00 88 16 
68 07 07 68 7b 01 00 07 14 08 00 9f 16 
68 07 07 68 5b 01 00 07 14 03 bf 39 16 
68 07 07 68 7b 01 00 07 14 40 25 fc 16 
68 07 07 68 5b 01 00 07 12 40 25 da 16 
68 07 07 68 7b 01 00 07 14 df 00 76 16 
68 07 07 68 5b 01 00 07 14 04 00 7b 16 
68 07 07 68 7b 01 00 07 14 05 00 9c 16 
68 07 07 68 5b 01 00 07 14 06 00 7d 16 
68 07 07 68 7b 01 00 07 14 11 00 a8 16 
68 09 09 68 5b 01 00 07 15 01 01 05 4a c9 16 
68 07 07 68 7b 01 00 07 15 01 01 9a 16 
68 0a 0a 68 5b 01 00 07 40 01 01 26 00 00 cb 16 
68 05 05 68 7b 01 00 05 4e cf 16 
68 07 07 68 5b 01 00 07 17 00 01 7b 16 
68 06 06 68 7b 01 00 06 21 00 a3 16 
68 06 06 68 5b 01 00 06 21 01 84 16 
68 06 06 68 7b 01 00 06 21 02 a5 16 
68 06 06 68 5b 01 00 06 21 03 86 16 
68 06 06 68 7b 01 00 06 21 04 a7 16 
68 06 06 68 5b 01 00 06 21 05 88 16 
68 06 06 68 7b 01 00 06 21 06 a9 16 
68 06 06 68 5b 01 00 06 21 07 8a 16 
68 06 06 68 7b 01 00 06 21 08 ab 16 
68 07 07 68 5b 01 00 07 18 00 01 7c 16 
68 06 06 68 7b 01 00 06 21 00 a3 16 
68 06 06 68 5b 01 00 06 21 01 84 16 
"""

def target(port, hex_package, results):
    """
   Sends a sequence of hexadecimal packets to the specified serial port and stores the received data.

   Parameters:
   port (str): The serial port to send the data.
   hex_package (str): The sequence of hexadecimal data to send.
   results (dict): Dictionary to store the received data from each port.
   """
   # Initialize serial communication with the specified parameters
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = 19200
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_EVEN
    ser.stopbits = serial.STOPBITS_ONE
    ser.timeout = 5
    
    lines = hex_package.strip().split('\n')
    all_received_data = []

    ser.open()
    ser.flushInput()
    ser.flushOutput()
    received_data_list = []
    
    for index, line in enumerate(lines, start=1):
        package = line.replace(" ", "")
        hex_data_to_send = bytes.fromhex(package)
        ser.write(hex_data_to_send)
        time.sleep(0.2)
        received_data = ser.read_all()
        hex_received_data = received_data.hex().upper()
        received_data_list.append(hex_received_data)
    
    all_received_data.append(received_data_list)
    ser.close()

    results[port] = all_received_data

# Dictionary to store the results of each thread
results = {}

# Start threads
collector_1 = threading.Thread(target=target, args=("COM3", hex_package, results))
collector_2 = threading.Thread(target=target, args=("COM4", hex_package, results))
collector_1.start()
collector_2.start()

# Comparison part
count = 0
n_it = 8
new_event = 2
print("First Request")

definitive_list = []
previous_data = [1]

while count <= n_it - 1:
    collector_1.join()
    collector_2.join()
    
    collected_data_1 = results["COM3"]
    collected_data_2 = results["COM4"]
    current_data = [collected_data_1, collected_data_2]
    
    # Data comparison
    if new_event == 2:
        previous_data = current_data
        definitive_list.append(current_data)
        print("------Starting loop request------")
        new_event = 0
    if current_data[0][0][30] == previous_data[0][0][30] and current_data[1][0][30] == previous_data[1][0][30]:
        time.sleep(1)
        count += 1
        new_event = 0
        print(f"Waiting for new event -> COUNTER [{count}]/[{n_it}]")
    else:  # When current_data != previous_data
        previous_data = current_data
        definitive_list.append(current_data)
        count = 0
        new_event = 1
        print("------NEW EVENT------")
        time.sleep(1)

    # Restart threads for a new read
    collector_1 = threading.Thread(target=target, args=("COM3", hex_package, results))
    collector_2 = threading.Thread(target=target, args=("COM4", hex_package, results))
    collector_1.start()
    collector_2.start()

# Create fault location and selection variables
fault_locations = [[] for _ in range(len(definitive_list[0]))]
fault_selections = [[] for _ in range(len(definitive_list[0]))]

# Read fault location and selection for each new fault package
for record_index, record in enumerate(definitive_list):
    for relay_number in range(len(record)):
        fault_segment = record[relay_number][0][-1]
        fault_data = fault_segment[64:66] + fault_segment[62:64]
        if fault_segment[66:68] == '7C':
            fault_value = int(fault_data, 16) / 100
        elif fault_segment[66:68] == '7B':
            fault_value = int(fault_data, 16) / 1000
        elif fault_segment[66:68] == '7D':
            fault_value = int(fault_data, 16) / 10
        fault_locations[relay_number].append(fault_value)

        selection_segment = record[relay_number][0][-2]
        selection_data = selection_segment[226:228]
        selection_value = format(int(selection_data, 16), '08b')
        fault_selections[relay_number].append(selection_value)

# Transpose and write data to CSV
complete_list = (fault_locations, fault_selections)
complete_tuple_transposed = tuple(zip(*[zip(*sublist) for sublist in complete_list]))
complete_list_transposed = list(complete_tuple_transposed)
complete_list_transposed.pop(0)


headers = ["Fault Location (local)", "Fault Location (remote)", "Fault Selection (local)", "Fault Selection (remote)"]
file_name = 'Recorded_Faults.csv'

file_path = os.path.join(DIRECTORY, file_name)

# Write data to CSV file
with open(file_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    
    for row in complete_list_transposed:
        writer.writerow([value for tup in row for value in tup])

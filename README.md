# P443_Extractor_EHP
Automated Fault Data Extraction for AREVA P443 Relays

This Python script facilitates communication with devices over serial ports using hexadecimal data packets. It is designed to monitor, compare, and record fault events detected in transmission line systems by communicating with Intelligent Electronic Devices (IEDs) over serial connections. The results, including fault locations and fault selections, are stored in a CSV file for further analysis.

Features
1 - Sends hexadecimal data to IEDs via serial ports (COM3 and COM4 by default).
2 - Receives and interprets responses in hexadecimal format.
3 - Compares received data across multiple iterations to detect new fault events.
4 - Extracts fault location and fault selection data from the received hex responses.
5 - Saves the fault information to a CSV file with appropriate headers.

How to Use
1 - Set the Serial Port and Hexadecimal Package:
 -> Configure the serial ports (e.g., COM3, COM4) and the hexadecimal package you want to send.
 -> Adjust the DIRECTORY constant to point to the folder where you want the CSV file to be saved.
 
2 - Run the Script.


Feel free to modify the code for your own setup or submit pull requests to improve functionality.

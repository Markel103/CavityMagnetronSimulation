# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 09:29:46 2024

@author: Markel
"""


from pyvisa import util
import numpy as np
import serial
import time
from threading import Event
import win32com.client as comclt
BAUD_RATE = 115200


def remove_comment(string):
    if (string.find(';') == -1):
        return string
    else:
        return string[:string.index(';')]


def remove_eol_chars(string):
    # removed \n or traling spaces
    return string.strip()


def send_wake_up(ser):
    # Wake up
    # Hit enter a few times to wake the Printrbot
    ser.write(str.encode("\r\n\r\n"))
    time.sleep(2)   # Wait for Printrbot to initialize
    ser.flushInput()  # Flush startup text in serial input

def wait_for_movement_completion(ser,cleaned_line):

    Event().wait(1)

    if cleaned_line != '$X' or '$$':

        idle_counter = 0

        while True:

            # Event().wait(0.01)
            ser.reset_input_buffer()
            command = str.encode('?' + '\n')
            ser.write(command)
            grbl_out = ser.readline() 
            grbl_response = grbl_out.strip().decode('utf-8')

            if grbl_response != 'ok':

                if grbl_response.find('Idle') > 0:
                    idle_counter += 1

            if idle_counter > 10:
                break
    return


def stream_gcode(GRBL_port_path,gcode_path):
    # with contect opens file/connection and closes it if function(with) scope is left
    with open(gcode_path, "r") as file, serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        send_wake_up(ser)
        print("Sending gcode: $X")
        command = '$X' + '\n'
        ser.write(command.encode())
        wait_for_movement_completion(ser,'$X')
        grbl_out = ser.readline()  # Wait for response with carriage return
        print(" : " , grbl_out.strip().decode('utf-8'))
        # command = "G0X0Y0Z0" + '\n'
        # ser.write(command.encode())
        # wait_for_movement_completion(ser,'G0X0Y0Z0')
        # grbl_out = ser.readline()  # Wait for response with carriage return
        # print(" : " , grbl_out.strip().decode('utf-8'))
        for line in file:
            # cleaning up gcode from file
            cleaned_line = remove_eol_chars(remove_comment(line))
            if cleaned_line:  # checks if string is empty
                print("Sending gcode:" + str(cleaned_line))
                # converts string to byte encoded string and append newline
                command = str.encode(line + '\n')
                ser.write(command)  # Send g-code
                wait_for_movement_completion(ser,cleaned_line)
                grbl_out = ser.readline()  # Wait for response with carriage return
                print(" : " , grbl_out.strip().decode('utf-8'))

                
        
        print('End of gcode')

if __name__ == "__main__":

    # GRBL_port_path = '/dev/tty.usbserial-A906L14X'
    GRBL_port_path = 'COM4'
    # gcode_path = 'grbl_test.gcode'
    nx = 20
    ny = 20
    nz = 6
    
    xlen = 100
    ylen = 100
    zlen = 30
    
    xstep = int(xlen / nx)
    ystep = int(ylen / ny)
    zstep = int(zlen / nz)
    
    print(xstep,ystep,zstep)

    print("USB Port: ", GRBL_port_path)
    with serial.Serial(GRBL_port_path, BAUD_RATE) as ser:
        send_wake_up(ser)
        print("Sending gcode: $X")
        command = '$X' + '\n'
        ser.write(command.encode())
        wait_for_movement_completion(ser,'$X')
        grbl_out = ser.readline()
        print(" : " , grbl_out.strip().decode('utf-8'))
        wsh= comclt.Dispatch("WScript.Shell")
        for k in range (nz):
            for i in range (ny):
                for j in range (nx):
                    print(i,j,k)
                    wsh.AppActivate("Manual mapper plugin")
                    wsh.SendKeys("\n")
                    command = "G91G21X" + str(xstep) + "F2000" + '\n'
                    ser.write(command.encode())
                    wait_for_movement_completion(ser,command)
                command = "G91G21X" + str(-xlen) + "Y" + str(-ystep) + "F2000" + '\n'
                ser.write(command.encode())
                wait_for_movement_completion(ser,command)
            command = "G91G21Y" + str(ylen) + "Z" + str(zstep) + "F2000" + '\n'
            ser.write(command.encode())
            wait_for_movement_completion(ser,command)
        command = "G91G21Z" + str(-zlen) + "F2000" + '\n'
        ser.write(command.encode())
        wait_for_movement_completion(ser,command)
        
        print('End of gcode')
    print('EOF')

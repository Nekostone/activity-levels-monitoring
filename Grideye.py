# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 23:00:15 2020

@author: TTM
"""

import serial
import numpy as np
import matplotlib.pyplot as plt

serial_port = 'COM3'
baud_rate = 115200
start_byte = b'\r\n'

ser = serial.Serial(serial_port, baud_rate)
ser.flushInput()


counter = 0


while counter < 600:
    try:
        ser_bytes = ser.readline()
        if ser_bytes == start_byte:
            data_frame = np.zeros(64)
            for i in range(64):
                try:
                    ser_bytes = ser.readline()
                    decoded_bytes = float(ser_bytes[0:-2].decode("utf-8"))
                    data_frame[i] = decoded_bytes
                    
                except Exception as e:
                    print(e)
                    print(ser_bytes)
                    break
                
            data_frame = np.reshape(data_frame, (8,8))
            img = plt.imshow(data_frame, cmap='hot', interpolation='nearest')
            plt.colorbar()
            plt.clim(20,40)
            plt.pause(0.02) # plt pause allows the plotter time to catch up with the data
            plt.clf() 
            counter += 1
            
        else:
            continue
            
    except Exception as e:
        print(e)
        break


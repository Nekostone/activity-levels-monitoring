import serial
import time
import csv
import numpy as np
import matplotlib.pyplot as plt


# Serial parameters
serial_port = 'COM3'
baud_rate = 115200
start_byte = b'\r\n'

# Max sample count to take. Ensures the loop will cut off after some amount of time. 
# Larger number of samples means it executes for a longer amount of time
num = 200

# Mode
# 0: real time plot mode
# 1: Saved data mode. File is saved to current working directory. File is saved as yyyymmdd_hhmmss.csv
mode = 0

counter = 0

def plot(data):
    d = np.array(data)
    d = np.reshape(d, (8,8))
    plt.imshow(d, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.clim(25,40)
    plt.pause(0.05) # plt pause allows the plotter time to catch up with the data
    plt.clf() 
    return d

def to_csv(data,file):
    curr_time = time.time()
    data.insert(0, curr_time)
    with open(file, "a", newline = '') as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(data)

def run_arduino(mode): # 0: plot mode, 1: csv mode
    curr_time = time.time()
    filename = time.strftime("%Y%m%d_%H%M%S",time.localtime(curr_time)) + "_grideye.csv"
    ser = serial.Serial(serial_port, baud_rate)
    ser.flushInput()
    
    global counter
    while counter < num:
        try:
            ser_bytes = ser.readline()
            if ser_bytes == start_byte:
                data_frame = [0] * 64
                for i in range(64):
                    try:
                        ser_bytes = ser.readline()
                        decoded_bytes = float(ser_bytes[0:-2].decode("utf-8"))
                        data_frame[i] = decoded_bytes
                        
                    except Exception as e:
                        print(e)
                        print(ser_bytes)
                        break
                
                print(data_frame)
                if mode == 0:
                    plot(data_frame)
                    
                elif mode == 1:
                    to_csv(data_frame,filename)
                    
                counter += 1
                
            else:
                continue
                
        except Exception as e:
            print(e)
            break


run_arduino(mode)

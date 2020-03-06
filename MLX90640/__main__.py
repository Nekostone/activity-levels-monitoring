import serial
import time
import csv
import numpy as np
from csv_utils import to_csv
import matplotlib.pyplot as plt

# Serial parameters
serial_port = 'COM4'
baud_rate = 115200
start_byte = b'\r\n'

# Max sample count to take. Ensures the loop will cut off after some amount of time. 
# Larger number of samples means it executes for a longer amount of time
num = 200

# Mode
# 0: real time plot mode
# 1: Saved data mode. File is saved to current working directory. File is saved as yyyymmdd_hhmmss.csv
mode = 0


def plot(data):
    d = np.array(data)
    d = np.reshape(d, (24,32))
    plt.imshow(d, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.clim(25,40)
    plt.pause(0.05) # plt pause allows the plotter time to catch up with the data
    plt.clf() 
    return d

def run_arduino(mode: int, counter: int): # 0: plot mode, 1: csv mode
    curr_time = time.time()
    filename = time.strftime("%Y%m%d_%H%M%S",time.localtime(curr_time)) + "_grideye.csv"
    ser = serial.Serial(serial_port, baud_rate)
    ser.flushInput()

    # ignore initialization statements
    ser.readline()
    ser.readline()
    ser.readline()
    ser.readline()

    while counter < num:
        try:
            ser_bytes = ser.readline()
            decoded_string = ser_bytes.decode("utf-8").strip("\r\n")
            values = decoded_string.split(",")[:-1]
            data_frame = np.reshape(np.array(values).astype(float), (24,32))

            if mode == 0:
                plot(data_frame)

            elif mode == 1:
                to_csv(data_frame,filename)

            counter += 1

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
            break

if __name__ == "__main__":
    run_arduino(mode, counter=0)


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


def get_nan_value_indices(array):
  """
  returns indices of nan values in an array of [row, column]
  """
  return np.argwhere(np.isnan(array))

def interpolate_values(array, nan_value_indices):
    """
    :param 24x32 array:
    :param result obtained from get_nan_value_indices(data_frame):
    :return: 24x32 array
    """
    for indx in nan_value_indices:
        x = indx[0]
        y = indx[1]
        array[x][y] = (array[x][y+1] + array[x+1][y] + array[x-1][y] + array[x][y-1]) / 4
    return array

def section_grid(array):
    """
    :param array: 24x32 array
    :return: 8x12x8 array
    """
    result = np.zeros((8, 12, 8))
    block_number = 0
    for i in range(2):
        for j in range(4):
            result[block_number] = array[i * 12:(i + 1) * 12, j * 8:(j + 1) * 8]
            block_number += 1
    return result

def plot(d):
    plt.imshow(d, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.clim(25,40)
    plt.pause(0.05) # plt pause allows the plotter time to catch up with the data

    plt.clf() 

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
    ser.readline()

    while counter < num:
        try:
            ser_bytes = ser.readline()
            decoded_string = ser_bytes.decode("utf-8").strip("\r\n")
            values = decoded_string.split(",")[:-1]
            data_frame = np.reshape(np.array(values).astype(float), (24,32))

            if mode == 0:
                d = np.array(data_frame)
                d = np.reshape(d, (24, 32))
                nan_value_indices = get_nan_value_indices(d)
                d = interpolate_values(d, nan_value_indices)
                # plot(d)
                divided_grid = section_grid(d)

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


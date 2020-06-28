import time

import numpy as np
import serial
import keyboard
from file_utils import save_npy, create_folder_if_absent
from visualizer import init_heatmap, update_heatmap
import asyncio

"""
Initialization
Serial Parameters - Port, Baud Rate, Start Byte
Program Mode - Plot (Debug) / Write Mode
"""

SERIAL_PORT = 'COM5'  # for windows
# SERIAL_PORT = "/dev/ttyS3" # for linux
BAUD_RATE = 115200
ARRAY_SHAPE = (24, 32)

DEBUG_MODE = 1
WRITE_MODE = 0
DATA_PATH = "data/switching test"  # change as it fits
DATA_DIR_SORT = "day"


def interpolate_values(df):
    """
    :param: 24x32 data frame obtained from get_nan_value_indices(df)
    :return: 24x32 array
    """
    nan_value_indices = np.argwhere(np.isnan(df))
    x_max = df.shape[0] - 1
    y_max = df.shape[1] - 1
    for indx in nan_value_indices:
        x = indx[0]
        y = indx[1]
        if x == 0 and y == 0:
            df[x][y] = (df[x + 1][y] + df[x][y + 1]) / 2

        elif (x == x_max and y == y_max):
            df[x][y] = (df[x - 1][y] + df[x][y - 1]) / 2

        elif (x == 0 and y == y_max):
            df[x][y] = (df[x + 1][y] + df[x][y - 1]) / 2

        elif (x == x_max and y == 0):
            df[x][y] = (df[x - 1][y] + df[x][y + 1]) / 2

        elif (x == 0):
            df[x][y] = (df[x + 1][y] + df[x][y - 1] + df[x][y + 1]) / 3

        elif (x == x_max):
            df[x][y] = (df[x - 1][y] + df[x][y - 1] + df[x][y + 1]) / 3

        elif (y == 0):
            df[x][y] = (df[x + 1][y] + df[x - 1][y] + df[x][y + 1]) / 3

        elif (y == y_max):
            df[x][y] = (df[x - 1][y] + df[x + 1][y] + df[x][y - 1]) / 3
        else:
            df[x][y] = (df[x][y + 1] + df[x + 1][y] + df[x - 1][y] + df[x][y - 1]) / 4
    return df


# TODO: Using a lambda function, Automate the cycle of:
# - collection of 30mins worth of data frame
# - time series analysis
# - free memory by deleting the 30mins of data after analysis is completed
# - send data to cloud

def handle_df(values, counter):
    array = np.array(values)
    if array.shape[0] == ARRAY_SHAPE[0] * ARRAY_SHAPE[1]:
        df = np.reshape(array.astype(float), ARRAY_SHAPE)
        df = interpolate_values(df)
        return df, True
    else:
        return None, False
        # if mode == DEBUG_MODE:
        #     print("Updating Heatmap...", "[{}]".format(counter))
        #     update_heatmap(df, plot)

        # elif mode == WRITE_MODE:
        #     print("Saving npy object...", "[{}]".format(counter))
        #     save_npy(df, DATA_PATH, directory_sort=DATA_DIR_SORT)
        #


def save_serial_output(ser, counter, plot, mlx_number=0):
    """
    Save serial output from arduino
    """
    #
    # change_port = None

    if mlx_number == 0:
        change_port = '3'
        print('com3 waiting')
    elif mlx_number == 1:
        change_port = '5'
        print('com5 waiting')

    if change_port == '3':
        ser.port = 'COM3'
        print("com3 now")
    elif change_port == '5':
        ser.port = 'COM5'
        print("com5 now")

    # elif mode == WRITE_MODE:
    #     create_folder_if_absent(DATA_PATH)

    try:
        ser_bytes = ser.readline()
        decoded_string = ser_bytes.decode("utf-8", errors='ignore').strip("\r\n")
        values = decoded_string.split(",")[:-1]

        df, legit_string = handle_df(values, counter)

        if legit_string:
            print("Updating Heatmap...", "[{}]".format(counter))
            update_heatmap(df, plot)
        else:
            print("Not Updating Heatmap...", "[{}]".format(counter))

    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(e)

def checkKeypress():
    if keyboard.is_pressed('1'):
        mlx_number = 0
    elif keyboard.is_pressed('2'):
        mlx_number = 1
    return mlx_number


if __name__ == "__main__":
    counter = 0
    min_temp = 28
    max_temp = 40
    plot = init_heatmap("MLX90640 Heatmap", ARRAY_SHAPE, min_temp, max_temp)
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    ser.reset_output_buffer()
    mlx_number = 0

    while True:
        counter +=1
        mlx_number = checkKeypress()
        save_serial_output(ser, counter, plot, mlx_number)
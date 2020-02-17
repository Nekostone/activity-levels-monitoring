import serial
import time
import csv
import matplotlib
import numpy as np

matplotlib.use("tkAgg")
ser = serial.Serial('COM4', 115200)
ser.flushInput()

while True:
    try:
        frame = np.array([])
        for i in range(0, 8):
            row = np.array([])
            for j in range(0, 8):
                ser_bytes = ser.readline()
                try:
                    decoded_bytes = float(ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))
                    row = np.append(row, decoded_bytes)
                except:
                    continue
            frame = np.append(frame, row)
        print(frame)
        print('break')

        frame = np.resize(frame, (8, 8))
        with open("test_data.csv", "a", newline = '') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow([time.time(), np.array2string(frame)])

    except Exception as e:
        print(e)
        # print("Keyboard Interrupt")
        break


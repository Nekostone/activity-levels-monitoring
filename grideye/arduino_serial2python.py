import serial
import time
import csv
import matplotlib
matplotlib.use("tkAgg")
import matplotlib.pyplot as plt
import numpy as np

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

        pt = np.resize(frame, (8, 8))
        # draw_plot(pt)

        # plt.show()
        with open("test_data.csv", "a", newline = '') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow([time.time(), np.array2string(pt)])

    except Exception as e:
        print(e)
        # print("Keyboard Interrupt")
        break

def draw_plot(pt):
    fig, ax = plt.subplots()
    im = ax.imshow(pt)
    ax.set_xticks(np.arange(8))
    ax.set_yticks(np.arange(8))
    ax.set_xticklabels(range(8))
    ax.set_yticklabels(range(8))

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(8):
        for j in range(8):
            text = ax.text(j, i, pt[i, j],
                           ha="center", va="center", color="w")

    ax.set_title("Heat map")
    fig.tight_layout()

    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.savefig("test_pic.png")
#! usr/bin/env/python
from file_utils import get_all_files
from file_utils import get_frame, get_frame_GREY
import matplotlib.pyplot as plt
import numpy as np
from visualizer import write_gif
import copy

class KalmanFilter:
    def __init__(self):
        # State matrices
        self.F = np.array([[1, 1], [0, 1]])  # F matrix
        self.H = np.matrix([1, 0])  # H matrix

        # Covariance matrices
        self.Q = np.array([[0.05, 0], [0, 0.01]])  # process noise covariance
        self.R = 2  # measurement noise covariance
        self.P = np.array([[1, 0], [0, 1]])  # estimation covariance, init to identity matrix

        # System State
        self._x = np.array([[0], [0]])  # current state
        self.K = 0  # Kalman gain

    def filter(self, y):
        # estimate
        P_est = np.dot(np.dot(self.F, self.P), np.transpose(self.F)) + self.Q
        x_est = np.dot(self.F, self._x)

        # compute kalman gain
        PH_t = np.dot(P_est, np.transpose(self.H))
        HPH_t = np.dot(np.dot(self.H, P_est), np.transpose(self.H))
        self.K = np.dot(PH_t, 1 / (HPH_t + self.R))

        # update
        self._x = x_est + np.dot(self.K, np.subtract(y, np.dot(self.H, x_est)))
        self.P = np.dot((np.eye(2) - np.dot(self.K, self.H)), P_est)

        return self._x[0][0]



class Frame:
    def __init__(self):
        self.frame_state = [[KalmanFilter() for i in range(32)] for j in range(24)]
        self.frame_out = np.zeros((24, 32))  # temp state after filter
        self.frame_in = np.zeros((24, 32))  # measured temp

    def process_frame(self):  # improve with multithreading
        self.get_data()
        for col in range(32):
            for row in range(24):
                pix = self.frame_state[row][col]
                self.frame_out[row][col] = pix.filter(self.frame_in[row][col])

        return self.frame_out

    def get_data(self):
        global data
        self.frame_in = get_frame(data.pop(0))
        # print(self.frame_in)

data = get_all_files("data/teck_walk_out_and_in")
data2 = get_all_files("data/teck_walk_out_and_in")

# ------------------------------for generating pngs------------------------------------------
temp_over_time = []
frame = Frame()
for i in range(len(data2)):
    processed = frame.process_frame()
    temp_over_time.append(copy.copy(processed))

    plt.subplot(121)
    plt.imshow(get_frame(data2[i]))
    plt.title("Original Image %d" % i)
    plt.subplot(122)
    plt.imshow(processed)
    plt.title("noise removed %d" % i)

    plt.savefig("kalman_filter_pics/teck_walk_out_and_in/{}.png".format(i)) #make png

    if i == len(data2)-1:
        print("done!")


# --------------------------------looking at individual pixels-------------------------------------------------
# temp_over_time = []  # contains the filtered results
# frame = Frame()
# for i in range(len(data2)):
#     processed = frame.process_frame()
#     temp_over_time.append(copy.copy(processed))  # ADD THE COPY.COPY(). IF YOU DONT,IT APPENDS THE REFERENCE SO YOUR WHOLE ARRAY IS THE SAME
#
# pixel_over_time = []
# for i in range(len(data2)):
#     frame = get_frame(data2[i])  # measurement data
#     pixel_over_time.append(frame[20][20])  # adds the values of a specific pixel over time to pixel_over_time
#
# filtered_over_time = []
# for i in range(len(data2)):
#     frame = temp_over_time[i]  # filtered data
#     # print(frame)
#     # print(len(frame))
#     filtered_over_time.append(frame[20][20])  # adds the values of a specific pixel over time to filtered_over_time
#
# plt.plot(np.arange(0,255,1), pixel_over_time,  "r--", np.arange(0,255,1), filtered_over_time, "bs")
# plt.show()


# ----------------------------------for generating gifs------------------------------------------------
pngs = get_all_files("kalman_filter_pics/teck_walk_out_and_in")

GifGenInput = ["kalman_filter_pics/teck_walk_out_and_in/" + "{}".format(i) + ".png" for i in range(len(pngs))]

write_gif(GifGenInput, "kalman_filter_gifs/teck_walk_out_and_in.gif", 0, 254, fps=30)

#! usr/bin/env/python
from file_utils import get_all_files
from file_utils import get_frame, get_frame_GREY
import numpy as np
import matplotlib.pyplot as plt
import copy


class Kalman_Filter:
    def __init__(self):
        # State matrices
        self.F = np.array([[1, 1],[0, 1]])  # F matrix
        self.H = np.matrix([1, 0])  # H matrix

        # Covariance matrices
        self.Q = np.array([[0.05, 0], [0, 0.01]])   # process noise covariance
        self.R = 2 # measurement noise covariance
        self.P = np.array([[1, 0], [0, 1]]) # estimation covariance, init to identity matrix

        # System State
        self._x = np.array([[0], [0]])  # current state
        self.K = 0  # Kalman gain

        # data
        self._y = 0 # arbitary init value
        self._counter = 0

    def filter(self):
        # get current set of data input
        self.set_y()

        # estimate
        P_est = np.dot(np.dot(self.F, self.P), np.transpose(self.F)) + self.Q
        x_est = np.dot(self.F, self._x)
        
        # compute kalman gain
        PH_t = np.dot(P_est, np.transpose(self.H))
        HPH_t = np.dot(np.dot(self.H, P_est), np.transpose(self.H))
        self.K = np.dot(PH_t, 1/(HPH_t + self.R))

        # update 
        self._x = x_est + np.dot(self.K, np.subtract(self._y, np.dot(self.H, x_est)))
        self.P = np.dot((np.eye(2)-np.dot(self.K, self.H)), P_est)

        # return output
        return self.output()

    def set_y(self): 
        self._y = self.get_data()

    def output(self):
        return self._x[0][0]


    def get_data(self):
        #  write function to get data here, should return a single float for the temperature
        #  takes in a pixel temperature value of a frame of thermal sensor data in the form of a numpy array
        global temp_over_time
        # self._counter += 1
        # print(self._counter)
        # print(np.eye(2)-np.dot(self.K, self.H))
        return temp_over_time.pop(0)

noise_remover = Kalman_Filter()
data = get_all_files("data/teck_walk_out_and_in")
temp_over_time = []
for i in range(len(data)):
    to_be_added = get_frame(data[i])[0][0]
    temp_over_time.append(to_be_added)

temp_over_time_2 = copy.copy(temp_over_time)
noise_remover = Kalman_Filter()
filtered = []
for i in range(len(data)):
    filtered.append(np.array(noise_remover.filter())[0][0])

plt.plot(np.arange(0,255,1), temp_over_time_2,  "r--", np.arange(0,255,1), filtered, "bs")
plt.show()
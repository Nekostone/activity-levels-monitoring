#! usr/bin/env/python
from file_utils import get_all_files
from file_utils import get_frame, get_frame_GREY
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import copy

class PixelKalmanFilter:
    def __init__(self):
        # State matrices
        self.F = np.array([[1, 1], [0, 1]])  # F matrix
        self.H = np.matrix([1, 0])  # H matrix

        # Covariance matrices
        self.Q = np.array([[0.1, 0], [0, 0.1]])  # process noise covariance
        self.R = 1.5  # measurement noise covariance
        self.P = np.array([[1, 0], [0, 1]])  # estimation covariance, init to identity matrix

        # System State
        self._x = np.array([[0], [0]])  # current state
        self.K = 0  # Kalman gain
        
        # data
        self._counter = 0

    def filter(self, y):
        # estimate
        P_est = np.dot(np.dot(self.F, self.P), np.transpose(self.F)) + self.Q
        x_est = np.dot(self.F, self._x)
        
        # compute kalman gain
        PH_t = np.dot(P_est, np.transpose(self.H))
        HPH_t = np.dot(np.dot(self.H, P_est), np.transpose(self.H))
        self.K = np.dot(PH_t, 1/(HPH_t + self.R))

        # update 
        self._x = x_est + np.dot(self.K, np.subtract(y, np.dot(self.H, x_est)))
        self.P = np.dot((np.eye(2)-np.dot(self.K, self.H)), P_est)

        return self._x[0][0]        

class FrameKalmanFilter:
    def __init__(self):
        self.filters = [[PixelKalmanFilter() for i in range(32)] for j in range(24)]

    def process_frame(self, frame_in):  # improve with multithreading
        frame_out = np.zeros((24, 32))  # temp state after filter
        for col in range(32):
            for row in range(24):
                pixel_filter = self.filters[row][col]
                frame_out[row][col] = pixel_filter.filter(frame_in[row][col])

        return frame_out

def init_noise_reduction_plot(frame, subplt_titles):
    num_rows = 1
    num_columns = 2
    fig, axs = plt.subplots(num_rows, num_columns)
    fig.suptitle("Noise Reduction with Kalman Filters")
    ims = []
    for i in range(num_columns):
        axs[i].set_title(subplt_titles[i])
        im = axs[i].imshow(frame)
        ims.append(im)
    return ims, axs, fig

def update_noise_reduction_plot(ims, images):
    for i in range(len(ims)):
        ims[i].set_clim(vmin=np.amin(images[i]), vmax=np.amax(images[i]))
        ims[i].set_data(images[i])
    plt.draw()
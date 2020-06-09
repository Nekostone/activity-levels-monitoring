import copy

import matplotlib.pyplot as plt
import numpy as np

from background_subtraction import postprocess_img
from file_utils import get_all_files, get_frame, get_frame_GREY

data = "data/teck_walk_out_and_in"
files = get_all_files(data)

def append_centroid_history(centroids, i, centroid_history):
    if len(centroids) == 1:
        centroid_history.append(centroids[0])
        return
        
    if i == 0:
        centroid_history.append(centroids[0])  # pick the first centroid of the first frame. Not the most accurate but yolo
    else:
        prev_centroid = centroid_history[i - 1]
        if len(centroids) > 1:
            if prev_centroid:  # if the subsequent frames have more than one centroid then we use the one closest to the previous centroid
                prev_centroid = centroid_history[i-1]
                distances = np.zeros(len(centroids))
                for j in range(len(centroids)):
                    x_disp = prev_centroid[0]-centroids[j][0]
                    y_disp = prev_centroid[1]-centroids[j][1]
                    distance = (x_disp**2 + y_disp**2)**(1/2)
                    distances[j] = distance
                desired_centroid_index = np.argmin(distances)
                centroid_history.append(centroids[desired_centroid_index])

            elif not prev_centroid:  # if your first few frames were None and your first frame with centroids has multiple, just pick the first one
                centroid_history.append(centroids[0])
        else:
            centroid_history.append(None)

def get_centroid_history(files):
    centroid_history = []
    for i in range(len(files)):
        img = get_frame_GREY(files[i])
        images, centroids = postprocess_img(img)
        append_centroid_history(centroids, i, centroid_history)

    return np.array(centroid_history)


class Interpolator:
    def __init__(self, history):
        self.none_counter = 0
        self.none_block = []  # stores start and end indices of blocks of none
        self.block_start = (0, 0)
        self.block_end = (0, 0)
        self.history = copy.copy(history)
        self.limit = 5 # how many Nones until you are sure the elder has left the room?

    def none_checker(self, arr_elem, index):
        if arr_elem is None:
            self.none_counter += 1
            if len(self.none_block) == 0:  # if this be the first None,
                if index != 0:  # and if the first element isn't a None,
                    self.none_block.append(index)
                    self.block_start = self.history[index-1]
        else:
            self.none_counter = 0
            if self.history[index-1] is None: # if the previous element was the last None in a block,
                self.none_block.append(index-1)
                self.block_end = self.history[index]
                length = self.none_block[1] - self.none_block[0] + 1
                if length <= self.limit:  # if we wanna interpolate the current none block?
                    start_x = self.block_start[0]
                    start_y = self.block_start[1]
                    x_interval = (self.block_end[0] - start_x) / (length+1)
                    y_interval = (self.block_end[1] - start_y) / (length+1)

                    for k in range(length):
                        self.history[self.none_block[0] + k] = (np.round(start_x + (k+1)*x_interval), np.round(start_y + (k+1)*y_interval))

                self.none_block = []
                
def plot_centroid_history(interp_history):
    x = [x[0] for x in interp_history if x!= None]
    y = [32-x[1] for x in interp_history if x!= None]
    xmin = min(x)
    xmax = max(x)
    ymin = min(y)
    ymax = max(y)
    fig, axs = plt.subplots(ncols=2, sharey=True, figsize=(7, 4))
    fig.subplots_adjust(hspace=0.5, left=0.07, right=0.93)
    ax = axs[0]
    hb = ax.hexbin(x, y, gridsize=32, cmap='inferno')
    ax.axis([xmin, xmax, ymin, ymax])
    ax.set_title("Centroid History")
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label('counts')

    ax = axs[1]
    hb = ax.hexbin(x, y, gridsize=32, bins='log', cmap='inferno')
    ax.axis([xmin, xmax, ymin, ymax])
    ax.set_title("With a log color scale")
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label('log10(N)')

    plt.show()

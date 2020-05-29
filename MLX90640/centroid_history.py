import copy

import numpy as np

from background_model import postprocess_img
from file_utils import get_frame_GREY


def get_centroid_history(files):
    centroid_history = []
    for i in range(len(files)):
        img = get_frame_GREY(files[i])

        #  get images and centroids
        #  images array contains: [img, blurred_img, thresholded_img, annotated_img]
        images, centroids = postprocess_img(img)

        if i == 0:
            centroid_history.append(centroids[0])  # pick the first centroid of the first frame. Not the most accurate but yolo
        else:
            prev_centroid = centroid_history[i - 1]
            if len(centroids) > 1 and prev_centroid:  # if the subsequent frames have more than one centroid then we use the one closest to the previous centroid
                prev_centroid = centroid_history[i-1]
                distances = []
                for j in range(len(centroids)):
                    x_disp = prev_centroid[0]-centroids[j][0]
                    y_disp = prev_centroid[1]-centroids[j][1]
                    distance = np.sqrt(x_disp**2 + y_disp**2)
                    distances.append(distance)
                desired_centroid = distances.index(min(distances))
                centroid_history.append(centroids[desired_centroid])

            elif len(centroids) > 1 and not prev_centroid:  # if your first few frames were None and your first frame with centroids has multiple
                centroid_history.append(centroids[0])

            elif len(centroids) == 1:
                centroid_history.append(centroids[0])

            else:
                centroid_history.append(None)

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

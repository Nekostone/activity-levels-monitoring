import copy
import math
import os
from collections import Counter, defaultdict
from bokeh.plotting import curdoc, figure
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from background_subtraction import bs_godec, cleaned_godec_img, postprocess_img
from file_utils import (basename, create_folder_if_absent, get_all_files,
                        get_frame, get_frame_GREY, normalize_frame)


def input_target_centroid_area():
    centroid_area = input("Please input which area the target is (0-7):")
    
    print("The selected target is in area " + centroid_area)
    return centroid_area


def get_centroid_area_number(centroid):
    if centroid != None:
        x, y = centroid
        return x // 8 + y // 12
    return None

def get_centroid_history(files):
    centroid_history = []
    contour_history = []
    for i in range(len(files)):
        img = get_frame_GREY(files[i])
        images, centroids = postprocess_img(img)
        append_centroid_history(centroids, i, centroid_history)
        
    return np.array(centroid_history)

def append_centroid_history(centroids, i, centroid_history):
    if len(centroids) == 1:
        centroid_history.append(centroids[0])
        return
        
    if i == 0:
        if len(centroids) >= 1:
            centroid_history.append(centroids[0])  # pick the first centroid of the first frame. Not the most accurate but yolo
        else:
            centroid_history.append(None)

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
                
def plot_centroid_history_hexbin(interp_history):
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


def get_centroid_area_history(files, debug=True, key_format="simple"):
    """
    Primary function to be called for obtaining history in the following format:
    {
        0: {
            0: ...,
            1: ...,
        },
        1: { ... }
    }
    Arguments:
        files {[str]} -- up to 30 mins of files, since we decided that recalibration of godec should be done every 30 mins
    """
    annotated_images = []
    centroid_history = []
    M, LS, L, S, width, height = bs_godec(files)
    
    for i in range(len(files)):
        img = get_frame_GREY(files[i])
        L_frame = normalize_frame(L[:, i].reshape(width, height).T)
        S_frame = normalize_frame(S[:, i].reshape(width, height).T)
        img = cleaned_godec_img(L_frame, S_frame, get_frame(files[i]))
        images, centroids = postprocess_img(img)
        
        annotated_img = images[-1]
        annotated_images.append(annotated_img)
        
        append_centroid_history(centroids, i, centroid_history)
    
    interpolated_centroid_history = Interpolator(centroid_history).history
    centroid_area_array = [get_centroid_area_number(cnt) for cnt in interpolated_centroid_history]
    area_counter = Counter(centroid_area_array)
    
    for i in range(8):
        if i not in area_counter:
            area_counter[i] = 0
            
    if key_format == "simple":
        area_movement_counter = Counter()
        
        for i in range(len(centroid_area_array) - 1):
            from_area = str(centroid_area_array[i])
            to_area = str(centroid_area_array[i+1])
            label = from_area+"→"+to_area
            area_movement_counter[label] += 1
        
    elif key_format == "from_to":
        area_movement_counter = {"None": Counter()}
        for i in range(8):
            area_movement_counter[str(i)] = Counter()
            
        for i in range(len(centroid_area_array) - 1):
            from_area = str(centroid_area_array[i])
            to_area = str(centroid_area_array[i+1])
            area_movement_counter[from_area][to_area] += 1
            
    if debug:
        return area_counter, area_movement_counter, centroid_area_array, annotated_images
    return area_movement_counter

def get_centroid_displacement_history(files, debug=True):
    """
    Primary function for getting history of the following format:   
    {
        "time": [x1, x2, ..., xn]
    }

    where xi is the displacement from xi-1 to xi frame
    Instead of geting centroid area number for each centroid, 
    calculate displacement directly.
    
    Args:
        files ([type]): [description]
        debug (bool, optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    annotated_images = []
    centroid_history = []
    M, LS, L, S, width, height = bs_godec(files)
    
    for i in range(len(files)):
        img = get_frame_GREY(files[i])
        L_frame = normalize_frame(L[:, i].reshape(width, height).T)
        S_frame = normalize_frame(S[:, i].reshape(width, height).T)
        img = cleaned_godec_img(L_frame, S_frame, get_frame(files[i]))
        images, centroids = postprocess_img(img)
        
        annotated_img = images[-1]
        annotated_images.append(annotated_img)
        
        append_centroid_history(centroids, i, centroid_history)
    
    interpolated_centroid_history = Interpolator(centroid_history).history
    
    displacement = 0
    
    # plotting
    if debug:
        p = figure()
        r = p.circle([], [])
        curdoc().add_root(p)
        
    for i in range(len(interpolated_centroid_history) - 1):
        prev_centroid = interpolated_centroid_history[i+1]
        curr_centroid = interpolated_centroid_history[i]
        if not (prev_centroid == None or curr_centroid == None): 
            curr_displacement = np.sqrt((prev_centroid[0]-curr_centroid[0])**2 + (prev_centroid[1]-curr_centroid[1])**2)
            displacement += curr_displacement
            if debug:
                r.data_source.stream({'x': [i], 'y': [curr_displacement]})
            
    key = basename(files[0])
    return {key: displacement}

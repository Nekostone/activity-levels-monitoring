import cv2
import numpy as np
from file_utils import load_npy, get_all_data_filenames
import os
from os.path import isfile, join
import time
from visualizer import init_heatmap, update_heatmap
import matplotlib.pyplot as plt

data_path = "./data/teck_first_trial"
files = get_all_data_filenames(data_path)
print("Number of frames found in ", data_path, ": ", len(files))

def get_frame(filename):
    return load_npy(join(data_path, filename))

# for plotting the heatmap of original data

def get_init_heatmap_plot():
    array_shape = (24,32)
    min_value = 25
    max_value = 40
    plot = init_heatmap("Grideye Heatmap", array_shape, min_value, max_value)
    return plot

"""
Naive Algorithm or determining which area the person is at inside a single room
- the room is a 24x32 pixel array
- the room is divided into 8 areas, resulting in a 12x8 array each
- if the area has at least 60% pixels that are considered human temperature range (34 - 40) 
  including device tolerance of +- 1.5 degree celsius, then we consider that a human is there
"""

def divide_grid_into_areas(array):
    """
    Divides a 24x32 array into 8x12x8 array
    :return: 8x12x8 array
    """
    print(array)
    result = np.zeros((8, 12, 8))
    block_number = 0
    for i in range(2):
        for j in range(4):
            result[block_number] = array[i * 12:(i + 1) * 12, j * 8:(j + 1) * 8]
            block_number += 1
    return result

def naive_detection_by_frame(frame):
    divided_grid = divide_grid_into_areas(frame)
    areas_person_is_in = {}
    max_temp = 40
    if np.amax(frame) < max_temp:
        max_temp = np.amax(frame)
    for i in range(8):
        area = divided_grid[i]
        filtered_area = area[np.logical_and(area >= (max_temp - 2), (area <= max_temp))]
        num_hot_pixels = filtered_area.size
        person_is_in_area = num_hot_pixels > 0.6*(area.size)
        areas_person_is_in[i] = {"in_area": person_is_in_area, "likelihood": num_hot_pixels/area.size}
    
    total_percentage_hot_pixels = sum([areas_person_is_in[x]["likelihood"] for x in areas_person_is_in])
   
    for x in areas_person_is_in:
        areas_person_is_in[x]["likelihood"] = areas_person_is_in[x]["likelihood"]/total_percentage_hot_pixels

    return areas_person_is_in

def visualize_likelihood_plot(areas_person_is_in):
    to_plot = [[areas_person_is_in[i]["likelihood"] for i in range(4)], [areas_person_is_in[i]["likelihood"] for i in range(4,8)]]
    fig, ax = plt.subplots()
    im = ax.imshow(to_plot, cmap="autumn")

    ax.set_xticks(np.arange(4))
    ax.set_yticks(np.arange(2))
    # Loop over data dimensions and create text annotations.
    for i in range(2):
        for j in range(4):
            text = ax.text(j, i, "{:.2f}".format(to_plot[i][j]), ha="center", va="center", color="black")

    ax.set_title("Likelihood plot")
    fig.tight_layout()
    plt.show()
    plt.colorbar()

# testing of naive detection algorithm
# view normal heatmap next to percentage plot
test_frame = get_frame(files[5])
areas_person_is_in = naive_detection_by_frame(test_frame)
fig, ax = plt.subplots()
im = ax.imshow(test_frame, cmap="hot")
visualize_likelihood_plot(areas_person_is_in)

"""
Optical Flow Algorithm
"""
def convert_temp_to_rgb(df):
    max_temp = np.amax(df)
    min_temp = np.amin(df)
    result = (df - min_temp) / (max_temp - min_temp) * 255
    return  result 

def get_frame_in_rgb(filename):
    return convert_temp_to_rgb(get_frame(filename))

def run_optical_flow(files):
    plot = get_init_heatmap_plot()
    frame1 = get_frame(files[0])
    prev = get_frame_in_rgb(files[0])
    test = cv2.cvtColor(frame1.astype("uint8"), cv2.COLOR_GRAY2BGR)
    hsv = np.zeros_like(test)
    hsv[...,1] = 255
    window_name = "optical_flow"

    counter = 1

    while counter < len(files):
        next = get_frame_in_rgb(files[counter])
        flow = cv2.calcOpticalFlowFarneback(prev,next, None, 0.5, 3, 15, 3, 5, 1.2, 0) # to tune parameters
        mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
        hsv[...,0] = ang*180/np.pi/2
        hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
        
        # plotting of grayscale flowmap and data heatmap
        cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 120, 180)
        cv2.imshow(window_name,hsv[...,2])
        update_heatmap(get_frame(files[counter]), plot)
        
        prev = next
        k = cv2.waitKey(30) & 0xff
        time.sleep(1)
        print(counter)
        
        counter += 1

# run_optical_flow(files)
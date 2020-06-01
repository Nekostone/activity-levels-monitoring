import os
import time
from os.path import isfile, join

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

from file_utils import (get_all_files, get_frame, get_frame_GREY,
                        get_frame_RGB, normalize_frame)
from visualizer import init_heatmap, update_heatmap

def get_init_heatmap_plot():
    array_shape = (24,32)
    min_value = 25
    max_value = 40
    return init_heatmap("MLX90640 Heatmap", array_shape, min_value, max_value)

def get_init_likelihood_plot():
    array_shape = (2,4)
    min_value = 0
    max_value = 1
    return init_heatmap("Likelihood Plot", array_shape, min_value, max_value)

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
    result = np.zeros((8, 12, 8))
    block_number = 0
    for i in range(2):
        for j in range(4):
            result[block_number] = array[i * 12:(i + 1) * 12, j * 8:(j + 1) * 8]
            block_number += 1
    return result

def naive_binary_likelihood_by_frame(frame):
    """
    :param: 24x32 frame
    :return: { int: bool, ... int: bool }
    """
    divided_grid = divide_grid_into_areas(frame)
    areas_person_is_in = {}
    max_temp = 40
    if np.amax(frame) < max_temp:
        max_temp = np.amax(frame)
    for i in range(8):
        area = divided_grid[i]
        filtered_area = area[np.logical_and(area >= (max_temp - 2), (area <= max_temp))]
        num_hot_pixels = filtered_area.size
        areas_person_is_in[i] =  num_hot_pixels/area.size

    total_percentage_hot_pixels = sum(areas_person_is_in.values())
    max_likelihood = 0

    if total_percentage_hot_pixels == 0:
        for x in areas_person_is_in:
            areas_person_is_in[x] = 0
            
        return {i : 0 for i in range(8)}

    else:
        for x in areas_person_is_in:
            likelihood = areas_person_is_in[x]/total_percentage_hot_pixels
            areas_person_is_in[x] = likelihood
            if likelihood > max_likelihood: 
                max_likelihood = likelihood

        return {i : (1 if areas_person_is_in[i] == max_likelihood else 0) for i in range(8) }
    

def naive_detection_by_frame(frame):
    """
    :param: a single 24x32 frame
    :return: areas_person_is_in - a dictionary of the structure
        {
            0: {
                "in_area": True, # criteria based on >0.6 of area is hot
                "likelihood": 0.83
            },
            ...,
            8: {...}
        }  
    """
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
    
    if total_percentage_hot_pixels == 0:
        for x in areas_person_is_in:
            areas_person_is_in[x]["likelihood"] = 0

    else:
        for x in areas_person_is_in:
            areas_person_is_in[x]["likelihood"] = areas_person_is_in[x]["likelihood"]/total_percentage_hot_pixels

    return areas_person_is_in

def naive_detection_from_files(data_path, startIndex=None, endIndex=None):
    heatmap_plot = get_init_heatmap_plot()
    likelihood_plot = get_init_likelihood_plot()
    files = get_all_files(data_path)
    if startIndex == None:
        startIndex = 0
    if endIndex == None:
        endIndex = len(files)
    print(startIndex, endIndex)
    for i in range(startIndex, endIndex):
        frame = get_frame(files[i])
        areas_person_is_in = naive_detection_by_frame(frame)
        likelihood_array = [[areas_person_is_in[i]["likelihood"] for i in range(4)], [areas_person_is_in[i]["likelihood"] for i in range(4,8)]]
        
        # if debugging with plot view
        update_heatmap(frame, heatmap_plot)
        update_heatmap(likelihood_array, likelihood_plot)


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

"""
Time Series Analysis Functions
"""

def analyze_by_period(files, num_frames=60*30):
    time_person_spent_in_areas = defaultdict(int)
    counter = 0
    while counter < num_frames:
        frame = get_frame(files[counter])
        areas_person_is_in = naive_binary_likelihood_by_frame(frame)
        for area in areas_person_is_in:
            if areas_person_is_in[area]:
                time_person_spent_in_areas[area] += 1
        counter += 1
    total_time_spent_in_room = sum(time_person_spent_in_areas.values())
    time_person_spent_in_areas = {i:  time_person_spent_in_areas[i]/total_time_spent_in_room for i in range(8)}    
    return time_person_spent_in_areas

def analyze():
    total_frames = len(files)
    counter = 0
    analysis_results = {}
    while counter < total_frames:
        num_frames = 60*30
        if num_frames + counter >= total_frames:
            num_frames = total_frames - counter
        
        start_time = files[counter].split("_grideye")[0]
        print("Analyzing 30min interval from", start_time,)
        one_span_frames = files[counter: counter+num_frames]
        one_span_analysis = analyze_by_period(one_span_frames, num_frames)
        analysis_results[start_time] = one_span_analysis
        counter += num_frames
    return analysis_results


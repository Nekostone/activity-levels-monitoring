import os
import time
from os.path import isfile, join

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

from background_subtraction import bs_godec
from file_utils import (get_all_files, get_frame, get_frame_GREY,
                        get_frame_RGB, normalize_frame)
from visualizer import init_heatmap, update_heatmap

# for plotting the heatmap of original data

def get_init_heatmap_plot():
    array_shape = (24,32)
    min_value = 25
    max_value = 40
    return init_heatmap("Grideye Heatmap", array_shape, min_value, max_value)

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
Optical Flow Algorithm
"""

def optical_flow_lk(files):
    print("Performing Lucas-Kanade Optical Flow")
    plot = get_init_heatmap_plot()

    # params for ShiTomasi corner detection
    feature_params = dict( maxCorners = 4,
                        qualityLevel = 0.2,
                        minDistance = 6,
                        blockSize = 4 )
    # Parameters for lucas kanade optical flow
    lk_params = dict( winSize  = (3,3),
                    maxLevel = 3,
                    criteria = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

    # Take first frame and find corners in it
    first_frame_gray = get_frame_GREY(files[0])
    prevPts = cv.goodFeaturesToTrack(first_frame_gray, mask = None, **feature_params)
    color = np.random.randint(0,255,(100,3))
    # Create a mask image for drawing purposes
    mask = np.zeros_like(first_frame_gray)
    counter = 1
    prevImg = first_frame_gray
    while counter < len(files):
        frame = get_frame_GREY(files[counter])
        cleaned_frame = bs_godec(frame)
        nextImg = frame.copy()
        update_heatmap(get_frame(files[counter]), plot)
        # grayscale but uint8??
        nextPts, status, err = cv.calcOpticalFlowPyrLK(prevImg, nextImg, prevPts, None, **lk_params)
        if nextPts is None:
            prevPts = cv.goodFeaturesToTrack(frame, mask = None, **feature_params)
            nextPts, status, err = cv.calcOpticalFlowPyrLK(prevImg, nextImg, prevPts, None, **lk_params)
     
        # Select good points
        # each element of the vector is set to 1 if the flow for the corresponding features has been found, otherwise, it is set to 0.
        good_new = nextPts[status==1]
        good_old = prevPts[status==1]
    
        # annotate the tracks
        for i,(new,old) in enumerate(zip(good_new, good_old)):
            a,b = new.ravel()
            c,d = old.ravel()
            mask = cv.line(mask, (a,b),(c,d), color[i].tolist(), 2)
            frame = cv.circle(frame,(a,b),5,color[i].tolist(),-1)
        img = cv.add(frame,mask)
        cv.imshow('frame',img)
        k = cv.waitKey(30) & 0xff
        if k == 27:
            break
        # Now update the previous frame and previous points
        prevImg = nextImg.copy()
        prevPts = good_new.reshape(-1,1,2)
        counter +=1
    

def optical_flow_dense(files):
    print("Performing Dense Optical Flow")
    plot = get_init_heatmap_plot()
    first_frame = get_frame(files[0])
    prev_rgb = get_frame_RGB(files[0])
    test = cv.cvtColor(first_frame.astype("uint8"), cv.COLOR_GRAY2BGR)
    hsv = np.zeros_like(test)
    hsv[...,1] = 255
    window_name = "optical_flow"

    counter = 1

    while counter < len(files):
        next_rgb = get_frame_RGB(files[counter])
        flow = cv.calcOpticalFlowFarneback(prev_rgb,next_rgb, None, 0.5, 3, 15, 3, 5, 1.2, 0) # to tune parameters
        mag, ang = cv.cartToPolar(flow[...,0], flow[...,1])
        hsv[...,0] = ang*180/np.pi/2
        hsv[...,2] = cv.normalize(mag,None,0,255,cv.NORM_MINMAX)
        
        # plotting of grayscale flowmap and data heatmap
        cv.namedWindow(window_name,cv.WINDOW_NORMAL)
        cv.resizeWindow(window_name, 120, 180)
        cv.imshow(window_name,hsv)
        update_heatmap(get_frame(files[counter]), plot)
        
        prev_rgb = next_rgb
        k = cv.waitKey(30) & 0xff
        # time.sleep(0.5)
        
        counter += 1

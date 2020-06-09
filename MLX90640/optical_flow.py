import os
import time
from os.path import isfile, join

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

from background_subtraction import bs_godec
from file_utils import (get_all_files, get_frame, get_frame_GREY,
                        get_frame_RGB, normalize_frame)
from naive_presence_detection import get_init_heatmap_plot
from visualizer import init_heatmap, update_heatmap


def optical_flow_lk(files, track_length=10, detect_interval=5):
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
    counter = 1
    prevImg = first_frame_gray
    while counter < len(files):
        frame = get_frame_GREY(files[counter])
        nextImg = frame.copy()
        update_heatmap(get_frame(files[counter]), plot)
        nextPts, status, err = cv.calcOpticalFlowPyrLK(prevImg, nextImg, prevPts, None, **lk_params)
        displacement = nextPts - prevPts
        if (abs(displacement) > 3).any():
            print(displacement)
            plt.xlabel("Displacement: {}".format(displacement))
        else:
            plt.xlabel("Displacement in x/y lower than 3 ")
        if nextPts is None:
            print("Target not moving")
            prevPts = cv.goodFeaturesToTrack(frame, mask = None, **feature_params)
            nextPts, status, err = cv.calcOpticalFlowPyrLK(prevImg, nextImg, prevPts, None, **lk_params)
     
        # Select good points
        # each element of the vector is set to 1 if the flow for the corresponding features has been found, otherwise, it is set to 0.
        good_new = nextPts[status==1]
        good_old = prevPts[status==1]
    
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

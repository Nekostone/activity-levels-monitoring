import os
import time
from os.path import isfile, join

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

from file_utils import (get_all_files, get_frame, get_frame_GREY,
                        get_frame_RGB, normalize_frame)
from visualizer import init_heatmap, update_heatmap
from naive_presence_detection import get_init_heatmap_plot
from background_subtraction import bs_godec


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
        nextImg = frame.copy()
        update_heatmap(get_frame(files[counter]), plot)
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

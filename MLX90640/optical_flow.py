import os
import time
from os.path import isfile, join

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

from background_subtraction import bs_godec, get_godec_frame, postprocess_img
from file_utils import (create_folder_if_absent, get_all_files, get_frame,
                        get_frame_GREY, get_frame_RGB, normalize_frame)
from naive_presence_detection import get_init_heatmap_plot
from visualizer import (init_comparison_plot, init_heatmap,
                        update_comparison_plot, update_heatmap)


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
    # TODO: instead of using good features to track, possibly just use contour points directly
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
    # Perform Godec first on all frames
    M, LS, L, S, width, height = bs_godec(files)
    first_frame = get_frame(files[0])
    
    # frames to be compared is after godec and postprocessing
    godec_frame, probability = get_godec_frame(M, L, S, width, height, 0)
    img, centroids = postprocess_img(godec_frame, all_images=False)
    prev_gray = img
    ims = init_comparison_plot(first_frame, ["Original", "Thresholded", "FlowS"], 1,3)
    test = cv.cvtColor(first_frame.astype("uint8"), cv.COLOR_GRAY2BGR)
    hsv_mask = np.zeros_like(test)
    hsv_mask[...,1] = 255
    window_name = "Dense Optical Flow"

    counter = 1

    while counter < len(files):
        print(counter)
        godec_frame, probability = get_godec_frame(M, L, S, width, height, counter)
        img, centroids = postprocess_img(godec_frame, all_images=False)
        next_gray = img
        flow = cv.calcOpticalFlowFarneback(prev_gray,next_gray, 
                                           None, 
                                           pyr_scale = 0.5, 
                                           levels = 5, 
                                           winsize = 11, 
                                           iterations = 5, 
                                           poly_n = 5, 
                                           poly_sigma = 1.1, 
                                           flags = 0)
        magnitude, angle = cv.cartToPolar(flow[...,0], flow[...,1])
        hsv_mask[...,0] = angle*180/np.pi/2 # Set image hue according to the optical flow direction
        hsv_mask[...,2] = cv.normalize(magnitude, None, 0, 255, cv.NORM_MINMAX) # Set image value according to the optical flow magnitude (normalized)
        
        # plotting of grayscale flowmap and data heatmap
        update_comparison_plot(ims, [get_frame(files[counter]), next_gray, hsv_mask])
        plt.title("Max Magnitude :" + str(np.amax(magnitude)) + "\nMax Angle:" + str(np.amax(angle)))
        create_folder_if_absent("optical_flow_pics")
        plt.savefig("optical_flow_pics/{}.png".format(counter))
        prev_gray = next_gray
        k = cv.waitKey(30) & 0xff
        counter += 1

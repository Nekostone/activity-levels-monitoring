import cv2
import numpy as np
from file_utils import load_npy, get_all_data_filenames
import os
from os.path import isfile, join
import time
from visualizer import init_heatmap, update_heatmap

data_path = "./data"
files = get_all_data_filenames(data_path)
print(f"Number of frames found in {data_path}: {len(files)}")

# for plotting the heatmap of original data
array_shape = (24,32)
min_value = 30
max_value = 40
plot = init_heatmap("Grideye Heatmap", array_shape, min_value, max_value)

# for plotting the optical flow map

def get_frame(filename):
    return load_npy(join(data_path, filename))

def convert_temp_to_rgb(df):
    max_temp = np.amax(df)
    min_temp = np.amin(df)
    result = (df - min_temp) / (max_temp - min_temp) * 255
    return  result 

def get_frame_in_rgb(filename):
    return convert_temp_to_rgb(get_frame(filename))

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
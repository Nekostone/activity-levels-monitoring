import numpy as np

from background_subtraction_test import test_postprocess_img
from centroid_history import (Interpolator, get_centroid_area_history,
                              get_centroid_area_number, get_centroid_history,
                              input_target_centroid_area,
                              plot_centroid_history_hexbin)
from file_utils import get_all_files
from visualizer import init_heatmap, update_heatmap
import matplotlib.pyplot as plt

data = "data/teck_walk_out_and_in"
files = get_all_files(data)

def test_input_target_centroid_area():
    input_target_centroid_area()
    
def test_get_centroid_area_number():
    centroid = (0,0)
    print("Area number for centroid ", centroid, " is ", get_centroid_area_number(centroid))
    centroid = (12,0)
    print("Area number for centroid ", centroid, " is ", get_centroid_area_number(centroid))
    centroid = (0,12)
    print("Area number for centroid ", centroid, " is ", get_centroid_area_number(centroid))
    centroid = (6,24)
    print("Area number for centroid ", centroid, " is ", get_centroid_area_number(centroid))
    
def test_get_centroid_area_number_from_postprocess(file):
    thresholded_img, centroids = test_postprocess_img(file, plot=True)
    centroid = centroids[0]
    print("Area number for centroid based on contours ", centroid, " is ", get_centroid_area_number(centroid))

def test_get_centroid_history(plot=False):
    history = get_centroid_history(files)
    interp = Interpolator(history)
    for a in range(len(history)):
        interp.none_checker(history[a], a)
    print("Original History")
    print(history)
    print("\n")
    print("Interpolated History")
    print(interp.history)
    if plot:
        plot_centroid_history_hexbin(interp.history)
        
def test_get_centroid_area_history(files):
    area_counter, area_movement_counter, centroid_area_numbers, annotated_images = get_centroid_area_history(files)
    assert len(centroid_area_numbers) == len(annotated_images)
        
    print(area_counter)
    print(area_movement_counter)
    
    contours_plot = init_heatmap("Detected Contours", (24,32), show=True)
    track_plot = init_heatmap("Tracked Centroid", (2, 4), min_value=0, max_value=1, show=True)
    
    
    area_number_frames = []
    for i in range(len(centroid_area_numbers)):
        area_number = centroid_area_numbers[i]
        frame = np.zeros(8)
        frame[area_number] = 1
        frame = frame.reshape((2,4))
        update_heatmap(frame, track_plot)
        update_heatmap(annotated_images[i], contours_plot)
        
# test_input_target_centroid_area()
# test_get_centroid_history(plot=True)
test_get_centroid_area_history(files)

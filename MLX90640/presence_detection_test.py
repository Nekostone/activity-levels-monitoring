import matplotlib.pyplot as plt

from file_utils import get_all_files
from presence_detection import (get_frame, naive_binary_likelihood_by_frame,
                                naive_detection_by_frame,
                                naive_detection_from_files,
                                optical_flow_dense, optical_flow_lk,
                                visualize_likelihood_plot)

data_path = "./data/teck_walk_out_and_in" # dirty data with movement
# data_path = "./data/sw_second_trial" # very dirty data with no movement
files = get_all_files(data_path)
print("Number of frames found in ", data_path, ": ", len(files))

"""
Naive Presence Detection Tests
"""

def test_naive_one_frame():
    # view normal heatmap next to percentage plot
    test_frame = get_frame(files[60*20])
    areas_person_is_in = naive_detection_by_frame(test_frame)
    fig, ax = plt.subplots()
    im = ax.imshow(test_frame, cmap="hot")
    visualize_likelihood_plot(areas_person_is_in)

def test_naive_many_frames():
    naive_detection_from_files(files, 7200, 12000)

def test_naive_all_frames():
    naive_detection_from_files(files)

def test_naive_binary_likelihood():
    test_frame = get_frame(files[60*20])
    result = naive_binary_likelihood_by_frame(test_frame)
    
""" 
Optical Flow Tests
"""
def test_opticalflow_lk():
    optical_flow_lk(files)
    
def test_opticalflow_dense():
    optical_flow_dense(files)

test_opticalflow_lk()
import math
import os
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from background_subtraction import bs_godec, cleaned_godec_img, postprocess_img
from centroid_history import Interpolator, append_centroid_history
from file_utils import (basename, create_folder_if_absent, get_all_files,
                        get_frame_GREY, normalize_frame)
from naive_presence_detection import divide_grid_into_areas


def get_centroid_area_number(centroid):
    if centroid != None:
        x, y = centroid
        return x // 8 + y // 12
    return None

def get_centroid_area_history(files):
    """
    -  Centroid Tracking
    - Background Subtraction Pipeline
    - Return something for analysis

    Arguments:
        files {[str]} -- up to 30 mins of files, since we decided that recalibration of godec should be done every 30 mins
    """
    centroid_history = []
    M, LS, L, S, width, height = bs_godec(files)
    for i in tqdm(range(len(files))):
        img = get_frame_GREY(files[i])
        L_frame = normalize_frame(L[:, i].reshape(width, height).T)
        S_frame = normalize_frame(S[:, i].reshape(width, height).T)
        img = cleaned_godec_img(L_frame, S_frame)
        thresholded_img, centroids = postprocess_img(img)
        append_centroid_history(centroids, i, centroid_history)
    
    interpolated_centroid_history = Interpolator(centroid_history).history
    centroid_area_numbers = [get_centroid_area_number(cnt) for cnt in interpolated_centroid_history]
    centroid_locations = Counter(centroid_area_numbers)
    for i in range(8):
        if i not in centroid_locations:
            centroid_locations[i] = 0
        
    return centroid_locations, interpolated_centroid_history

def analyze(files, num_calibration_frames=30):
    total_frames = len(files)
    analysis_results = {}
    # TODO: calibrate contour detection area
    # contour_areas = [postprocess_img(get_frame_GREY(f)) for f in files[0:num_calibration_frames]]
    # counter = num_calibration_frames
    counter = 0
    while counter < total_frames:
        num_frames = 60*30
        if num_frames + counter >= total_frames:
            num_frames = total_frames - counter
        filename, file_extension = os.path.splitext(files[counter])
        initial_timestamp = filename
        centroid_locations, interpolated_centroid_history = get_centroid_area_history(files[counter:counter+num_frames])

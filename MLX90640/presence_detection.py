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

# def analyze(files, num_calibration_frames=30):
#     total_frames = len(files)
#     analysis_results = {}
#     # TODO: calibrate contour detection area
#     # contour_areas = [postprocess_img(get_frame_GREY(f)) for f in files[0:num_calibration_frames]]
#     # counter = num_calibration_frames
#     counter = 0
#     while counter < total_frames:
#         num_frames = 60*30
#         if num_frames + counter >= total_frames:
#             num_frames = total_frames - counter
#         filename, file_extension = os.path.splitext(files[counter])
#         initial_timestamp = filename
#         centroid_locations, interpolated_centroid_history = get_centroid_area_history(files[counter:counter+num_frames])

import math
import os
from collections import Counter, defaultdict

import numpy as np

from centroid_history import get_centroid_area_history
from file_utils import basename


def analyze(files, num_frames_per_iteration=1800, key_format="from_to"):
    """
    Given an array of file names, 
    get centroid area history iteratively over 30 mins of frames.

    Args:
        files ([type]): [description]
        num_frames (int, optional): [description]. Defaults to 1800 (30 mins).
    """
    total_frames = len(files) # each frame is 1 second
    analysis_results = {}
    counter = 0
    
    while counter < total_frames:
        start_index = counter
        if counter + num_frames_per_iteration > total_frames:
            end_index = total_frames
        else:
            end_index = counter + num_frames_per_iteration
            
        area_movement_counter = get_centroid_area_history(files[start_index:end_index], debug=False, key_format="from_to")
        dictkey = basename(files[start_index])
        analysis_results[dictkey] = {
            "keyformat": "from_to",
            "duration": end_index - start_index,
            "analysis": area_movement_counter
        }
        counter += num_frames_per_iteration
    
    return analysis_results

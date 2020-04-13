from os import listdir
from os.path import isfile, join

import numpy as np
from visualizer import init_heatmap, update_heatmap
from file_utils import get_all_data_filenames
from file_utils import load_npy, get_frame

array_shape = (24,32)
min_value = 26
max_value = 40
plot = init_heatmap("Grideye Heatmap", array_shape, min_value, max_value)

files_path = "./data/teck_one_day_activity"
files = get_all_data_filenames(files_path)

print("Number of frames foundc in ", files_path, ": ", len(files))

counter = 0

while counter < len(files):
    print(counter)
    update_heatmap(get_frame(files[counter], files_path), plot)
    counter += 1

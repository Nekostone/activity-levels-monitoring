from os import listdir
from os.path import isfile, join

import numpy as np
from visualizer import init_heatmap, update_heatmap
from file_utils import load_npy

array_shape = (24,32)
min_value = 30
max_value = 40
plot = init_heatmap("Grideye Heatmap", array_shape, min_value, max_value)

files_path = "./data"
files = [f for f in listdir(files_path) if isfile(join(files_path, f))]

print(f"Number of frames found in {files_path}: {len(files)}")

def get_frame(filename):
    return load_npy(join(files_path, filename))

counter = 0

while counter < len(files):
    print(counter)
    update_heatmap(get_frame(files[counter]), plot)
    counter += 1

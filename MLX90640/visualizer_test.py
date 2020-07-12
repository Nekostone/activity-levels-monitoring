import matplotlib.pyplot as plt
import numpy as np

from file_utils import create_folder_if_absent, get_all_files, get_frame
from visualizer import init_heatmap, update_heatmap, write_gif_from_npy


"""
Test Visualizer
"""

def test_plot_random():
  array_shape = (24,32)
  min_value = 30
  max_value = 40
  plot = init_heatmap("Heatmap", array_shape, min_value, max_value)

  while True:
    frame = np.around(np.random.random(array_shape)*10+30,decimals=2)
    update_heatmap(frame, plot)

def test_plot(files):
  array_shape = (24,32)
  min_value = 30
  max_value = 40
  plot = init_heatmap("Heatmap", array_shape, min_value, max_value, debug=True)
  for f in files:
    frame = get_frame(f)
    update_heatmap(frame,plot)

def test_plot_without_labels(files):
  array_shape = (24,32)
  min_value = 25
  max_value = 40
  plot = init_heatmap("Heatmap", array_shape, min_value, max_value, debug=False)
  for i in range(len(files)):
    frame = get_frame(files[i])
    update_heatmap(frame,plot)
    create_folder_if_absent("testpics")
    plt.savefig("testpics/{}.png".format(i))

def test_create_folder_if_absent(folder):
  create_folder_if_absent(folder)


def test_write_gif_from_npy(files, name, start_index=0, end_index=0, fps=5):
    write_gif_from_npy(files, name, start_index, end_index, fps)

data_path = "data/teck_walk_out_and_in"
files = get_all_files(data_path)
test_plot_without_labels(files)
# test_write_gif_from_npy(files, data_path+".gif", end_index=len(files), fps=60)

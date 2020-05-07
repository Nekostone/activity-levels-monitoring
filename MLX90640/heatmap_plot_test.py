import numpy as np

from visualizer import init_heatmap, update_heatmap
from file_utils import get_frame, get_all_files

"""
Test Visualizer
"""

def test_plot_random():
  array_shape = (24,32)
  min_value = 30
  max_value = 40
  plot = init_heatmap("Grideye Heatmap", array_shape, min_value, max_value)

  while True:
    frame = np.around(np.random.random(array_shape)*10+30,decimals=2)
    update_heatmap(frame, plot)

def test_plot(files):
  array_shape = (24,32)
  min_value = 30
  max_value = 40
  plot = init_heatmap("Grideye Heatmap", array_shape, min_value, max_value)
  for f in files:
    frame = get_frame(f)
    update_heatmap(frame,plot)
    print(f)
  
data_path = "data/teck_empty_room_with_light_and_no_AC_curtains_open_10mins"
files = get_all_files(data_path)
test_plot(files)
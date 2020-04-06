import numpy as np
from visualizer import init_heatmap, update_heatmap

"""
Test Visualizer
"""
array_shape = (24,32)
min_value = 30
max_value = 40
plot = init_heatmap("Grideye Heatmap", array_shape, min_value, max_value)

while True:
  frame = np.around(np.random.random(array_shape)*10+30,decimals=2)
  update_heatmap(frame, plot)
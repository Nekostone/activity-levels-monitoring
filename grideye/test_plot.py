import numpy as np

from visualizer import init_heatmap, update_heatmap

"""
Test Visualizer
"""
plot = init_heatmap("Grideye Heatmap")

while True:
  frame = np.around(np.random.random((8,8))*10+30,decimals=2)
  print(frame)
  update_heatmap(frame, plot)
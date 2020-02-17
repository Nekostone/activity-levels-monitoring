import numpy as np
from visualizer import init_heatmap, update_heatmap

frame = np.random.random((8,8))
plot = init_heatmap(frame, "Grideye Heatmap")

while True:
  frame = np.around(np.random.random((8,8)),decimals=2)
  print(frame)
  update_heatmap(frame, plot)
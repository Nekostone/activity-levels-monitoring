import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import time

def init_heatmap(title, frame_shape, min_value, max_value):
  """
  Initialize the heatmap figure plot.
  Returns a plot tuple (fig, ax, im).
  """
  fig, ax = plt.subplots()
  frame = np.random.random(frame_shape)*0 # set empty array first
  im = plt.imshow(frame, cmap='hot', interpolation='nearest')
  plt.clim(min_value, max_value)
  plt.show(block=False)
  ax.set_title(title)
  plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")
  plt.colorbar()
  fig.canvas.draw()
  return fig, ax, im
  

def update_heatmap(frame, plot):
  """
  Given a plot tuple of (fig, ax, im), updates the plot with the new frame received.
  """
  fig, ax, im = plot
  im.set_array(frame)
  ax.draw_artist(ax.patch)
  im.figure.canvas.draw_idle()
  fig.canvas.flush_events()

def draw_section_borders_8(ax):
  for i in range(2):
        for j in range(4):
          lower_left_coords = (12*(i + 1)-1, 8*(j+1)-1)
          rect = patches.Rectangle(lower_left_coords, width=2, height=1, linewidth=1, edgecolor='b', facecolor='none')

def saveplot(save=False, save_path=""):
  if save and save_path: 
   plt.savefig(save_path)

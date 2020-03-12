from nptyping import Array
import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import time

def init_heatmap(title: str):
  """
  Initialize the heatmap figure plot.
  Returns a plot tuple (fig, ax, im).
  """
  # create the figure
  fig, ax = plt.subplots()
  frame = np.random.random((8,8))*0
  im = plt.imshow(frame, cmap='hot', interpolation='nearest')
  plt.clim(30,40)
  plt.show(block=False)
  ax.set_xticks(np.arange(8))
  ax.set_yticks(np.arange(8))
  ax.set_xticklabels(range(8))
  ax.set_yticklabels(range(8))
  ax.set_title(title)
  plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")
  plt.colorbar()
  return fig, ax, im
  

def update_heatmap(frame: Array[float, 8, 8], plot):
  """
  Given a plot tuple of (fig, ax, im), updates the plot with the new frame received.
  """
  fig, ax, im = plot
  im.set_array(frame)
  fig.canvas.draw()
  
def saveplot(save=False, save_path=""):
  if save and save_path: 
   plt.savefig(save_path)
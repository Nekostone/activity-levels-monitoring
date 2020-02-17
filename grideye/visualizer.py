from nptyping import Array
import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import time

def init_heatmap(frame: Array[float, 8, 8], title: str):
  """
  initialize the heatmap figure plot.
  the plot comes with a figure, axes and im.
  """
  # create the figure
  fig, ax = plt.subplots()
  im = ax.imshow(frame)
  plt.show(block=False)
  ax.set_xticks(np.arange(8))
  ax.set_yticks(np.arange(8))
  ax.set_xticklabels(range(8))
  ax.set_yticklabels(range(8))
  ax.set_title(title)
  plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")
  return fig, ax, im
  

def update_heatmap(frame: Array[float, 8, 8], plot):
  fig, ax, im = plot
  im.set_array(frame)
  # TODO: Add text, below code does not replace text, but adds a layer of text on top of existing text.
  # for i in range(8):
  #     for j in range(8):
  #         text = ax.text(j, i, np.around(frame[i, j],decimals=2),
  #                         ha="center", va="center", color="w")
  fig.canvas.draw()
  
def saveplot(save=False, save_path=""):
  if save and save_path: 
   plt.savefig(save_path)
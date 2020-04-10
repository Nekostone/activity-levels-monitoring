import os
import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import time
from datetime import datetime

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

def time_series_plot(time_series_dict):
  """
  Given a dictionary of the following format, plot the trend in likelihood
  {
    "[time]": {
      [room_number]: [likelihood] 
    }, ...
  }
  """
  fig, ax = plt.subplots()
  unformatted_intervals = sorted(list(time_series_dict.keys()))
  intervals = [datetime.strptime(t, "%Y%m%d_%H%M%S") for t in unformatted_intervals]
  start_time = intervals[0]
  title = "/".join([str(start_time.day), str(start_time.month), str(start_time.year)])
  ax.set_title(title)

  ax.set_xlabel("Time")
  xtick_labels = [str(t.hour) +":"+ str(t.minute) for t in intervals ]
  ax.set_xticklabels(xtick_labels)
  
  ax.set_ylabel("Percentage of time spent in 30min interval")
  ytick_labels = list(time_series_dict[unformatted_intervals[0]].keys())

  for i in range(len(ytick_labels)):
    y_values = [time_series_dict[x][str(i)] for x in unformatted_intervals]
    ax.plot(y_values, marker='o', label=ytick_labels[i])
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

  fig.tight_layout()
  plt.show()

def saveplot(save=False, save_path=""):
  if save and save_path: 
   plt.savefig(save_path)


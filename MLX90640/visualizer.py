import os
import time
from datetime import datetime

import matplotlib as mpl
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')

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

def datetime_to_string(datetime):
  return "/".join([str(datetime.day), str(datetime.month), str(datetime.year)])

def time_series_plot_from_json(time_series_dict, single_day=False, save=False):
  """
  Given a dictionary of the following format, plot the trend in likelihood
  {
    "[time]": {
      [room_number]: [likelihood] 
    }, ...
  }
  """
  fig, ax = plt.subplots()
  sorted_intervals = sorted(list(time_series_dict.keys()))
  formatted_intervals = [datetime.strptime(t, "%Y%m%d_%H%M%S") for t in sorted_intervals]
  start_time = formatted_intervals[0]
  formatted_start_time = datetime_to_string(start_time)
  if single_day:
    xticks = range(len(formatted_intervals)) # show ticks only for every half hour period
    xtick_labels = [str(t.hour) +":"+ str(t.minute) for t in formatted_intervals ]
    title = formatted_start_time

  else:
    end_time = formatted_intervals[-1]
    formatted_end_time = datetime_to_string(end_time)
    temp_labels = [str(t.hour) +":"+ str(t.minute) for t in formatted_intervals ]
    num_intervals = len(formatted_intervals)
    xticks = range(0,num_intervals,2) # show ticks only for every hour period
    xtick_labels = [temp_labels[i] for i in range(num_intervals) if i % 2 != 0]
    title = formatted_start_time + " to " + formatted_end_time

  ax.set_title(title)
  ax.set_xlabel("Time")
  ax.set_xticks(xticks)
  ax.set_xticklabels(xtick_labels)
  plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
  ax.set_ylabel("Percentage of time spent in 30min interval")
  ytick_labels = sorted(list(time_series_dict[sorted_intervals[0]].keys()))

  for label in ytick_labels:
    y_values = []
    for interval in sorted_intervals:
      time_series_dict[interval][label]
      y_values.append(time_series_dict[interval][label])
    ax.plot(y_values, marker='o', label=label)
 
  ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
  fig.tight_layout()
  if save:
    plt.savefig("./time_series_plt.png")
  plt.show()

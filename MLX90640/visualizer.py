import os
import time
from datetime import datetime

import imageio
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from file_utils import create_folder_if_absent, get_frame, optimize_size

"""
===========================================
Temperature Heatmap
===========================================
"""

def init_heatmap(title, frame_shape=(24,32), min_value=25, max_value=40, show=True):
  """
  Initialize the heatmap figure plot.
  Returns a plot tuple (fig, ax, im).
  """
  fig, ax = plt.subplots()
  frame = np.random.random(frame_shape)*0 # set empty array first
  im = plt.imshow(frame, cmap='hot', interpolation='nearest')
  plt.clim(min_value, max_value)
  if show:
    plt.show(block=False)
  ax.set_title(title)
  plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")
  plt.colorbar()
  fig.canvas.draw()
  return fig, ax, im
  

def update_heatmap(frame, plot):
  """
  Given a plot tuple of (fig, ax, im), 
  updates the plot with the new frame received.
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

"""
===========================================
Making GIFs
===========================================
"""
  
def write_gif(files, name, start=0, end=0, fps=1):
  """
  Primary function to write gifs.
  - If file type given is .npy (temperature npy arrays),
    then it will plot the heatmap and save these pics before making them into a gif.  
  - If file type given is .png (godec plots),
    then it will just make them into a gif directly.

  Arguments:
      files {string[]} -- result from get_all_files()
      name {string} -- name of the gif to be saved

  Keyword Arguments:
      start {int} -- index of files (default: {0})
      end {int} -- index of files (default: {0})
      fps {int} -- frames per second (default: {1})
  """
  filename, file_extension = os.path.splitext(files[0])
  create_folder_if_absent(os.path.dirname(files[0]))
  if file_extension == ".png":
    write_gif_from_pics(files, name, start=0, end=0, fps=1)
  elif file_extension == ".npy":
    write_gif_from_npy(files, name, start=0, end=0, fps=1)
  
def write_gif_from_npy(files, name, start=0, end=0, fps=1):
  print("Plotting from {} numpy files and writing gif of {}...".format(len(files), fps))
  plot = init_heatmap(name, show=False)
  end = end or len(files)
  with imageio.get_writer(name, mode='I', fps=fps) as writer:
    for i in tqdm(range(start, end)):
      f = get_frame(files[i])
      update_heatmap(f, plot)
      pic_name = "pics/"+files[i]+".png"
      plt.savefig(pic_name)
      writer.append_data(imageio.imread(pic_name))
  writer.close()
  print("Finished writing gif at {}.".format(name))
  optimize_size(name)
  
def write_gif_from_pics(files, name, start=0, end=0, fps=1):
  print("Converting {} pictures into a gif of {} fps...".format(len(files),fps))
  end = end or len(files)
  with imageio.get_writer(name, mode='I', fps=fps) as writer:
    for i in tqdm(range(start, end)):
      writer.append_data(imageio.imread(files[i]))
  writer.close()
  print("Finished writing gif at {}.".format(name))
  optimize_size(name)

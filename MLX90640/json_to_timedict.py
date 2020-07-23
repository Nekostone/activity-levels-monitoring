import json
import time
import scipy
import numpy as np


def name_to_time(filename, directory_sort=None):
    if directory_sort == "day":
      time_tuple = time.strptime(filename, "%Y.%m.%d")
    elif directory_sort == "hour":
      time_tuple = time.strptime(filename, "%Y.%m.%d_%H00")
    else:
      time_tuple = time.strptime(filename, "%Y.%m.%d_%H%M%S")
    return time_tuple


def padarray(A, size):
    t = size - len(A)
    return np.pad(A, pad_width=(0, t), mode='constant', constant_values=0)

def shift_to_30min(time):  # takes 24hr time format and rounds it down to the nearest 30 min block
    if int(time[2:4]) > 30:
        shifted_time = time[0:2] + '30'
    elif int(time[2:4]) < 30:
        shifted_time = time[0:2] + '00'
    else:
        return time

    return shifted_time

def json_to_timedict(json_path, interpolate=False, shift_30min=False):
    with open(json_path) as file:
        data = json.load(file)
        keylist = []
        data = dict(sorted(data.items()))   # sorts the timestamp dicts by timestamp
        newdict = {}
        for i in data:
            if len(data[i]) < 1800:
                if interpolate:  # if you wanna use this to interpolate values:
                    data[i] = scipy.signal.resample(data[i], 1800)
            split = i.split('_')
            split_time = split[1]
            split_time = split_time[:-2]

            if shift_30min:  # if you wanna shift the timestamps to approximate the 30 min blocks
                split_time = shift_to_30min(split_time)

            newdict[split_time] = data[i].tolist()

        return newdict

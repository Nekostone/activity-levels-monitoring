import json
import time

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


def json_to_timedict(json_path):
    with open(json_path) as file:
        data = json.load(file)
        keylist = []
        data = dict(sorted(data.items()))
        newdict = {}
        for i in data:
            if len(data[i]) < 1800:
                data[i] = padarray(data[i], 1800)
            split = i.split('_')
            split_time = split[1]
            split_time = split_time[:-2]

            if int(split_time[2:4]) > 30:
                split_time = split_time[0:2] + '30'
            elif int(split_time[2:4]) < 30:
                split_time = split_time[0:2] + '00'
            newdict[split_time] = data[i]

        return newdict

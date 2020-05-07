import csv
import json
import time
from os import listdir
from os.path import isfile, join

import cv2
import numpy as np


def save_as_npy(df, data_path):
  filename = time.strftime("%Y%m%d_%H%M%S",time.localtime(time.time()))
  np.save(join(data_path,filename), df)


def get_all_files(data_path):
    return sorted([join(data_path, f) for f in listdir(data_path) if isfile(join(data_path, f))])

def write_to_json(content, filename):
  with open(filename, 'w') as outfile:
    json.dump(content, outfile)

def load_json(filename):
  with open(filename) as json_file:
    return json.load(json_file)

def get_frame(filename):
    return np.load(filename)

def normalize_frame(df):
    return cv2.normalize(df, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

def get_frame_GREY(filename):
    return normalize_frame(get_frame(filename))

def get_frame_RGB(filename):
    return get_frame_GREY(filename) * 255

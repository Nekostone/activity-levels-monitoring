import csv
import json
import time
from os import listdir, makedirs
from os.path import dirname, exists, getsize, isfile, join, basename

import cv2 as cv
import numpy as np
from pygifsicle import optimize

def save_npy(df, data_path, name=None, directory_sort=None):
  file = name or time.strftime("%Y.%m.%d_%H%M%S",time.localtime(time.time()))
  save_path = data_path
  if directory_sort == "day":
    save_path = time.strftime("%Y.%m.%d",time.localtime(time.time()))
    save_path = join(data_path, save_path)
    create_folder_if_absent(save_path)
  elif directory_sort == "hour":
    save_path = time.strftime("%Y.%m.%d_%H00",time.localtime(time.time()))
    save_path = join(data_path, save_path)
    create_folder_if_absent(save_path)
    
  np.save(join(save_path,file), df)

def get_all_files(data_path):
    return sorted([join(data_path, f) for f in listdir(data_path) if isfile(join(data_path, f))])

def write_to_json(content, file):
  with open(file, 'w') as outfile:
    json.dump(content, outfile)

def load_json(file):
  with open(file) as json_file:
    return json.load(json_file)

def get_frame(file):
    return np.load(file)

def normalize_frame(df):
    return cv.normalize(df, None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)

def get_frame_GREY(file):
    return normalize_frame(get_frame(file))

def get_frame_RGB(file):
    return get_frame_GREY(file) * 255
  
def folder_path(file):
    return dirname(file)
  
def base_folder(file):
  return basename(file)

def create_folder_if_absent(folder_name):
  if not exists(folder_name):
    makedirs(folder_name)
    print("Folder ",folder_name, " does not exist. Created it to save files.")
    
def optimize_size(file):
  print("Optimizing size...")
  before_size = getsize(file)
  optimize(file)
  after_size = getsize(file)
  print("Original Size: {}. Optimized to {}.".format(before_size, after_size))

  
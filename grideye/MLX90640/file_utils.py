import csv
import numpy as np
import time
from os import listdir
from os.path import isfile, join
import json

def save_as_npy(df, data_path):
  filename = time.strftime("%Y%m%d_%H%M%S",time.localtime(time.time())) + "_grideye"
  np.save(join(data_path,filename), df)
  
def load_npy(filename):
  return np.load(filename)

def get_frame(filename, data_path):
    return load_npy(join(data_path, filename))

def get_all_data_filenames(data_path):
    return sorted([f for f in listdir(data_path) if isfile(join(data_path, f))])

def write_to_json(content, filename):
  with open(filename, 'w') as outfile:
    json.dump(content, outfile)

def load_json(filename):
  with open(filename) as json_file:
    return json.load(json_file)
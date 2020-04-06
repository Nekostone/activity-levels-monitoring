import csv
import numpy as np
import time
from os import listdir
from os.path import isfile, join
from nptyping import Array

def save_as_npy(df):
  folder_path = "data/"
  filename = time.strftime(folder_path + "%Y%m%d_%H%M%S",time.localtime(time.time())) + "_grideye"
  np.save(filename, df)
  print("Saved in ", filename, ".npy")
  
def load_npy(filename: str):
  return np.load(filename)

def get_all_data_filenames(dataPath: str):
  return [f for f in listdir(dataPath) if isfile(join(dataPath, f))]
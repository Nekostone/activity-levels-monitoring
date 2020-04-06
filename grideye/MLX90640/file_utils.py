import csv
import numpy as np
import time

def save_as_npy(df):
  folder_path = "data/"
  filename = time.strftime(folder_path + "%Y%m%d_%H%M%S",time.localtime(time.time())) + "_grideye"
  np.save(filename, df)
  print("Saved in ", filename, ".npy")
  
def load_npy(filename):
  arr = np.load(filename)
  return arr 

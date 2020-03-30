import csv
import numpy as np
import time
from nptyping import Array

def to_csv(data: Array[float,24,32], filePath: str):
  curr_time = time.time()
  data.insert(0, curr_time)
  with open(filePath, "a", newline = '') as f:
      writer = csv.writer(f, delimiter=",")
      writer.writerow(data)
          
def parse_csv(filePath: str):
  with open(filePath, "r") as f:
      reader = csv.reader(f, delimiter=",")
      for row in reader:
          timestamp = row[0]
          temp_values = row[1]
          
          # TODO: get the 2D array from csv.
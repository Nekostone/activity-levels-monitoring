import csv
import numpy as np
with open("test_data.csv", "r") as f:
    reader = csv.reader(f, delimiter=",")
    for row in reader:
        timestamp = row[0]
        # print(timestamp)
        temp_values = row[1]
        # print(temp_values)
        print(temp_values)

        obj = np.fromstring(temp_values, float)
        # obj = ast.literal_eval(temp_values)
        print(obj)
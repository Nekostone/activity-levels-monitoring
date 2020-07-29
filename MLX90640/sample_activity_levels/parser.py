import re
import csv


f = open("Log.txt", "r")
f2 = open("log.csv", "w+")

with f2:
    writer = csv.writer(f2)
    lines = [l for l in (line.strip() for line in f) if l]
    for x in lines:
        y = re.search("^T tt.*\[.*\].*$", x)
        if y:
            time = x.split("T tt, ")[1]
            print(time)
        elif x != "\n":
            print(x)
            writer.writerow([time, x])


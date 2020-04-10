from file_utils import load_json
from visualizer import time_series_plot
data = load_json("./analysis_result.json")
time_series_plot(data)
from file_utils import load_json
from visualizer import time_series_plot_from_json

def test_three_hours():
    data = load_json("./analysis_result1.json")
    time_series_plot_from_json(data, save=True)

def test_one_day():
    data = load_json("./analysis_result2.json")
    time_series_plot_from_json(data, save=True)
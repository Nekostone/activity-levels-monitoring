from file_utils import load_json
from visualizer import time_series_plot_from_json


def test_three_hours():
    data = load_json("./sample_time_series_results/sw_first_trial.json")
    time_series_plot_from_json(data, single_day=True, save=True)

def test_one_day():
    data = load_json("./sample_time_series_results/teck_one_day_activity.json")
    time_series_plot_from_json(data, save=True)

test_three_hours()

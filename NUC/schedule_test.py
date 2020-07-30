import json
import time
from os import listdir
from os.path import basename, isdir, isfile, join

import schedule
from activity_levels import get_activity_levels, join_dictionaries

data_path = "test_json"

def get_all_files(folder):
    return sorted([f for f in listdir(folder)])

def get_all_folders(folder):
    return [join(folder, f) for f in listdir(folder) if isdir(join(folder, f))]

def job():
    folders = get_all_folders(data_path)
    for folder in folders:
        filenames = get_all_files(folder)
        folder = basename(folder)
        compiled_dictionary = {}
        dict_list = []
        
        for filename in filenames:
            with open(join(data_path, folder, filename)) as json_file:
                dictionary = json.load(json_file)
                dict_list.append(dictionary)
        compiled_dictionary = join_dictionaries(dict_list)
        get_activity_levels(compiled_dictionary, debug=True, title=folder)

# job() # to test the function directly

# time_to_run_job = "15:37"
time_to_run_job = "00:00"

def start_schedule():
    """Starts schedule to run activity_levels analysis script everyday at 0000
    TODO: add to main.py of NUC
    """
    schedule.every().day.at(time_to_run_job).do(job)

    while True:
        schedule.run_pending() 
        time.sleep(1)


from file_utils import get_all_files, write_to_json, basename
from presence_detection import analyze_centroid_displacement_history, analyze_centroid_area_history
from json_to_timedict import json_to_timedict
import time


def test_analyze_centroid_area_history_short_time():
    data_path = "data/teck_calib_2"
    files = get_all_files(data_path)
    analysis_results = analyze_centroid_area_history(files)
    print(analysis_results)
    write_to_json(analysis_results, "sample_presence_detection_analysis/{}.json".format(basename(data_path)))
    
def test_analyze_centroid_area_history_long_time():
    data_path = "data/teck_one_day_activity"
    files = get_all_files(data_path)
    analysis_results = analyze_centroid_area_history(files)
    print(analysis_results)
    write_to_json(analysis_results, "sample_presence_detection_analysis/{}.json".format(basename(data_path)))

def test_analyze_centroid_displacement_history():
    data_path = "data/teck_one_day_activity"
    files = get_all_files(data_path)
    analysis_results = analyze_centroid_displacement_history(files)
    print(analysis_results)
    write_to_json(analysis_results, "displacement_{}.json".format(basename(data_path)))

    
def test_analyze_centroid_displacement_history():
    start = time.time()
    data_path = "data/dataset_for_xavier/2020.07.16"
    files = get_all_files(data_path)
    print("Number of files: {}".format(len(files)))
    analysis_results = analyze_centroid_displacement_history(files)
    json_name = basename(data_path)
    print("Analysis done, writing to {}.json...".format(json_name))
    write_to_json(analysis_results, "displacement_history/{}.json".format(json_name))
    end = time.time()
    print("Time taken to collect displacement dictionary for {} files : {}".format(len(files), end - start))

def test_json_to_timedict():
    filepath = 'sample_activity_levels/displacement_history/2020.07.14.json'
    filepath1 = 'sample_activity_levels/displacement_history/2020.07.15.json'
    filepath2 = 'sample_activity_levels/displacement_history/2020.07.16.json'
    newdict = json_to_timedict(filepath)
    for i in newdict:
        print(i, len(newdict[i]))
    print('\n')
    newdict1 = json_to_timedict(filepath1)
    for i in newdict1:
        print(i, len(newdict1[i]))
    print('\n')
    newdict2 = json_to_timedict(filepath2)
    for i in newdict2:
        print(i, len(newdict2[i]))
    print('\n')
    write_to_json(newdict, "sample_activity_levels/old_format/formatted_history/2020.07.14.json")
    write_to_json(newdict1, "sample_activity_levels/old_format/formatted_history/2020.07.15.json")
    write_to_json(newdict2, "sample_activity_levels/old_format/formatted_history/2020.07.16.json")


# test_analyze_centroid_area_history_short_time()
# test_analyze_centroid_area_history_long_time()
# test_analyze_centroid_displacement_history()
# test_json_to_timedict()

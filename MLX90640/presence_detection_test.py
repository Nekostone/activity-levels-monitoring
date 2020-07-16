from file_utils import get_all_files, write_to_json, basename
from presence_detection import analyze_centroid_displacement_history, analyze_centroid_area_history


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

# test_analyze_centroid_area_history_short_time()
# test_analyze_centroid_area_history_long_time()

test_analyze_centroid_displacement_history()

from collections import defaultdict
from file_utils import get_all_data_filenames, get_frame, write_to_json
from person_detection import naive_binary_likelihood_by_frame
import time


data_path = "./data/teck_one_day_trial"
files = get_all_data_filenames(data_path)
print("Number of frames: ", len(files))

def analyze_by_period(files, num_frames=60*30):
    time_person_spent_in_areas = defaultdict(int)
    counter = 0
    while counter < num_frames:
        frame = get_frame(files[counter], data_path)
        areas_person_is_in = naive_binary_likelihood_by_frame(frame)
        for area in areas_person_is_in:
            if areas_person_is_in[area]:
                time_person_spent_in_areas[area] += 1
        counter += 1
    total_time_spent_in_room = sum(time_person_spent_in_areas.values())
    time_person_spent_in_areas = {i:  time_person_spent_in_areas[i]/total_time_spent_in_room for i in range(8)}    
    return time_person_spent_in_areas

def analyze():
    total_frames = len(files)
    counter = 0
    analysis_results = {}
    while counter < total_frames:
        num_frames = 60*30
        if num_frames + counter >= total_frames:
            num_frames = total_frames - counter
        
        start_time = files[counter].split("_grideye")[0]
        one_span_frames = files[counter: counter+num_frames]
        one_span_analysis = analyze_by_period(one_span_frames, num_frames)
        analysis_results[start_time] = one_span_analysis
        counter += num_frames
    print(analysis_results)
    return analysis_results

start = time.time()
result = analyze()
end = time.time()
print("Analysis completed in ", end-start, "seconds")
write_to_json(result, "./analysis_result.json")
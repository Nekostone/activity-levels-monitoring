from file_utils import get_all_data_filenames
import matplotlib.pyplot as plt
from presence_detection import get_frame, naive_detection_by_frame, naive_detection_from_data, visualize_likelihood_plot
from presence_detection import naive_binary_likelihood_by_frame

data_path = "./data/teck_one_day_activity"
files = get_all_data_filenames(data_path)
print("Number of frames found in ", data_path, ": ", len(files))


# testing of naive detection algorithm based on 1 single frame

def test_naive_one_frame():
    # view normal heatmap next to percentage plot
    test_frame = get_frame(files[60*20], data_path)
    areas_person_is_in = naive_detection_by_frame(test_frame)
    fig, ax = plt.subplots()
    im = ax.imshow(test_frame, cmap="hot")
    visualize_likelihood_plot(areas_person_is_in)

def test_naive_many_frames():
    naive_detection_from_data(data_path, 7200, 12000)
# testing of naive detection algorithm based on many frames

def test_naive_all_frames():
    naive_detection_from_data(data_path)

def test_naive_binary_likelihood():
    test_frame = get_frame(files[60*20], data_path)
    result = naive_binary_likelihood_by_frame(test_frame)
    print(result)
from presence_detection import get_centroid_area_number, get_centroid_area_history
from background_subtraction_test import test_postprocess_img
from centroid_history import plot_centroid_history
from file_utils import get_all_files

def test_get_centroid_area_number():
    centroid = (0,0)
    print("Area number for centroid ", centroid, " is ", get_centroid_area_number(centroid))
    centroid = (12,0)
    print("Area number for centroid ", centroid, " is ", get_centroid_area_number(centroid))
    centroid = (0,12)
    print("Area number for centroid ", centroid, " is ", get_centroid_area_number(centroid))
    centroid = (6,24)
    print("Area number for centroid ", centroid, " is ", get_centroid_area_number(centroid))
    
def test_get_centroid_area_number_from_postprocess(file):
    thresholded_img, centroids = test_postprocess_img(file, plot=True)
    centroid = centroids[0]
    print("Area number for centroid based on contours ", centroid, " is ", get_centroid_area_number(centroid))
    
def test_get_centroid_area_history(files, contour_detection_filter=None):
    centroid_locations, interpolated_centroid_history = get_centroid_area_history(files, contour_detection_filter)
    print(interpolated_centroid_history)
    plot_centroid_history(interpolated_centroid_history)
    print(centroid_locations)
    
data_path = "data/teck_sit_one_hr"
files = get_all_files(data_path)
# test_get_centroid_area_number_from_postprocess(files[89])
test_get_centroid_area_history(files)
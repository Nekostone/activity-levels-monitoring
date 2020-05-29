from centroid_history import Interpolator, get_centroid_history
from file_utils import get_all_files

data = "data/teck_walk_out_and_in"
files = get_all_files(data)

def test_get_centroid_history():
    history = get_centroid_history(files)
    interp = Interpolator(history)
    for a in range(len(history)):
        interp.none_checker(history[a], a)
    print("Original History")
    print(history)
    print("Interpolated History")
    print("\n")
    print(interp.history)
    
test_get_centroid_history()
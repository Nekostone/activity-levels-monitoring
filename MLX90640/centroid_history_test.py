from centroid_history import Interpolator, get_centroid_history, plot_centroid_history
from file_utils import get_all_files

data = "data/teck_walk_out_and_in"
files = get_all_files(data)

def test_get_centroid_history(plot=False):
    history = get_centroid_history(files)
    interp = Interpolator(history)
    for a in range(len(history)):
        interp.none_checker(history[a], a)
    print("Original History")
    print(history)
    print("\n")
    print("Interpolated History")
    print(interp.history)
    if plot:
        plot_centroid_history(interp.history)

    
# test_get_centroid_history(plot=True)
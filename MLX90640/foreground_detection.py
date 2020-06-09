import copy

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

from background_subtraction import bs_godec, cleaned_godec_img
from config import (bg_subtraction_gifs_path, bg_subtraction_pics_path,
                    bs_pics_path, bs_results_path, godec_data_path,
                    godec_gifs_path, godec_pics_path)
from file_utils import (base_folder, get_all_files, get_frame, get_frame_GREY,
                        normalize_frame, create_folder_if_absent)
from godec import plot_bs_results, plot_godec
from visualizer import init_comparison_plot, update_comparison_plot, write_gif_from_pics

# the functions here take in frames of MLX data in 24*32 np arrays

def residual_squares(est_background, mlx_measurement):
    return np.square(est_background - mlx_measurement)


def probability_function(residual, steepness=1.5):  # probability that the measurement belongs to the background
    exp = np.exp(steepness*residual)
    denom = 1 + exp
    return 1- 2/denom


# ---------------------------- TEST -------------------------------------------------------------
# need to implement your own background thingy


data_path = "data/teck_calib_2"
data = get_all_files(data_path)
M, LS, L, S, width, height = bs_godec(data, normalize=False) # get that godec data mmmm

backgrounds = L
probabilities = []

subplt_titles = ["Original", "Foreground %"]
ims = init_comparison_plot(get_frame_GREY(data[0]), subplt_titles, 1, 2, title="Probabilistic Foreground Detection")

for i in range(len(data)):
    frame = get_frame(data[i])
    L_frame = L[:, i].reshape(width, height).T
    S_frame = S[:, i].reshape(width, height).T
    img = cleaned_godec_img(L_frame, S_frame)
    residue = residual_squares(img, frame)
    probability = probability_function(residue)
    probabilities.append(probability)
    images = [normalize_frame(img), normalize_frame(probability)]
    update_comparison_plot(ims, images)
    create_folder_if_absent("testpics")
    plt.savefig("testpics/{}.png".format(i))

files = get_all_files("testpics")
write_gif_from_pics(files, "probabilistic_foreground_detection.gif", fps=20)

probabilities = np.array(probabilities)
probabilities *= 100
probabilities = np.round(probabilities)  # probabilities contains the percentage probabilities that a pixel in
print(probabilities[0])                  # each frame belongs to the background

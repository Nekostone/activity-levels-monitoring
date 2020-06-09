import cv2 as cv
import numpy as np

from file_utils import get_all_files, get_frame_GREY, base_folder, normalize_frame, get_frame
from background_subtraction import bs_godec
import matplotlib.pyplot as plt
from config import (bg_subtraction_gifs_path, bg_subtraction_pics_path,
                    bs_pics_path, bs_results_path, godec_data_path,
                    godec_gifs_path, godec_pics_path)
from godec import plot_bs_results, plot_godec
import copy

# the functions here take in frames of MLX data in 24*32 np arrays

def residual_squares(est_background, mlx_measurement):

    return np.square(est_background - mlx_measurement)


def probability_function(residual, steepness=1.5):  # probability that the measurement belongs to the background
    exp = np.exp(steepness*residual)
    denom = 1 + exp
    return 2/denom


# ---------------------------- TEST -------------------------------------------------------------
#need to implement your own background thingy


data_path = "data/teck_calib_2"
data = get_all_files(data_path)
M, LS, L, S, width, height = bs_godec(data, normalize=False) # get that godec data mmmm

backgrounds = L
probabilities = []


for i in range(len(data)):
    frame = get_frame(data[i])
    L_frame = L[:, i].reshape(width, height).T
    residue = residual_squares(L_frame, frame)
    probability = probability_function(residue)

    probabilities.append(copy.copy(probability))

probabilities = np.array(probabilities)
probabilities *= 100
probabilities = np.round(probabilities)  # probabilities contains the percentage probabilities that a pixel in
print(probabilities[0])                  # each frame belongs to the background




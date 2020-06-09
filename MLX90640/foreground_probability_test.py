import copy

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

from background_subtraction import bs_godec
from file_utils import (base_folder, create_folder_if_absent, get_all_files,
                        get_frame, get_frame_GREY, normalize_frame)
from foreground_probability import (foreground_probability,
                                    probability_from_residue, residual_squares)
from visualizer import (init_comparison_plot, update_comparison_plot,
                        write_gif_from_pics)

data_path = "data/teck_calib"
data = get_all_files(data_path)
M, LS, L, S, width, height = bs_godec(data, normalize=False) # get that godec data mmmm

def test_foreground_probability(savegif=False):

    subplt_titles = ["Original", "Foreground %"]
    ims = init_comparison_plot(get_frame_GREY(data[0]), subplt_titles, 1, 2, title="Probabilistic Foreground Detection")

    for i in range(len(data)):
        frame = get_frame(data[i])
        L_frame = L[:, i].reshape(width, height).T
        S_frame = S[:, i].reshape(width, height).T
        L_probability = foreground_probability(L_frame, frame)
        
        # this condition is now abstracted as the function cleaned_godec_img() in background_subtractio.py
        S_probability = foreground_probability(S_frame, frame)
        if np.sum(L_probability) < np.sum(S_probability):
            probability = L_probability
            img = L_frame
        else:
            probability = S_probability
            img = S_frame
        
        images = [normalize_frame(img), normalize_frame(probability)]
        update_comparison_plot(ims, images)
        create_folder_if_absent("testpics")
        plt.savefig("testpics/{}.png".format(i))

    if savegif:
        files = get_all_files("testpics")
        write_gif_from_pics(files, "probabilistic_foreground_detection.gif", fps=20)
        
test_foreground_probability(True)

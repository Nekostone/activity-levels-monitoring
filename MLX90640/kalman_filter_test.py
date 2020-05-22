import copy

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from file_utils import (base_folder, create_folder_if_absent, get_all_files,
                        get_frame, get_frame_GREY, optimize_size)
from kalman_filter import FrameKalmanFilter, PixelKalmanFilter, init_noise_reduction_plot, update_noise_reduction_plot
from visualizer import write_gif

kalman_pics_path = "kalman_filter_pics/"
kalman_gifs_path = "kalman_filter_gifs/"
data_path = "data/teck_walk_out_and_in"
data = get_all_files(data_path)

def test_pixel_filter():
    noise_remover = PixelKalmanFilter()
    temp_over_time = [get_frame(data[i])[0][0] for i in range(len(data))]
    temp_over_time_2 = copy.copy(temp_over_time)
    filtered = [np.array(noise_remover.filter(temp_over_time[i]))[0][0] for i in range(len(data))]

    plt.plot(np.arange(0,255,1), temp_over_time_2,  "r--", np.arange(0,255,1), filtered, "bs")
    plt.show()

def test_frame_filter(savegif=False):
    noise_remover = FrameKalmanFilter()
    save_path = kalman_pics_path + base_folder(data_path)
    create_folder_if_absent(save_path)
    data_i = get_frame(data[0])
    subplt_titles = ["Original Image", "noise removed"]
    ims, axs, fig = init_noise_reduction_plot(data_i, subplt_titles)
    for i in tqdm(range(len(data))):
        data_i = get_frame(data[i])
        processed = noise_remover.process_frame(data_i)
        update_noise_reduction_plot(ims, [data_i, processed])
        plt.savefig(save_path + "/{}.png".format(i)) #make png
    if savegif:
        gif_pics = [save_path+ "/{}".format(i) + ".png" for i in range(len(data))]
        gif_path = kalman_gifs_path+base_folder(data_path)+".gif"
        write_gif(gif_pics, gif_path, 0, len(gif_pics), fps=30)
        optimize_size(gif_path)

def test_frame_filter_by_pixel():
    temp_over_time = []
    noise_remover = FrameKalmanFilter()
    for i in tqdm(range(len(data))):
        processed = noise_remover.process_frame(get_frame(data[i]))
        temp_over_time.append(copy.copy(processed))  # ADD THE COPY.COPY(). IF YOU DONT,IT APPENDS THE REFERENCE SO YOUR WHOLE ARRAY IS THE SAME
        pixel_over_time = []
    for i in tqdm(range(len(data))):
        frame = get_frame(data[i])  # measurement data
        pixel_over_time.append(frame[20][20])  # adds the values of a specific pixel over time to pixel_over_time

    filtered_over_time = []
    for i in tqdm(range(len(data))):
        frame = temp_over_time[i]  # filtered data
        filtered_over_time.append(frame[20][20])  # adds the values of a specific pixel over time to filtered_over_time

    plt.plot(np.arange(0,255,1), pixel_over_time,  "r--", np.arange(0,255,1), filtered_over_time, "bs")
    plt.show()

test_frame_filter(savegif=True)
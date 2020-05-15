from file_utils import get_all_files
from file_utils import get_frame, get_frame_GREY
from background_subtraction import bs_godec
import numpy as np
import matplotlib.pyplot as plt


def generate_background_est(m, b_n_minus_2, prev_output, alpha, MODE="DEFAULT"):
    # background est is b(n-1). Feed in numpy arrays.

    if MODE == 'DEFAULT':
        lampa = 1 - (1 / m)
        alpha = lampa
    output = b_n_minus_2 + (1 - alpha) * prev_output

    return output


def static_clutter_algo(data):
    # data: numpy array file. Outputs the uncluttered data and backgrounds in the form of an array of numpy arrays
    # each representing one frame

    M, LS, L, S, width, height = bs_godec(data[0:2])
    first_background = S[:, 0].reshape(width, height).T
    first_uncluttered = L[:, 1].reshape(width, height).T
    background = first_background

    # xxXX__set initialisation parameters here__XXxx
    m = len(data)
    result = []
    backgrounds = []

    for i in range(len(data)):

        if i == 2:
            background = generate_background_est(m, background, first_uncluttered, 0.2)
        elif i > 2:
            background = generate_background_est(m, backgrounds[i - 2], result[i - 1], 0.2)

        backgrounds.append(background)
        r = get_frame_GREY(data[i]) - background
        print(r + background == get_frame_GREY(data[i]))
        result.append(r)

    return result, backgrounds

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@__xxXX__FOOD FOR THOUGHT____XXxx@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# data = get_all_files("data/teck_walk_out_and_in")
# M, LS, L, S, width, height = bs_godec(data[0:2])
# first_background = S[:,0].reshape(width, height).T
# first_uncluttered = L[:,1].reshape(width, height).T
# background = first_background
#
# # xxXX__set initialisation parameters here__XXxx
# m = len(data)
# result = []
# backgrounds = []
#
# for i in range(len(data)):
#
#     if i == 2:
#         background = generate_background_est(m, background, first_uncluttered, 0.2)
#     elif i > 2:
#         background = generate_background_est(m, backgrounds[i - 2], result[i - 1], 0.2)
#
#     backgrounds.append(background)
#     r = get_frame_GREY(data[i]) - background
#     print(r + background == get_frame_GREY(data[i]))
#     result.append(r)


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@__xxXX__TEST____XXxx@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

data = get_all_files("data/teck_walk_out_and_in")
result, backgrounds = static_clutter_algo(data)

plt.subplot(131)
plt.imshow(get_frame_GREY(data[29]))
# plt.title("Original Image %d" % i)
plt.subplot(132)
plt.imshow(result[29])
# plt.title("clutter removed %d" % i)
plt.subplot(133)
plt.imshow(backgrounds[29])
# plt.title("backgrounds %d" % i)

plt.show()

import time

import cv2
from numpy import array, column_stack

from file_utils import get_all_files, get_frame_GREY
from godec import godec
from godec_utils import play_2d_results


def bs_godec(data_path, debug=False):
    files = get_all_files(data_path)
    files = files[len(files)-20:len(files)]
    print(len(files))
    i = 0
    for f in files:
        frame = get_frame_GREY(f)
        # Stack frames as column vectors
        F = frame.T.reshape(-1)
        
        if i == 0:
            M = array([F]).T
        else:
            M = column_stack((M, F))
        i+=1
        
    t = time.time()
    L, S, LS, RMSE = godec(M, iterated_power=20)
    elapsed = time.time() - t
    print(elapsed, "sec elapsed")
    height, width = frame.shape
    if debug:
        play_2d_results(M, LS, L, S, width, height)
    return LS


def bs_mog2(data_path):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    fgbg = cv2.createBackgroundSubtractorMOG2()
    files = get_all_files(data_path)
    for f in files:
        frame = get_frame_GREY(f)
        fgmask = fgbg.apply(frame)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

        cv2.imshow('Background Subtraction - MOG2',fgmask)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

    cv2.destroyAllWindows()

data_path = "data/teck_empty_room_with_light_and_no_AC_curtains_open_10mins"
bs_godec(data_path)

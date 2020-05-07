import time

import cv2
from numpy import array, column_stack

from file_utils import get_all_files, get_frame_GREY
from godec import godec
from godec_utils import play_2d_results


def bs_godec(files, debug=False):
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
    
    print(M.shape)
    t = time.time()
    L, S, LS, RMSE = godec(M, iterated_power=5)
    elapsed = time.time() - t
    print(elapsed, "sec elapsed")
    if debug:
        height, width = frame.shape
        play_2d_results(M, LS, L, S, width, height)
    return L, S


def bs_mog2(files):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    fgbg = cv2.createBackgroundSubtractorMOG2()
    for f in files:
        frame = get_frame_GREY(f)
        fgmask = fgbg.apply(frame)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

        cv2.imshow('Background Subtraction - MOG2',fgmask)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

    cv2.destroyAllWindows()
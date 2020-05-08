import time

import cv2 as cv
from numpy import array, column_stack

from file_utils import get_all_files, get_frame_GREY
from godec import godec, plot_godec

def create_godec_input(files):
    i = 0
    t = time.time()
    for f in files:
        frame = get_frame_GREY(f)
        # Stack frames as column vectors
        F = frame.T.reshape(-1)
        
        if i == 0:
            M = array([F]).T
        else:
            M = column_stack((M, F))
        i+=1
    elapsed = time.time() - t
    print("Time taken to create M: " , elapsed, "seconds")
    return M, frame

def bs_godec_trained(files, noise, debug=False):
    M, frame = create_godec_input(files)
    R = M - noise
    return M, R
    

def bs_godec(files, debug=False, gif_name=False):
    M , frame = create_godec_input(files)
    t = time.time()
    L, S, LS, RMSE = godec(M, iterated_power=5)
    elapsed = time.time() - t
    print("Time taken to run Godec to create L, S, LS, RMSE: " , elapsed, " seconds")
    height, width = frame.shape
    return M, LS, L, S, width, height


def bs_mog2(files):
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(3,3))
    fgbg = cv.createBackgroundSubtractorMOG2()
    for f in files:
        frame = get_frame_GREY(f)
        fgmask = fgbg.apply(frame)
        fgmask = cv.morphologyEx(fgmask, cv.MORPH_OPEN, kernel)

        cv.imshow('Background Subtraction - MOG2',fgmask)
        k = cv.waitKey(30) & 0xff
        if k == 27:
            break

    cv.destroyAllWindows()

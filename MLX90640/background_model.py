import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
from numpy import array, column_stack
from tqdm import tqdm

from config import bg_model_gifs_path, bg_model_pics_path
from file_utils import (base_folder, create_folder_if_absent, get_all_files,
                        get_frame_GREY, normalize_frame)
from godec import get_reshaped_frames, godec, plot_godec, set_data
from visualizer import write_gif


"""
Background Subtraction with Godec
"""

def create_godec_input(files):
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
    return M, frame

def bs_godec(files, debug=False, gif_name=False):
    M , frame = create_godec_input(files)
    L, S, LS, RMSE = godec(M, iterated_power=5)
    height, width = frame.shape
    return M, LS, L, S, width, height

def bs_godec_trained(files, noise, debug=False):
    M, frame = create_godec_input(files)
    R = M - noise
    return M, R
    
"""
Comparison Methods
---
Best results attained so far:
- Blur Method: Median Blur
- Median Blur: kszize = 5
- Bilateral Filter: d = 9
- Thresholding Method - global binary thresholding
"""

def init_blob_detector():
    params = cv.SimpleBlobDetector_Params()
    # Change thresholds
    params.minThreshold = 127
    params.maxThreshold = 255

    # Filter by Area.
    params.filterByArea = True
    params.minArea = 4

    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.1

    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.3

    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.01
    detector = cv.SimpleBlobDetector_create(params)
    return detector

def detect(img, detector):
    keypoints = detector.detect(img)
    im = cv.drawKeypoints(img, keypoints, np.array([]), (0,0,255), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    return im


def compare_bilateral_filter(img):
    """Compare Bilateral Filter effect with different parameters. A slow filter.
    ---
    Sigma values: 
        - If they are small (< 10), the filter will not have much effect, 
        - whereas if they are large (> 150), they will have a very strong effect, making the image look “cartoonish”.
    Filter size: 
        - Large filters (d > 5) are very slow, so it is recommended to use d=5 for real-time applications
        - d=9 for offline applications that need heavy noise filtering.
    """
    images = []
    subplt_titles = []
    for i in range(1,9):
        im = cv.bilateralFilter(img, d=i, sigmaColor=75, sigmaSpace=75)
        images.append(im)
        subplt_titles.append("d = {}".format(i))
    plot_comparison(images, subplt_titles, 2, 4, title="Bilateral Filter with sigmaColor=75, sigmaSpace=75", debug=True)

def compare_gaussian_blur(img):
    images = []
    subplt_titles = []
    for i in range(1,15,2):
        im = cv.GaussianBlur(img,(i,i), 3)
        images.append(im)
        subplt_titles.append("ksize = {}".format(i))
    plot_comparison(images, subplt_titles, 2, 4, title="Gaussian Blur", debug=True)

def compare_average_blur(img):
    images = []
    subplt_titles = []
    for i in range(1,15,2):
        im = cv.blur(img,(i,i))
        images.append(im)
        subplt_titles.append("ksize = {}".format((i,i)))
    plot_comparison(images, subplt_titles, 2, 4, title="Average Blur", debug=True)

def compare_median_blur(img):
    images = []
    subplt_titles = []
    for i in range(1,15,2):
        im = cv.medianBlur(img,i)
        images.append(im)
        subplt_titles.append("ksize = {}".format(i))
    plot_comparison(images, subplt_titles, 2, 4, title="Median Blur", debug=True)
    
def compare_thresholds(original_img, cleaned_img):
    blurred = cv.medianBlur(cleaned_img,5)
    ret,th1 = cv.threshold(cleaned_img,127,255,cv.THRESH_BINARY)
    th2 = cv.adaptiveThreshold(cleaned_img,255,cv.ADAPTIVE_THRESH_MEAN_C,\
                cv.THRESH_BINARY,35,2)
    th3 = cv.adaptiveThreshold(cleaned_img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv.THRESH_BINARY,35,2)
    images = [original_img, cleaned_img, blurred, th1, th2, th3]
    subplt_titles = ['Original Image', 'After Godec', 'Median Blur of 5', 'Global Thresholding (v = 127)',
        'Adaptive Mean Thresholding', 'Adaptive Gaussian Thresholding']
    plot_comparison(images, subplt_titles, 2, 3, title="Thresholding", debug=True)

def init_comparison_plot(frame, subplt_titles, num_rows, num_columns, title="", debug=False):
    fig, axs = plt.subplots(num_rows, num_columns)
    fig.suptitle(title)
    ims = []
    
    if num_rows <= 1:
        for i in range(num_columns):
            axs[i].set_title(subplt_titles[i])
            im = axs[i].imshow(frame, 'gray')
            ims.append(im)
            plt.xticks([]),plt.yticks([])
    else:
        counter = 0
        for i in range(num_columns):
            for j in range(num_rows):
                axs[i,j].set_title(subplt_titles[counter])
                im = axs[i,j].imshow(frame, 'gray')
                ims.append(im)
                counter +=1
    if debug:
        plt.show()
    return ims    

def update_comparison_plot(ims, images, saveIndex=None, debug=False, save=False):
    for i in range(len(ims)):
        ims[i].set_data(images[i])
    plt.draw()
    if debug:
        plt.pause(.01) # required for very small datasets for previewing
    if save:
        print("saving...")
        pic_name = '{}{}.png'.format(bg_model_pics_path, saveIndex)
        plt.savefig(pic_name)

def plot_comparison(images, subplt_titles, num_rows, num_columns, title=""):
    assert len(images) == len(subplt_titles)
    ims = init_comparison_plot(subplt_titles, num_rows, num_columns, title="")
    update_comparison_plot(ims, images)

"""
Postprocessing Pipeline
"""

def postprocess_img(img):
    blurred_img = cv.medianBlur(img,5)
    _, thresholded_img = cv.threshold(blurred_img,127,255,cv.THRESH_BINARY)
    blob_detector = init_blob_detector()
    annotated_img = detect(thresholded_img, blob_detector)
    images = [img, blurred_img, thresholded_img, annotated_img]
    return images


def bg_model(files, debug=False, save=False):
    """Background modeling process
    1. perform godec background subtraction
    2. thresholding to make actual pixels representing the person to be more salient in the frame
    3. naive detection / optical flow. 

    Arguments:
        files {[str]} -- Array obtained from get_all_files(data_path)

    Keyword Arguments:
        debug {bool} -- [description] (default: {False})
    """    
    M, LS, L, S, width, height = bs_godec(files)
    if debug:
        subplt_titles = ["Original", "After Godec", "Blurred", " Thresholded", "Annotated"]
        ims = init_comparison_plot(get_frame_GREY(files[0]), subplt_titles, 1, 5, title="Post Processing")
        for i in tqdm(range(len(files))):
            L_frame = normalize_frame(L[:, i].reshape(width, height).T)
            S_frame = normalize_frame(S[:, i].reshape(width, height).T)
            M_frame = normalize_frame(M[:, i].reshape(width, height).T)
            # L or S could be the clean data depending on how much movement has occured during the timeframe
            img = S_frame
            images = postprocess_img(img)
            images.insert(0, get_frame_GREY(files[i]))
            update_comparison_plot(ims, images, i, debug, save)
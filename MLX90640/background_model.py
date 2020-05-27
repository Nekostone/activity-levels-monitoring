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
    return images, subplt_titles

def compare_gaussian_blur(img):
    images = []
    subplt_titles = []
    for i in range(1,15,2):
        im = cv.GaussianBlur(img,(i,i), 3)
        images.append(im)
        subplt_titles.append("ksize = {}".format(i))
    return images, subplt_titles

def compare_average_blur(img):
    images = []
    subplt_titles = []
    for i in range(1,15,2):
        im = cv.blur(img,(i,i))
        images.append(im)
        subplt_titles.append("ksize = {}".format((i,i)))
    return images, subplt_titles

def compare_median_blur(img):
    images = []
    subplt_titles = []
    for i in range(1,15,2):
        im = cv.medianBlur(img,i)
        images.append(im)
        subplt_titles.append("ksize = {}".format(i))
    return images, subplt_titles
    
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

def init_comparison_plot(frame, subplt_titles, num_rows, num_columns, title=""):
    fig, axs = plt.subplots(num_rows, num_columns)
    fig.suptitle(title)
    ims = []
    
    if num_rows <= 1:
        for i in range(num_columns):
            axs[i].set_title(subplt_titles[i])
            im = axs[i].imshow(frame, cmap='hot')
            ims.append(im)
            plt.xticks([]),plt.yticks([])
    else:
        counter = 0
        for i in range(num_rows):
            for j in range(num_columns):
                if len(subplt_titles) < counter:
                    axs[i,j].set_title(subplt_titles[counter])
                    im = axs[i][j].imshow(frame, 'gray')
                    ims.append(im)
                    counter +=1
    return ims    

def update_comparison_plot(ims, images, saveIndex=None, save=False):
    for i in range(len(ims)):
        ims[i].set_data(images[i])
    plt.draw()
    if save:
        print("saving...")
        create_folder_if_absent(bg_model_pics_path)
        pic_name = '{}{}.png'.format(bg_model_pics_path, saveIndex)
        plt.savefig(pic_name)

def compare_plot(images, subplt_titles, num_rows, num_columns, title="", debug=False):
    fig, axs = plt.subplots(num_rows, num_columns)
    axs[0,0].imshow(images[2], 'gray')
    plt.show()

"""
Postprocessing Pipeline
"""

def is_human_contour(cnt):
    return cv.contourArea(cnt) > 4 and cv.contourArea(cnt) < 12

def postprocess_img(img):
    blurred_img = cv.medianBlur(img,5)
    _, thresholded_img = cv.threshold(blurred_img,127,255,cv.THRESH_BINARY)
    mask = thresholded_img.copy()
    contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    color_img = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
    selected_contours = [cnt for cnt in contours if is_human_contour(cnt)]
    annotated_img = cv.drawContours(color_img, selected_contours, -1, (0,255,0), 1)
    images = [img, blurred_img, thresholded_img, annotated_img]
    centroids = []
    if len(selected_contours) > 0:
        centroids = [get_centroid_from_contour(cnt) for cnt in selected_contours]
    return images, centroids

def get_centroid_from_contour(cnt):
    M = cv.moments(cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    return (cx,cy)


def bg_model(files, debug=False, save=False):
    """Background modeling process
    1. perform godec background subtraction
    2. thresholding to make actual pixels representing the person to be more salient in the frame
    3. Contour detection to detect centroid of person 
    4. naive detection / optical flow. 

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
            # TODO: L or S could be the clean data depending on how much movement has occured during the timeframe
            # TODO: maybe can perform contour detection first before deciding L or S is the clean frame
            
            img = S_frame
            # compare_median_blur(img)
            images = postprocess_img(img)
            images.insert(0, get_frame_GREY(files[i]))
            update_comparison_plot(ims, images, i, save)
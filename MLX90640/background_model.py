import cv2 as cv
import matplotlib.pyplot as plt

from background_subtraction import bs_godec


def threshold(img):
    img = cv.medianBlur(img,5)
    ret,th1 = cv.threshold(img,127,255,cv.THRESH_BINARY)
    th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C,\
                cv.THRESH_BINARY,11,2)
    th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv.THRESH_BINARY,11,2)
    images = [img, th1, th2, th3]

def plot_threshold_comparison(images):
    titles = ['Original Image', 'Global Thresholding (v = 127)',
                'Adaptive Mean Thresholding', 'Adaptive Gaussian Thresholding']
    for i in range(4):
        plt.subplot(2,2,i+1),plt.imshow(images[i],'gray')
        plt.title(titles[i])
        plt.xticks([]),plt.yticks([])
    plt.show()


def bg_model(files):
    """
    # TODO
    Background modeling process
    1. perform godec background subtraction
    2. adaptive thresholding to make actual pixels representing the person to be more salient in the frame
    3. naive detection / optical flow. 
    """
    # L, S = bs_goc() # sparse is what we want
    pass

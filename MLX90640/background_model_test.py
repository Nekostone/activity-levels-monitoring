import time
from background_model import (bg_model, bs_godec, bs_godec_trained, postprocess_img, get_centroid_from_contour,
                              compare_gaussian_blur, compare_median_blur, init_comparison_plot, update_comparison_plot)
from config import (bg_model_gifs_path, bg_model_pics_path, bs_pics_path,
                    bs_results_path, godec_data_path, godec_gifs_path,
                    godec_pics_path)
from file_utils import (base_folder, create_folder_if_absent, get_all_files,
                        get_frame, get_frame_GREY, save_npy)
from godec import plot_bs_results, plot_godec
from timer import Timer
from visualizer import write_gif


def test_bs_godec(files, save_data=False, save_gif=False, gif_name=None, fps=60):
    """Test bs_godec Implementation

    Keyword Arguments:
        save_data {bool} -- (default: {False})
        save_gif {bool} -- (default: {False})
        gif_name {string} -- (default: {None})
        fps {int} -- (default: {60})
    ---
    This test shows you different ways of running the bs_godec method and obtain the various type of data you need.
    """
    print("Testing Godec...")
    t = Timer("accumulate")
    t.start()
    M, LS, L, S, width, height = bs_godec(files)
    t.stop("Time taken to run background subtraction with godec: ")
    
    if save_data:
        t.start()
        
        npy_path = "godec_data/" + base_folder(data_path) 
        create_folder_if_absent(godec_data_path)
        save_npy(M, npy_path, "M")
        save_npy(L, npy_path, "L")
        save_npy(S, npy_path, "S")
        save_npy(LS, npy_path, "LS")
        
        t.stop("Time taken to save godec result npy arrays: " )
    
    plots_path = godec_pics_path + base_folder(data_path)  
    if not save_gif:
        print("Plotting....")
        t.start()
        
        plot_godec(M, LS, L, S, plots_path, width=width, height=height, preview=True)
        
        t.stop("Time taken to save godec plots: ")
    elif save_gif and gif_name:
        print("Saving gif as {}....".format(gif_name))
        t.start()
        
        plot_godec(M, LS, L, S, plots_path, width=width, height=height)
        pics = get_all_files(plots_path)
        
        t.stop("Time taken to save godec plots: ")
        write_gif(pics, godec_gifs_path+gif_name, start=0, end=len(pics), fps=fps)
    
    print("The entire process has taken: ", t.timers['accumulate'], " seconds")

def test_bs_godec_trained_noise(noise_path, gif_name, preview):
    """Test bs_godec Implementation with trained noise

    Keyword Arguments:
        noise_path {string}
        gif_name {string}
        preview {boolean}
    ---
    This test shows you how to run the bs_godec method.
    """
    N = get_frame(noise_path)
    M, R = bs_godec_trained(files, N)
    plot_bs_results(M, N, R, bs_pics_path, preview=preview)

def test_compare_median_blur(file):
    compare_median_blur(get_frame_GREY(file))
    
def test_compare_gaussian_blur(file):
    compare_gaussian_blur(get_frame_GREY(file))

def test_background_model(files, debug=False, save=False):
    bg_model(files, debug, save)
    
def test_postprocess_img(f,  plot=False):
    img = get_frame_GREY(f)
    images, centroids = postprocess_img(img)
    if plot:
        images.insert(0, img)
        subplt_titles = ["Original", "After Godec", "Blurred", " Thresholded", "Annotated"]
        ims = init_comparison_plot(img, subplt_titles, 1, 5, title="Post Processing")
        update_comparison_plot(ims, images, save=True, saveIndex=100)
    
    print("Centroids found are located at: ", centroids)

"""
Initialization of test parameters
""" 
data_path = "data/teck_walk_out_and_in"
files = get_all_files(data_path)
    
"""
Test godec implementation
""" 
# test_bs_godec(files)
# test_bs_godec(gif_name=base_folder(data_path)+".gif", fps=30, save_gif=True)

"""
Test preobtained noise from godec with upcoming data
"""
# noise_path = godec_data_path + "data/S.npy"
# gif_name = "bs_result_5mins_noise.gif"

# test_bs_godec_trained_noise(noise_path, gif_name, True)
# pics = get_all_files(bs_pics_path)
# write_gif(pics, godec_gifs_path+gif_name, start=0, end=len(pics), fps=30)

"""
Test Comparison Methods
"""
i = 4
# test_compare_median_blur(files[i])
# test_compare_gaussian_blur(files[i])

"""
Test Postprocessing of Image
"""

test_postprocess_img(files[i], plot=True)

""""
Test Background Model
"""

# test_background_model(files, debug=True, save=True)
# pics = get_all_files(bg_model_pics_path)
# gif_name = base_folder(data_path)+"2.gif"
# write_gif(pics, bg_model_gifs_path+gif_name, start=0, end=len(pics), fps=15)

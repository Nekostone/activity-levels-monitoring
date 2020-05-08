from background_model import bg_model
from background_subtraction import bs_godec, bs_godec_trained
from file_utils import get_all_files, save_as_npy, create_folder_if_absent, base_folder, get_frame
from godec import plot_godec, plot_bs_results
from visualizer import write_gif_from_pics
import time

data_path = "data/teck_one_day_activity"
godec_data_path = "godec_data/"
godec_pics_path = "godec_pics/"
godec_gifs_path = "godec_gifs/"
bs_pics_path = "bs_pics/"
bs_results_path = "bs_results/"

files = get_all_files(data_path)[300:600] # remove the indexes if u want to use all 24hrs frames

# TODO: Track time consumed with other methods instead of cluttering with time.time() statements 

def test_godec(save_data=False, save_gif=False, gif_name=None, fps=60):
    print("Testing Godec...")
    
    start_t = time.time()
    
    M, LS, L, S, width, height = bs_godec(files)
    if save_data:
        t = time.time()
        
        npy_path = "godec_data/" + base_folder(data_path) 
        create_folder_if_absent(godec_data_path)
        save_as_npy(M, npy_path, "M")
        save_as_npy(L, npy_path, "L")
        save_as_npy(S, npy_path, "S")
        save_as_npy(LS, npy_path, "LS")
        
        elapsed = time.time() - t
        print("Time taken to save godec result npy arrays: " , elapsed, " seconds")
    
    plots_path = godec_pics_path + base_folder(data_path)  
    if not save_gif:
        print("Plotting....")
        t = time.time()
        
        plot_godec(M, LS, L, S, plots_path, width=width, height=height, preview=True)
        
        elapsed = time.time() - t
        print("Time taken to save godec plots: " , elapsed, " seconds")
    elif save_gif and gif_name:
        print("Saving gif as {}....".format(gif_name))
        t = time.time()
        
        plot_godec(M, LS, L, S, plots_path, width=width, height=height)
        pics = get_all_files(plots_path)
        
        elapsed = time.time() - t
        print("Time taken to save godec plots: " , elapsed, " seconds")
        create_folder_if_absent(godec_gifs_path)
        write_gif_from_pics(pics, godec_gifs_path+gif_name, start=0, end=len(pics), fps=fps)
    
    end_t = time.time()
    print("The entire process has taken: ", end_t-start_t, " seconds")

def test_godec_result_on_future(noise_path, gif_name, preview):
    N = get_frame(noise_path)
    M, R = bs_godec_trained(files, N)
    plot_bs_results(M, N, R, bs_pics_path, preview=preview)
    
"""
Test godec implementation
""" 
   
# test_godec(gif_name=data_path+".gif", fps=300, save_gif=True, save_data=True)

"""
Test preobtained noise from godec with upcoming data
"""

noise_path = godec_data_path + "data/S.npy"
gif_name = "bs_result_5mins_noise.gif"

test_godec_result_on_future(noise_path, gif_name, True)
pics = get_all_files(bs_pics_path)
write_gif_from_pics(pics, godec_gifs_path+gif_name, start=0, end=len(pics), fps=30)


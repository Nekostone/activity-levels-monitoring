from file_utils import get_all_files
from optical_flow import optical_flow_dense, optical_flow_lk
from visualizer import write_gif_from_pics


def test_opticalflow_lk():
    print("Performing Lucas-Kanade Optical Flow")
    optical_flow_lk(files)
    
def test_opticalflow_dense():
    print("Performing Dense Optical Flow with Gunnar Farneback")
    optical_flow_dense(files)

data_path = "data/teck_walk_out_and_in"
files = get_all_files(data_path)
test_opticalflow_dense()

pics = get_all_files("optical_flow_pics/")
write_gif_from_pics(pics, "dense_v2.gif",start=0, end=len(pics), fps=5)


from optical_flow import optical_flow_dense, optical_flow_lk
from file_utils import get_all_files


def test_opticalflow_lk():
    optical_flow_lk(files)
    
def test_opticalflow_dense():
    optical_flow_dense(files)

data_path = "data/teck_first_trial"
files = get_all_files(data_path)
test_opticalflow_lk()
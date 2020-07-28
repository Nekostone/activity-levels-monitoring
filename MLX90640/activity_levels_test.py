from activity_levels import get_activity_levels
from file_utils import load_json

def test_activity_levels():
    data_path = r'C:\Users\XC199\Desktop\Crapstone\Activity Levels\IoT\2020.07.14.json'
    data = load_json(data_path)
    get_activity_levels(data, debug=True)
        
test_activity_levels()
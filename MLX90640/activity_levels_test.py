from activity_levels import get_activity_levels
from file_utils import load_json

def test_activity_levels():
    data_path = 'sample_activity_levels/formatted_history/2020.07.14.json'
    data = load_json(data_path)
    get_activity_levels(data, debug=True)
        
test_activity_levels()
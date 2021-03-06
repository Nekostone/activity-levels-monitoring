from activity_levels import get_activity_levels, stitch_data

def test_stitch_data():
    test_list = [{'0907': ['a', 'b', 'c'], '0906': ['d', 'e', 'f'], '0910': ['g', 'h', 'i']}, {'0901': ['j', 'k', 'l'], '0902': ['m', 'n', 'o']}, {'0904': ['p', 'q', 'r']}]
    print(stitch_data(test_list))

def test_activity_levels():
    data_path = "./sample_activity_levels/new_format/2020.07.16.json"
    with open(data_path) as json_file:
        data = json.load(json_file)
    get_activity_levels(data, debug=True)
        
test_stitch_data()
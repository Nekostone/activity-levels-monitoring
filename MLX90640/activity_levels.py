import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate
import scipy.signal

"""
This script is to be called by the NUC.
    1. During a time interval, say "0900-0930", the NUC receives different MQTT messages 
        that contains a json. These MQTT messages can be loaded into their respective 
        dictionary by the json module.
    2. After the time interval has passed, the NUC should call stitch_data(dictionaries) for all
        the dictionaries that has a key within that time interval, and produce a 
        compiled_dictionary consisting of the key "0900-0930".
    3. Analyze the displacement history by calling get_activity_levels(compiled_dictionary). 
        The result should be saved somewhere so that analysis can be performed across days, weeks or months.
"""

def stitch_data(dictionaries):
    """Stitch different dictionary data that are within the same time interval
    Returns a compiled dictionary containing only one key denotating the time interval.

    AKA it does this:
    [{key1:[...], key2:[...], key3:[...]}, {key4:[...], key5:[...]}, {key6:[...]}] where the keys fall within a specific 30 min interval
    ---> {key1:[...], key2:[...], key3:[...], key4:[...], key5:[...], key6:[...]}
    ---> {30min_interval:[..................]}

    Args:
        dictionaries ([dict]): displacement dictionaries from different Rpis
    """
    #TODO
    biggus_dictus = {}
    for dictionary in dictionaries:
        for key in dictionary:
            biggus_dictus[key] = dictionary[key]
    sorted_dict = dict(sorted(biggus_dictus.items()))

    output = {}
    biggus_listus = []
    keys = []
    for i in sorted_dict:
        keys.append(i)
        for j in sorted_dict[i]:
            biggus_listus.append(j)

    output[keys[0]] = biggus_listus

    return output


def get_activity_levels(data, debug=False):
    """Produce activity levels plot based on one time interval
    #TODO: save the out somewhere, compile different outs across days, weeks and months.

    Args:
        data (dict): compiled displacement dictionary for one time interval
        debug (bool): whether the plot is shown for that time interval
    """

    width = 300
    rect = np.ones(width) # rect function for convolution in seconds
    time_key = list(data.keys())[0] # or replace with any time
    y = data[time_key] 
    original = y[0:1500]
    x = np.linspace(0,np.size(original)-1, np.size(original))
    
    # Generate activity data
    ynew  = scipy.signal.resample(original, 1800)
    xnew = np.linspace(0,1799,1800)

    out    = np.dot(np.correlate(ynew, rect, 'valid'), 1/(width/10))
    offset = (width/2)-1
    xaxis = np.linspace(offset, offset+np.size(out)-1, np.size(out))

    ogplot = np.dot(np.correlate(y, rect, 'valid'), 1/(width/10))

    if debug:
        plt.plot(xaxis, ogplot, '--', label='0-padded')
        plt.plot(xaxis, out, '--', label='Resampled')
        plt.plot(xnew,y, label='Instant')
        plt.legend(loc='best')
        plt.grid()
        plt.show()


test_list = [{'0907': ['a', 'b', 'c'], '0906': ['d', 'e', 'f'], '0910': ['g', 'h', 'i']}, {'0901': ['j', 'k', 'l'], '0902': ['m', 'n', 'o']}, {'0904': ['p', 'q', 'r']}]
print(stitch_data(test_list))
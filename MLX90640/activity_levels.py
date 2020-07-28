import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate
import scipy.signal
from datetime import datetime

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
    # Iterate through keys to perform resampling, then stitch together based on timestamps

    Args:
        data (dict): compiled displacement dictionary for one time interval
        debug (bool): whether the plot is shown for that time interval
    """
    activity = []
    end_time = 0
    
    for i in data.keys():
        data[i]['frames'] = scipy.signal.resample(np.array(data[i]['frames']), int(data[i]['timeElapsedInSeconds']))
        if int(i) != 1:
            zeropad  =  datetime.strptime(data[i]['start'], "%Y.%m.%d_%H%M%S") - datetime.strptime(data[str(int(i)-1)]['end'], "%Y.%m.%d_%H%M%S")
            zeropad  =  zeropad.total_seconds() #add zeros for missing frames from previous data
            # print(zeropad)
            zeropad  = list(np.zeros(int(zeropad)))
            activity = activity + zeropad

        elif int(i) == 1:
            start    = data[i]['start'][:-6] + '000000'
            zeropad  = datetime.strptime(data[i]['start'], "%Y.%m.%d_%H%M%S") - datetime.strptime(start, "%Y.%m.%d_%H%M%S")
            zeropad  = zeropad.total_seconds()
            # print(zeropad)
            zeropad  = list(np.zeros(int(zeropad)))
            activity = activity + zeropad #add zeros for missing frames from start of the day
            
        activity = activity + list(data[i]['frames'])

    activity = np.array(activity) # Convert list to nparray

    width = 3600 # Rect function width
    rect  = np.ones(width)
    # Generate activity data
    xnew = np.linspace(0,len(activity),len(activity))

    offset = (width/2)-1
    xaxis = np.linspace(offset, np.size(activity)-offset, np.size(activity)-width+1)

    out = np.dot(np.correlate(activity, rect, 'valid'), 1/(width/10))
    start_time = data[list(data.keys())[0]]['start']
    end_time = data[list(data.keys())[-1]]['end']


    if debug:
        plt.plot(xaxis, out, '--', label='Activity')
        plt.plot(xnew, activity, '--', label='Raw')
        # plt.plot(xaxis, out, '--', label='Resampled')
        # plt.plot(xnew,y, label='Instant')
        plt.legend(loc='best')
        plt.grid()
        plt.show()
        print("Started at {}, ended at {}".format(start_time, end_time))
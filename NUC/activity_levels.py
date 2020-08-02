import json
import os
from datetime import datetime

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

def join_dictionaries(dictionaries):
    """Stitch different dictionaries to return one compiled dictionary.

    Args:
        dictionaries ([dict]): displacement dictionaries from different Rpis
    """
    biggus_dictus = {}
    counter = 0
    for dictionary in dictionaries:
        counter += 1
        biggus_dictus[str(counter)] = dictionary

    return biggus_dictus

def get_activity_levels(data, debug=False, name=""):
    """Produce activity levels plot based on one time interval
    # Iterate through keys to perform resampling, then stitch together based on timestamps
    Args:
        data (dict): compiled displacement dictionary for one time interval
        debug (bool): whether the plot is shown for that time interval
    """
    activity = []
    end_time = 0
    total_frames = 0
    
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
        total_frames += data[i]['numFrames']
    if len(activity) < 86399:
        activity = activity + list(np.zeros(86399-len(activity)))
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
    date, room = name.split(" ")

    if debug:
        plt.plot(xaxis, out, '--', label='Activity')
        plt.plot(xnew, activity, '--', label='Raw')
        plt.legend(loc='best')
        plt.title(name)
        plt.grid()
        plt.show()
        print("Started at {}, ended at {}".format(start_time, end_time))
    
    folder = os.path.join("analysis_results", date)
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    path_to_save = os.path.join("analysis_results", date, room+".json")
    print("saving analysis result to: ", path_to_save)
    with open(path_to_save, 'w+') as outfile:
        dictionary = {
            "start": start_time,
            "end": end_time,
            "numFrames": total_frames,
            "out": list(out)
        }
        json.dump(dictionary, outfile)

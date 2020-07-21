import matplotlib.pyplot as plt
import numpy as np
import scipy.interpolate
import scipy.signal

"""
This script is to be called by the NUC.
"""

def stitch_data(dictionaries):
    """Stitch different dictionary data that are within the same time interval
    Returns a compiled dictionary containing only one key denotating the time interval.

    Args:
        dictionaries ([dict]): displacement dictionaries from different Rpis
    """
    #TODO
    pass



def get_activity_levels(data, debug=False):
    """Produce activity levels plot 

    Args:
        data (dict): compiled displacement dictionary for one time interval
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


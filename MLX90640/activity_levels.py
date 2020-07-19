import numpy as np
import scipy.interpolate
import scipy.signal
import json
import os
import matplotlib.pyplot as plt

os.chdir(r'C:\Users\XC199\Desktop\Crapstone\Activity Levels\IoT\formatted_history')

with open('2020.07.14.json') as f:
    data = json.load(f)


width = 300
rect = np.ones(width) # rect function for convolution in seconds

y = data['0830'] # or replace with any time


original = y[0:1500]
x = np.linspace(0,np.size(original)-1, np.size(original))
print(np.size(y))

# Generate activity data


ynew  = scipy.signal.resample(original, 1800)
xnew = np.linspace(0,1799,1800)

out    = np.dot(np.correlate(ynew, rect, 'valid'), 1/(width/10))
offset = (width/2)-1
xaxis = np.linspace(offset, offset+np.size(out)-1, np.size(out))

ogplot = np.dot(np.correlate(y, rect, 'valid'), 1/(width/10))

""" plt.plot(x,y, 'o', xnew, ynew, '-')
plt.legend(loc='best')
plt.show() """

# plt.plot(x,y, '--', label='Instant')
# plt.plot(xaxis, out, '--', label='Activity')

plt.plot(xaxis, ogplot, '--', label='0-padded')
plt.plot(xaxis, out, '--', label='Resampled')
plt.plot(xnew,y, label='Instant')
plt.legend(loc='best')
plt.grid()
plt.show()


#!/usr/bin/python

import sys, binascii, base64, math

import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.mlab as mlab

def saveHisto(name, data):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # histogram our data with numpy
    n, bins = np.histogram(data, 500000) 

    # get the corners of the rectangles for the histogram
    left = np.array(bins[:-1])
    right = np.array(bins[1:])
    bottom = np.zeros(len(left))
    top = bottom + n 

    
    # we need a (numrects x numsides x 2) numpy array for the path helper
    # function to build a compound path
    XY = np.array([[left,left,right,right], [bottom,top,top,bottom]]).T
    
    # get the Path object
    barpath = path.Path.make_compound_path_from_polys(XY)
    
    # make a patch out of it
    patch = patches.PathPatch(barpath, facecolor='gray', edgecolor='blue', alpha=0.8)
    ax.add_patch(patch)
    
    ax.grid(True)

    # update the view limits
    ax.set_xlabel('Prime Numbers')
    ax.set_ylabel('Difference Between Last')
    ax.set_xlim(left[0], right[-1])
    ax.set_ylim(bottom.min(), top.max())
    plt.savefig('images/'+name+'.png')

def check(x):
    z=True
    for i in range(2,x):
        if i<=math.sqrt(x):
            if x%i!=0:
                z=True
            else:
                z=False
                break
        else:
            break
    return z

last = 3
data = []

for i in range(0, 1000000):
    if check(i):
        amount = i - last
        last = i
        for x in range(0, amount):
            data.append(i)

saveHisto('primes.1000000', data)

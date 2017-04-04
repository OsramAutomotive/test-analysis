#!/usr/bin/python3

''' This module contains interactive web-based plotting functions using the mpld3 module '''

from data_import import *

datapath = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\P552 MCA Headlamp\P552 MCA Aux\ADVPR\PV Aux\TL A&B\LTO\Raw Data"
test = TestStation(3456, datapath, -40)

def web_set_up_plot_area(test):
    fig, axes = plt.subplots(nrows=len(test.boards), ncols=1, sharex=True)  
    fig.suptitle('title', fontsize = 20, fontweight= 'bold')  ## main title for entire figure
    return fig, axes

def set_up_date_time(test, ax):
    ax.plot_date(test.mdf.index.to_pydatetime(), test.mdf[test.vsetpoint], 'k--', 
                      linewidth=3, zorder=10)
    date_fmt = '%m/%d/%y %H:%M:%S'
    formatter = dates.DateFormatter(date_fmt)
    locator = dates.AutoDateLocator()
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(locator)


### TESTING...
import mpld3
from mpld3 import plugins
from mpld3.utils import get_id
import numpy as np
import collections
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
labels = test.systems
line_collections = ax.plot(test.mdf.index, test.b3.df[test.systems], lw=4, alpha=0.2)
interactive_legend = plugins.InteractiveLegendPlugin(line_collections, labels)
plugins.connect(fig, interactive_legend)

mpld3.show()
#!/usr/bin/python3

''' This module contains functions that create temporal plots of 
    voltages and currents using matplotlib. '''

import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.ticker as ticker
from matplotlib import style
from core.data_import.helpers import *
from .. re_and_global import *


def determine_subplot_nrows(test):
    if test.outage:
        nrows = len(test.modes) + 3
    else:
        nrows = len(test.modes) + 2
    return nrows

def determine_legend_ncols(list_to_plot):
    return math.ceil(len(list_to_plot)/6)

def set_up_plot_area(test, pstyle='ggplot'):
    style.use(pstyle)  # set formatting style to use for matplotlib
    nrows = determine_subplot_nrows(test)
    fig, axes = plt.subplots(nrows=nrows, ncols=1, sharex=True)
    fig.suptitle(test.name, fontsize = 20, fontweight= 'bold')  # main title
    return fig, axes

def plot_voltage_functional_cycle(test, ax):
    ax.plot_date(test.df.index.to_pydatetime(), test.df[test.VSETPOINT], 'k--', 
                 linewidth=3, zorder=10)  # plot voltage setpoint on first subplot
    cmap = plt.get_cmap('inferno')
    colors = cmap(np.linspace(0, 1.0, len(test.thermocouples))) 
    vsenses = [vsense for vsense in test.voltage_senses \
               if any(board_id in vsense for board_id in test.board_ids)]
    vsense_labels = [replace_board_id_with_board_name(vsense, test.boards) \
                     for vsense in vsenses]
    for vsense, color in zip(vsenses, colors):
        test.df[vsense].plot(ax=ax, linewidth=2, c=color)
    ax.set_title("Voltage and Functional Cycle")
    ax.set_ylabel("Voltage (V)")
    ax.set_ylim([0,20])
    ax.yaxis.set_major_locator(ticker.MaxNLocator(4))
    ncol = determine_legend_ncols(vsenses)
    ax.legend(fontsize=8, loc='center left', bbox_to_anchor=(1.0, 0.5),
              ncol=ncol, labels=vsense_labels)

def plot_temperature_cycle(test, ax):
    cmap = plt.get_cmap('viridis')
    colors = cmap(np.linspace(0, 1.0, len(test.thermocouples)))    
    for thermocouple, color in zip(test.thermocouples, colors):
        test.df[thermocouple].plot(ax=ax, linewidth=2, c=color)
    ax.set_title("Temperature Profile")
    ax.set_ylabel(u"Temp (\N{DEGREE SIGN}C)")
    ncol = determine_legend_ncols(test.thermocouples)
    ax.legend(fontsize=8, loc='center left', bbox_to_anchor=(1.0, 0.5),
              labels=test.thermocouples, ncol=ncol)

def plot_mode_currents(test, axes, row=2):
    # start on third row subplot
    for mode in test.modes:
        axes[row].set_title(mode.name)
        axes[row].set_ylabel("Current (A)")
        cmap = plt.get_cmap('jet')
        colors = cmap(np.linspace(0, 1.0, len(mode.systems)))
        for system, color in zip(mode.systems, colors):
            axes[row].scatter(mode.df.index, mode.df[system], 
                              c=color, alpha=0.7)
        axes[row].yaxis.set_major_locator(ticker.MaxNLocator(5))
        ncol = determine_legend_ncols(mode.systems)
        axes[row].legend(fontsize=7, loc='center left', bbox_to_anchor=(1.0, 0.5),
                         ncol=ncol, labels = [sys.split(' ', 1)[1] for sys in mode.systems])
        row +=1

def plot_outage_voltages(test, axes):
    row = len(test.modes) + 2
    axes[row].set_title(test.outage.name)
    axes[row].set_ylabel("Voltage (V)")
    cmap = plt.get_cmap('jet')
    colors = cmap(np.linspace(0, 1.0, len(test.outage.systems)))
    for system, color in zip(test.outage.systems, colors):
        axes[row].scatter(test.df.index, test.df[system], 
                          c=color, alpha=0.7)
    axes[row].yaxis.set_major_locator(ticker.MaxNLocator(5))
    ncol = determine_legend_ncols(test.outage.systems)
    axes[row].legend(fontsize=7, loc='center left', bbox_to_anchor=(1.0, 0.5),
                     ncol=ncol, labels = [sys.split(' ', 1)[1] for sys in test.outage.systems])    

def set_figure_size_and_name(fig):
    plt.tight_layout()
    fig.subplots_adjust(top=0.900, bottom=0.075, left=0.070, right=0.760, hspace=0.330)
    fig.canvas.set_window_title('temporal plot')

def print_status(function):
    def wrapper(*args):
        print('\nPlotting temporal plot...')
        function(*args)
        print('...complete.')
    return wrapper


# MAIN PLOTTING FUNCTION 
@print_status
def plot_modes(test, limits=None):
    ''' Creates a temporal plot of the functional cycle, temperature profile, and test mode currents '''
    fig, axes = set_up_plot_area(test)  # set up figure and axes for plotting 
    plot_voltage_functional_cycle(test, ax=axes[0])  # subplot 1: voltage and functional cycle
    plot_temperature_cycle(test, ax=axes[1])  # subplot 2: temperatures
    plot_mode_currents(test, axes)  # subplots 3 and up: mode currents
    if test.outage:
        plot_outage_voltages(test, axes) # last subplot
    set_figure_size_and_name(fig) # set fig size and name

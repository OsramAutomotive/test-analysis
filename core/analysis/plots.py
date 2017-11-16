#!/usr/bin/python3

''' This module contains functions that create temporal plots of 
    voltages and currents using matplotlib. '''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib import style
from core.data_import.helpers import *
from .. re_and_global import *


def set_up_plot_area(test, pstyle='ggplot'):
    title = test.name
    style.use(pstyle)  ## set formatting style to use for matplotlib
    fig, axes = plt.subplots(nrows=len(test.modes)+2, ncols=1, sharex=True)  ## create plot space with app num of subplots
    fig.suptitle(title, fontsize = 20, fontweight= 'bold')  ## main title for entire figure
    return fig, axes


def format_date_time(test, axes):
    date_fmt = '%m/%d/%y %H:%M:%S'
    formatter = dates.DateFormatter(date_fmt)
    locator = dates.AutoDateLocator()
    axes[0].xaxis.set_major_formatter(formatter)
    axes[0].xaxis.set_major_locator(locator)


def plot_voltage_fc(test, axes):
    board_colors = dict(zip(test.boards, MODULE_COLOR_LIST))
    vsense = test.VSENSE1 ## grab only VSense 1 columns
    for board in test.boards:
        if board.outage: # skip Outage board
            continue
        elif '5' in board.id: # Turn current board dashed line
            test.df[board.id + ' ' + vsense].plot(ax=axes[0], color=board_colors[board], linewidth=2, 
                                               linestyle = ':')
        else: # Non-Turn current board solid lines
            test.df[board.id + ' ' + vsense].plot(ax=axes[0], color=board_colors[board], linewidth=2)


def plot_mode_currents(test, axes, row=2):
    ## start on third row subplot
    for mode in test.modes:
        cmap = plt.get_cmap('jet')
        colors = cmap(np.linspace(0, 1.0, len(mode.systems)))
        for system, color in zip(mode.systems, colors):
            axes[row].scatter(mode.df.index, mode.df[system], 
                              c=color, alpha=0.7)
        axes[row].legend(fontsize=7, loc='center left', bbox_to_anchor=(1.0, 0.5),
                       ncol=2, labels = [sys.split(' ', 1)[1] for sys in mode.systems])
        row +=1
    plt.gcf().autofmt_xdate()


def format_subplot_legends(test, axes):
    voltage_labels = axes[0].get_legend_handles_labels()[1]
    axes[0].legend(fontsize=8, loc='center left', bbox_to_anchor=(1.0, 0.5))
    for i in range(len(test.modes)+2):
        if i == 0:
            continue
        if i == 1:  # temperature profile
            axes[i].legend(fontsize=8, loc='center left', bbox_to_anchor=(1.0, 0.5),
                           labels = test.thermocouples)
        # elif i == 2: # where to place currents legend based on number of modes being plotted
        #     vert = {1:0.5, 2:-0.25 , 3:-1.0 , 4:-1.75 , 5:-2.5 , 6:-3.25, 7: -4.0, 8: -4.75}
        #     axes[i].legend(fontsize=8, loc='center left', bbox_to_anchor=(1.0, vert[len(test.modes)]),
        #                    labels = test.systems)
        # else:
        #     try:
        #         axes[i].legend_.remove()
        #     except AttributeError as e:
        #         pass

def set_titles_and_labels(test, fig, axes):
    fig.canvas.set_window_title('temporal plot')
    for i in range(len(test.modes)):
        axes[i+2].set_title(test.modes[i].name)
        axes[i+2].set_ylabel("Current (A)")
    axes[0].set_ylabel("Voltage (V)")
    axes[0].set_ylim([0,20])
    axes[0].set_title("Voltage and Functional Cycle")
    axes[1].set_ylabel(u"Temp (\N{DEGREE SIGN}C)")
    axes[1].set_title("Temperature Profile") 


def set_figure_size(fig, save=False):
    plt.tight_layout()
    fig.subplots_adjust(top=0.900, bottom=0.075, left=0.070, right=0.760, hspace=0.330)


def set_up_date_time(test, ax):
    ax.plot_date(test.df.index.to_pydatetime(), test.df[test.vsetpoint], 'k--', 
                      linewidth=3, zorder=10)
    date_fmt = '%m/%d/%y %H:%M:%S'
    formatter = dates.DateFormatter(date_fmt)
    locator = dates.AutoDateLocator()
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(locator)


### MAIN PLOTTING FUNCTIONS ###
def plot_modes(test, limits=None):
    ''' Creates a temporal plot of the functional cycle, temperature profile, and test mode currents '''
    print('\nPlotting temporal plot...')

    fig, axes = set_up_plot_area(test)  # set up figure and axes for plotting
    axes[0].plot_date(test.df.index.to_pydatetime(), test.df[test.VSETPOINT], 'k--', 
                      linewidth=3, zorder=10)  # plot voltage setpoint on first subplot
    format_date_time(test, axes)  # format and plot date time index 

    plot_voltage_fc(test, axes)  ## subplot 1: voltage and functional cycle
    test.df[test.thermocouples].plot(ax=axes[1])  ## subplot 2: temperatures
    plot_mode_currents(test, axes)  ## subplots 3 to XX (up to 6): mode currents
    
    format_subplot_legends(test, axes) ## format or remove legends
    set_titles_and_labels(test, fig, axes) ## give axis labels and titles to subplots
    set_figure_size(fig) ## set fig size

    print('...complete.')


def plot_boards(test, limits=None, pstyle = 'ggplot'):
    ''' Creates a temporal plot of the FC, temperature profile, and board currents '''
    print('Plotting temporal plot...')
    fig, axes = set_up_plot_area(test)  # set up figure and axes for plotting
    ### TO DO: write funciton to plot boards

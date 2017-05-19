#!/usr/bin/python3

''' This module contains functions that create current histograms using matplotlib. '''

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from core.data_import.helpers import *


def make_mode_histograms(test, system_by_system=True, limits=None):
    print('Plotting histograms...\n')
    for mode in test.modes:
        for temp in mode.temps:         
            if system_by_system:
                histogram_of_each_system(test, mode, temp, limits)
            else:
                histogram_of_mode(test, mode, temp, limits)
    print('complete.')
    # plt.show('hold') ## wait until all plots are built to show them

def histogram_of_each_system(test, mode, temp, limits=None):
    for voltage in mode.voltages: ## make plot for mode in each voltage
        num_subplots = len(mode.systems)
        fig = plt.figure()
        bar_color = determine_bar_color(temp)
        if limits: ## if doing limit analysis
            LL, UL = limits.lim[temp][mode.mode_tag][voltage][0], limits.lim[temp][mode.mode_tag][voltage][1]
            title = ' '.join([mode.name, str(temp), str(voltage), ' LL:', str(LL), ' UL:', str(UL)])
        else:
            title = ' '.join([mode.name, str(temp), str(voltage)])
        fig.canvas.set_window_title(title)
        fig.suptitle(title, fontsize = 14, fontweight='bold')

        nrows, ncols = make_subplot_layout(num_subplots)
        i = 1
        for system in mode.systems:
            filtered_df = filter_temp_and_voltage(mode.df[[mode.AMB_TEMP, mode.VSETPOINT, system]], temp, voltage)
            current_data = pd.to_numeric(filtered_df[system], downcast='float')
            avg = current_data.mean()
            sigma = current_data.std()
            ax = fig.add_subplot(nrows, ncols, i)
            ax.set_title(test.systems[i-1])
            ax.hist(current_data.dropna(), color=bar_color)  ## drop NaN values
            ax.axvline(avg, color='dimgray', linestyle='dotted', linewidth=4)
            if limits:
                ax.axvline(LL, color='red', linestyle='dashed', linewidth=2)
                ax.axvline(UL, color='red', linestyle='dashed', linewidth=2)
            else:
                ax.axvline(avg-3*sigma, color='b', linestyle='dashed', linewidth=2)
                ax.axvline(avg+3*sigma, color='b', linestyle='dashed', linewidth=2)
            ax.set_xlabel('Current (A)')
            ax.set_ylabel('Frequency')
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            i += 1

def histogram_of_mode(test, mode, temp, limits=None):
    fig = plt.figure()
    nrows, ncols = len(mode.voltages), 1
    main_title = ' '.join([mode.name, str(temp)])
    fig.canvas.set_window_title(main_title)
    fig.suptitle(main_title, fontsize = 14, fontweight='bold')

    i = 1
    for voltage in mode.voltages: # make subplot for each voltage
        if limits: ## if doing limit analysis
            LL, UL = get_limits_at_mode_temp_voltage(limits, mode, temp, voltage)
            subtitle = ' '.join([str(voltage)+'V', ' LL:', str(LL), ' UL:', str(UL)])
        else:
            subtitle = str(voltage)+'V' 
        dframe = mode.hist_dict[temp][voltage]
        current_data = mode.strip_index_and_melt_to_series(dframe)
        avg = current_data.mean()
        sigma = current_data.std()
        minus_ten = round(avg*0.9, 3)
        plus_ten = round(avg*1.1, 3)

        ax = fig.add_subplot(nrows, ncols, i)
        ax.hist(current_data.dropna(), color='dimgray')  ## drop NaN values
        ax.axvline(avg, color='k', linestyle='dotted', linewidth=2)
        if limits:
            ax.axvline(LL, color='red', linestyle='dashed', linewidth=2)
            ax.axvline(UL, color='red', linestyle='dashed', linewidth=2)
        else:
            ax.axvline(avg-3*sigma, color='b', linestyle='dashed', linewidth=2)
            ax.axvline(avg+3*sigma, color='b', linestyle='dashed', linewidth=2)
        ax.set_title(subtitle)
        ax.set_xlabel('Current (A)', fontsize=8)
        ax.set_ylabel('Frequency', fontsize=8)
        plt.setp(ax.get_xticklabels(), fontsize=8)
        plt.setp(ax.get_yticklabels(), fontsize=8)
        i += 1

    plt.tight_layout()
    plt.subplots_adjust(top=0.87, bottom=0.05, left=0.07, right=0.97)


def make_subplot_layout(num):
    nrows, ncols = 0, 0
    if num > 10:
        nrows, ncols = 3, 4
    elif num == 10:
        nrows, ncols = 2, 5
    elif num == 9:
        nrows, ncols = 3, 3
    elif num > 6:
        nrows, ncols = 2, 4
    elif num > 4:
        nrows, ncols = 2, 3
    elif num == 4:
        nrows, ncols = 2, 2
    else:
        nrows, ncols = 1, num   
    return nrows, ncols

def determine_bar_color(temp):
    if temp == 23:
        return 'green'
    elif temp > 23:
        return 'orange'
    else:
        return 'blue'
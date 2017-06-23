#!/usr/bin/python3

''' This module contains functions that create current histograms using matplotlib. '''

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from core.data_import.helpers import *


def make_mode_histograms(test, system_by_system=True, limits=None, percent_from_mean=10):
    print('Plotting histograms...\n')
    for mode in test.modes:
        for temp in mode.temps:
            if system_by_system:
                if temp in mode.hist_dict:
                    histogram_of_each_system(test, mode, temp, limits, percent_from_mean)
            else:
                if temp in mode.hist_dict:
                    histogram_of_mode(test, mode, temp, limits, percent_from_mean)
    print('complete.')


def histogram_of_each_system(test, mode, temp, limits=None, percent_from_mean=10):
    for voltage in mode.voltages: ## make plot for mode in each voltage
        num_subplots = len(mode.systems)
        fig = plt.figure()
        bar_color = determine_bar_color(temp)
        title = ' '.join([test.name+'\n', mode.name, str(temp), str(voltage)])
        if limits and test.run_limit_analysis: ## if doing limit analysis
            mode_limits_dict = get_limits_at_mode_temp_voltage(limits, mode, temp, voltage)
            if mode.has_led_binning:
                for lim_label, lim_value in sorted(mode_limits_dict.items()):
                    title += '  ' + lim_label + ': ' + str(lim_value)
            else:
                LL, UL = mode_limits_dict['LL'], mode_limits_dict['UL']
                title += '  LL: ' + str(LL) + '  UL: ' + str(UL)
        else:
            title = ' '.join([mode.name, str(temp), str(voltage)])
        fig.canvas.set_window_title(title.replace('\n', ' '))
        fig.suptitle(title, fontsize = 14, fontweight='bold')

        nrows, ncols = make_subplot_layout(num_subplots)
        i = 1
        for system in mode.systems:
            filtered_df = filter_temp_and_voltage(mode.df[[mode.AMB_TEMP, mode.VSETPOINT, system]], 
                          temp, voltage, mode.test.temperature_tolerance)
            current_data = pd.to_numeric(filtered_df[system], downcast='float')
            avg = current_data.mean()
            sigma = current_data.std()
            minus_ten = round(avg*(1-(percent_from_mean/100.0)), 3)
            plus_ten = round(avg*(1+(percent_from_mean/100.0)), 3)
            ax = fig.add_subplot(nrows, ncols, i)
            ax.hist(current_data.dropna(), color=bar_color)  ## drop NaN values
            ax.axvline(avg, color='dimgray', linestyle='dotted', linewidth=4)

            if limits and test.run_limit_analysis:  ## show current limits
                if mode.has_led_binning:
                    led_bin = get_system_bin(mode, system)
                    mode_limits_dict = get_limits_for_system_with_binning(limits, mode, temp, voltage, system)
                    LL, UL = mode_limits_dict['LL'], mode_limits_dict['UL']
                ax.axvline(LL, color='orangered', linestyle='dashed', linewidth=2)
                ax.axvline(UL, color='orangered', linestyle='dashed', linewidth=2)
            else:
                ax.axvline(minus_ten, color='b', linestyle='dashed', linewidth=2)
                ax.axvline(plus_ten, color='b', linestyle='dashed', linewidth=2)
            ax.set_title(test.systems[i-1]+'\n'+'(Avg: '+str(round(avg,3))+'A)')
            ax.set_xlabel('Current (A)')
            ax.set_ylabel('Frequency')
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
            i += 1
    plt.tight_layout()
    plt.subplots_adjust(top=0.87, bottom=0.05, left=0.07, right=0.97)


def histogram_of_mode(test, mode, temp, limits=None, percent_from_mean=10):
    if mode.has_led_binning:
        for led_bin in mode.led_bins: ## make each bin histogram
            histogram_of_mode_with_binning(test, mode, temp, limits, led_bin, percent_from_mean)
    else:
        histogram_of_mode_no_binning(test, mode, temp, limits, percent_from_mean)

            
def histogram_of_mode_with_binning(test, mode, temp, limits, led_bin, percent_from_mean):

    fig = plt.figure()
    nrows, ncols = len(mode.voltages), 1
    main_title = ' '.join([test.name+'\n', mode.name, str(temp)+u'\N{DEGREE SIGN}'+'C', ' LED bin', led_bin])
    fig.canvas.set_window_title(main_title.replace('\n', ' '))
    fig.suptitle(main_title, fontsize = 14, fontweight='bold')

    i = 1
    for voltage in mode.voltages: # make subplot for each voltage
        dframe = mode.hist_dict[temp][voltage]
        current_data = mode.strip_index_and_melt_to_series_for_binning(dframe, led_bin) ## put all system currents in single series
        avg = current_data.mean()
        sigma = current_data.std()
        minus_ten = round(avg*(1-(percent_from_mean/100.0)), 3)
        plus_ten = round(avg*(1+(percent_from_mean/100.0)), 3)

        subtitle = str(voltage)+'V'+'  Avg: '+str(round(avg, 3))
        ax = fig.add_subplot(nrows, ncols, i)
        ax.hist(current_data.dropna(), color='dimgray')  ## drop NaN values
        ax.axvline(avg, color='k', linestyle='dotted', linewidth=2)
        if limits and test.run_limit_analysis:  ## show current limits
            mode_limits_dict = get_limit_for_single_led_bin(led_bin, limits, mode, temp, voltage)
            for lim_label, lim_value in sorted(mode_limits_dict.items()):
                subtitle += '  ' + lim_label + ': ' + str(lim_value)
                ax.axvline(lim_value, color='orangered', linestyle='dashed', linewidth=2)
        else:  ## show +- percent from mean
            subtitle += '   Iin' + u'\N{PLUS-MINUS SIGN}'+str(percent_from_mean)+'%: ' + \
                        str(minus_ten) + ' to ' + str(plus_ten)
            ax.axvline(minus_ten, color='b', linestyle='dashed', linewidth=2)
            ax.axvline(plus_ten, color='b', linestyle='dashed', linewidth=2)
        ax.set_title(subtitle)
        ax.set_xlabel('Current (A)', fontsize=8)
        ax.set_ylabel('Frequency', fontsize=8)
        plt.setp(ax.get_xticklabels(), fontsize=8)
        plt.setp(ax.get_yticklabels(), fontsize=8)
        i += 1
    plt.tight_layout()
    plt.subplots_adjust(top=0.87, bottom=0.05, left=0.07, right=0.97)


def histogram_of_mode_no_binning(test, mode, temp, limits, percent_from_mean):

    fig = plt.figure()
    nrows, ncols = len(mode.voltages), 1
    main_title = ' '.join([test.name+'\n', mode.name, str(temp)+u'\N{DEGREE SIGN}'+'C'])
    fig.canvas.set_window_title(main_title.replace('\n', ' '))
    fig.suptitle(main_title, fontsize = 14, fontweight='bold')

    i = 1
    for voltage in mode.voltages: # make subplot for each voltage
        dframe = mode.hist_dict[temp][voltage]
        current_data = mode.strip_index_and_melt_to_series(dframe) ## put all system currents in single series
        avg = current_data.mean()
        sigma = current_data.std()
        minus_ten = round(avg*(1-(percent_from_mean/100.0)), 3)
        plus_ten = round(avg*(1+(percent_from_mean/100.0)), 3)

        subtitle = str(voltage)+'V'+'  Avg: '+str(round(avg, 3))
        ax = fig.add_subplot(nrows, ncols, i)
        ax.hist(current_data.dropna(), color='dimgray')  ## drop NaN values
        ax.axvline(avg, color='k', linestyle='dotted', linewidth=2)
        if limits and test.run_limit_analysis:  ## show current limits
            mode_limits_dict = get_limits_at_mode_temp_voltage(limits, mode, temp, voltage)
            for lim_label, lim_value in sorted(mode_limits_dict.items()):
                subtitle += '  ' + lim_label + ': ' + str(lim_value)
                ax.axvline(lim_value, color='orangered', linestyle='dashed', linewidth=2)
        else:  ## show +- percent from mean
            subtitle += '   Iin' + u'\N{PLUS-MINUS SIGN}'+str(percent_from_mean)+'%: ' + \
                        str(minus_ten) + ' to ' + str(plus_ten)
            ax.axvline(minus_ten, color='b', linestyle='dashed', linewidth=2)
            ax.axvline(plus_ten, color='b', linestyle='dashed', linewidth=2)
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
        return '#7F7FFF' ## pale blue
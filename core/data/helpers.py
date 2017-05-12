#!/usr/bin/python3

import pandas as pd
from core.re_and_global import * 

### ------- Helper Functions ------- ###

def rename_columns(mdf, board, columns):
    ''' This is a helper function that adds the board number to the labels of the
        input columns. Used for creating 'mother' dataframe for TestStation object. '''
    for column_label in columns:
        mdf.rename(columns={column_label: column_label+' '+board.id}, inplace=True)
    return mdf

def mask_to_mode(mask, board_ids):
    ''' Translates a board mask (e.g.- '1001') 
        to a board mode (e.g.- 'B3B4') '''
    mode = ''
    i = 0
    for binary_digit in mask:
        if int(binary_digit):
            mode += board_ids[i]
        i += 1
    return mode

def copy_and_remove_b6_from(a_list):
    ''' Removes B6 (outage) from input board list '''
    b_list = a_list.copy()
    try:
        b_list.remove('B6')  # remove outage
    except ValueError:
        pass  # do nothing
    return b_list

def get_limits_at_mode_temp_voltage(limits, mode, temp, voltage):
    ''' Attempt to pull mode/temp/voltage condition current limits from limits file '''
    try:
        lower_limit = limits.lim[temp][mode.mode_tag][voltage][0]
        upper_limit = limits.lim[temp][mode.mode_tag][voltage][1]
        return lower_limit, upper_limit
    except:
        raise

def filter_temp_and_voltage(df, temp, voltage):
    ''' Filter input dataframe (df) for temp voltage condition'''
    dframe = df.loc[(df[VSETPOINT] == voltage) &
                    (df[AMB_TEMP] > (temp-TEMPERATURE_TOLERANCE)) &
                    (df[AMB_TEMP] < (temp+TEMPERATURE_TOLERANCE))]
    return dframe


### Stats helpers
def get_system_stats_at_mode_temp_voltage(system, mode, temp, voltage):
    ''' Return basic stats for input system at mode/temp/voltage condition '''
    series = mode.hist_dict[temp][voltage][system]
    return series.min(), series.max(), series.mean(), series.std()

def get_vsense_stats_at_mode_temp_voltage(vsense, mode, temp, voltage):
    ''' Return basic stats for vsense at mode/temp/voltage condition '''
    dframe = filter_temp_and_voltage(mode.df, temp, voltage)
    series = dframe[vsense]
    return series.min(), series.max(), series.mean()


### Out of spec helpers
def check_if_out_of_spec(lower_limit, upper_limit, sys_min, sys_max):
    ''' Return True/False if system min/max is out of spec '''
    return (sys_min < lower_limit) or (sys_max > upper_limit)

def write_out_of_spec_to_file(df, mode, temp, voltage):
    ''' Append out of spec mode/temp/voltage condition to out of spec file '''
    with open('!output//out_of_spec.txt', 'a+') as f:
        f.write('\t'.join(['\n\n\n\n\n' + str(temp) + u'\N{DEGREE SIGN}C',
                mode.name, str(voltage) + 'V', '\n']))
    df.to_csv('!output//out_of_spec.txt', header=df.columns,
                              index=True, sep='\t', mode='a')


### Ipython helper (jupyter)
def run_from_ipython():
    ''' Returns true if program is being run from ipython interactive shell '''
    try:
        __IPYTHON__
        return True
    except NameError:
        return False
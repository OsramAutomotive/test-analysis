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

def rotate_mask(mask, n):
    ''' e.g. - 1000 => 0100 '''
    return mask[-n:] + mask[:-n]

def create_turn_mask(boards):
    turn_mask = ''
    for b in boards:
        if b == 'B5' or b == 'B6':
            turn_mask += '1'
        else:
            turn_mask += '0'
    return turn_mask

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


### Limits helpers
def get_limits_at_mode_temp_voltage(limits, mode, temp, voltage):
    ''' Attempt to pull mode/temp/voltage condition current limits from limits file '''
    if mode.has_led_binning:
        mode_limits_dict = get_all_mode_limits_with_binning(limits, mode, temp, voltage)
    else:
        mode_limits_dict = get_limits_without_binning(limits, mode, temp, voltage)
    return mode_limits_dict

def get_limits_without_binning(limits, mode, temp, voltage):
    try:
        lower_limit = limits.lim[temp][mode.name][voltage][0]
        upper_limit = limits.lim[temp][mode.name][voltage][1]
        return {'LL': lower_limit, 'UL': upper_limit}
    except:
        raise

def get_all_mode_limits_with_binning(limits, mode, temp, voltage):
    mode_bin_limits_dict = {}
    for led_bin in mode.led_bins:
        module_header = led_bin + ' ' + mode.name
        try:
            mode_bin_limits_dict[led_bin+' LL'] = limits.lim[temp][module_header][voltage][0]
            mode_bin_limits_dict[led_bin+' UL'] = limits.lim[temp][module_header][voltage][1]
        except:
            raise
    return mode_bin_limits_dict

def get_limit_for_single_led_bin(led_bin, limits, mode, temp, voltage):
    mode_bin_limits_dict = {}
    module_header = led_bin + ' ' + mode.name
    try:
        mode_bin_limits_dict[led_bin+' LL'] = limits.lim[temp][module_header][voltage][0]
        mode_bin_limits_dict[led_bin+' UL'] = limits.lim[temp][module_header][voltage][1]
    except:
        raise
    return mode_bin_limits_dict

def get_limits_for_system_with_binning(limits, mode, temp, voltage, system):
    led_bin = get_system_bin(mode, system)
    module_header = led_bin + ' ' + mode.name
    try:
        lower_limit = limits.lim[temp][module_header][voltage][0]
        upper_limit = limits.lim[temp][module_header][voltage][1]
        return {'LL': lower_limit, 'UL': upper_limit}
    except:
        raise

def get_system_bin(mode, system):
    possible_bins = system.split(' ')
    for led_bin in possible_bins:
        if led_bin in mode.led_bins:
            return led_bin

def get_limits_for_outage_off(limits, board):
    try:
        lower_limit = limits.lim[board.name]['OFF'][0]
        upper_limit = limits.lim[board.name]['OFF'][1]
        return {'LL': lower_limit, 'UL': upper_limit}
    except:
        raise

def get_limits_for_outage_on(limits, board, voltage):
    try:
        lower_limit = limits.lim[board.name]['ON'][voltage][0]
        upper_limit = limits.lim[board.name]['ON'][voltage][1]
        return {'LL': lower_limit, 'UL': upper_limit}
    except:
        raise

### Dataframe filter functions
def filter_temp_and_voltage(df, temp, voltage):
    ''' Filter input dataframe (df) for temp voltage condition'''
    dframe = df.loc[(df[VSETPOINT] == voltage) &
                    (df[AMB_TEMP] > (temp-TEMPERATURE_TOLERANCE)) &
                    (df[AMB_TEMP] < (temp+TEMPERATURE_TOLERANCE))]
    return dframe

def filter_temperature(df, temp):
    ''' Filter input dataframe (df) for temperature condition'''
    dframe = df.loc[(df[AMB_TEMP] > (temp-TEMPERATURE_TOLERANCE)) &
                    (df[AMB_TEMP] < (temp+TEMPERATURE_TOLERANCE))]
    return dframe

def filter_board_on_or_off(df, board_on_off_code):
    ''' board_on_off_code: 0 is off, 1 is on, 2 is flashing '''
    dframe = df.loc[(df[ON_OFF] == board_on_off_code)]
    return dframe


### Stats helpers
def get_system_stats_at_mode_temp_voltage(system, mode, temp, voltage):
    ''' Return basic stats for input system at mode/temp/voltage condition '''
    decimal_places = 3
    if temp in mode.hist_dict:
        if voltage in mode.hist_dict[temp]:
            series = mode.hist_dict[temp][voltage][system]
        if not series.empty:
            return round(series.min(), decimal_places), round(series.max(), decimal_places), \
                   round(series.mean(), decimal_places), round(series.std(), decimal_places)
    return 'NA', 'NA', 'NA', 'NA'

def get_vsense_stats_at_mode_temp_voltage(vsense, mode, temp, voltage):
    ''' Return basic stats for vsense at mode/temp/voltage condition '''
    decimal_places = 3
    dframe = filter_temp_and_voltage(mode.df, temp, voltage)
    series = dframe[vsense]
    if not series.empty:
        return round(series.min(), decimal_places), round(series.max(), decimal_places), \
               round(series.mean(), decimal_places)
    else:
        return 'NA', 'NA', 'NA'


### Outage analysis helpers
def get_outage_on_stats_at_temp_voltage(df, board, system, temp, voltage):
    ''' Return basic stats for outage at temp/voltage condition'''
    decimal_places = 3
    dframe = filter_temp_and_voltage(df, temp, voltage)
    series = dframe[system]
    if not series.empty:
        return round(series.min(), decimal_places), round(series.max(), decimal_places), \
               round(series.mean(), decimal_places)
    else:
        return 'NA', 'NA', 'NA'

def get_outage_off_stats_single_sys(df, board, system, temp):
    decimal_places = 3
    dframe = filter_temperature(df, temp)
    series = dframe[system]
    if not series.empty:
        return round(series.min(), decimal_places), round(series.max(), decimal_places), \
               round(series.mean(), decimal_places)
    else:
        return 'NA', 'NA', 'NA'

### Out of spec helpers
def check_if_out_of_spec(lower_limit, upper_limit, sys_min, sys_max):
    ''' Return True/False if system min/max is out of spec '''
    if isinstance(sys_min, float):
        return (sys_min < lower_limit) or (sys_max > upper_limit)
    else:
        return sys_min

def write_out_of_spec_to_file(df, mode, temp, voltage):
    ''' Append out of spec mode/temp/voltage condition to out of spec file '''
    with open('!output//out_of_spec.txt', 'a+') as f:
        f.write('\t'.join(['\n\n\n\n\n' + str(temp) + u'\N{DEGREE SIGN}C',
                mode.name, str(voltage) + 'V', '\n']))
    df.to_csv('!output//out_of_spec.txt', header=df.columns,
                              index=True, sep='\t', mode='a')


## Dictionary cleaner
def clean_empty_keys(d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty_keys(v) for v in d) if v]
    return {k: v for k, v in ((k, clean_empty_keys(v)) for k, v in d.items()) if v}


### Ipython helper (jupyter)
def run_from_ipython():
    ''' Returns true if program is being run from ipython interactive shell '''
    try:
        __IPYTHON__
        return True
    except NameError:
        return False
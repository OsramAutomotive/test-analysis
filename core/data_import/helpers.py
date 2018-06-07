#!/usr/bin/python3

""" 
This module contains helper functions...
"""

import re
from core.re_and_global import VSETPOINT, ON_OFF


def rename_columns(mdf, board, columns):
    """ Renames columns of input dataframe by adding board number to the col labels.
        Used for creating 'mother' dataframe for TestStation object.
    Args:
        mdf (dataframe): Dataframe of a TestStation object
        board (string): Board id to add to col labels (e.g. - 'B4')
        columns (list of dataframe columns): Dataframe columns to rename
    Returns:
        mdf (dataframe): The dataframe with renamed column labels
    """
    for column_label in columns:
        mdf.rename(columns={column_label: column_label+' '+board.id}, 
                   inplace=True)
    return mdf

def rotate_mask(mask, n):
    """ e.g. - 1000 => 0100 """
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
    """ Translates a board mask (e.g.- '1001')
        to a board mode (e.g.- 'B3B4') """
    mode = ''
    i = 0
    for binary_digit in mask:
        if int(binary_digit):
            mode += board_ids[i]
        i += 1
    return mode

def copy_and_remove_b6_from(list_of_boards):
    """ Removes B6 (Outage) from input board list
    Args:
        list_of_boards (list): List of boards represented by strings
    Returns:
        list_without_outage (list): List of boards with B6 (Outage) removed
    """
    list_without_outage = list_of_boards.copy()
    try:
        list_without_outage.remove('B6')  # remove outage
    except ValueError as e:
        print(e)
    return list_without_outage

def get_system_test_position_int(system, index=0):
    """ Find test position of input system
    Args:
        system (string): System name (e.g. - 'TP1: System 106')
        index (int): Default zero. Piece of the system name for extraction of TP
    Returns:
        test_position_num (int): Test position number of the input test system
    """
    test_position_num = system.split(' ')[index]
    test_position_num = re.sub('[^0-9]', '', test_position_num)
    try:
        test_position_num = int(test_position_num)
    except:
        pass
    return test_position_num

# Dataframe filter functions
def filter_temp_and_voltage(df, ambient, temp, voltage, temperature_tolerance):
    """ Filter input dataframe by temp/voltage condition
    Args:
        df (dataframe): Dataframe to be filtered
        ambient (string): Dataframe column name/label of test ambient thermocouple
        temp (int): Temperature to filter by
        voltage (float): Voltage to filter by
        temperature_tolerance (float): Temperature tolerance (default is 5.0°C)
    Returns:
        dframe (dataframe): Filtered dataframe
    """
    dframe = df.loc[(df[VSETPOINT] == voltage) &
                    (df[ambient] > (temp-temperature_tolerance)) &
                    (df[ambient] < (temp+temperature_tolerance))]
    return dframe

def filter_temperature(df, ambient, temp, temperature_tolerance):
    """ Filter input dataframe by temperature condition
    Args:
        df (dataframe): Dataframe to be filtered
        ambient (string): Dataframe column name/label of test ambient thermocouple
        temp (int): Temperature to filter by
        temperature_tolerance (float): Temperature tolerance (default is 5.0°C)
    Returns:
        dframe (dataframe): Filtered dataframe
    """
    dframe = df.loc[(df[ambient] > (temp-temperature_tolerance)) &
                    (df[ambient] < (temp+temperature_tolerance))]
    return dframe

def filter_board_on_or_off(df, board_id, board_on_off_code):
    """ Filter input dataframe by board_on_off_code
    Args:
        df (dataframe): Dataframe to be filtered
        board_id (string): Board ID string (e.g. - 'B4')
        board_on_off_code (int): 0 is off, 1 is on, 2 is flashing
    Returns:
        dframe (dataframe): Filtered dataframe
    """
    dframe = df.loc[(df[board_id + ' ' + ON_OFF] == board_on_off_code)]
    return dframe

# Stats helpers
def get_system_stats_at_mode_temp_voltage(system, mode, temp, voltage):
    """ Get basic stats for input system at mode/temp/voltage condition
    Args:
        system (string): Dataframe column name/label of system to be analyzed
        mode (Mode object): Mode to be analyzed
        temp (int): Temperature condition to analyze at
        voltage (float): Voltage condition to analyze at
    Returns:
        stats at mode/temp/voltage condition (tuple): min, max, mean, stdev
    """
    decimal_places = 3
    if temp in mode.hist_dict:
        if voltage in mode.hist_dict[temp]:
            series = mode.hist_dict[temp][voltage][system]
            if not series.empty:
                return round(series.min(), decimal_places),  \
                       round(series.max(), decimal_places),  \
                       round(series.mean(), decimal_places), \
                       round(series.std(), decimal_places)
    return 'NA', 'NA', 'NA', 'NA'

def get_vsense_stats_at_mode_temp_voltage(vsense, mode, temp, voltage):
    """ Return basic stats for vsense at mode/temp/voltage condition """
    decimal_places = 3
    dframe = filter_temp_and_voltage(mode.df, mode.test.ambient, temp,
                                     voltage, mode.test.temperature_tolerance)
    series = dframe[vsense]
    if not series.empty:
        return round(series.min(), decimal_places),  \
               round(series.max(), decimal_places),  \
               round(series.mean(), decimal_places), \
               round(series.std(), decimal_places)
    return 'NA', 'NA', 'NA', 'NA'

# Outage analysis helpers
def get_outage_stats_at_temp_voltage(df, board, system, temp, voltage):
    """ Return basic stats for outage at temp/voltage condition """
    decimal_places = 3
    dframe = filter_temp_and_voltage(df, board.test.ambient, temp, voltage, \
                                     board.test.temperature_tolerance)
    series = dframe[system]
    if not series.empty:
        return round(series.min(), decimal_places),  \
               round(series.max(), decimal_places),  \
               round(series.mean(), decimal_places), \
               round(series.std(), decimal_places)
    return 'NA', 'NA', 'NA', 'NA'

def get_outage_off_stats_single_sys(df, board, system, temp):
    """ Return outage stats for input system at input temp """
    decimal_places = 3
    dframe = filter_temperature(df, board.test.ambient, temp, \
                                board.test.temperature_tolerance)
    series = dframe[system]
    if not series.empty:
        return round(series.min(), decimal_places),  \
               round(series.max(), decimal_places),  \
               round(series.mean(), decimal_places), \
               round(series.std(), decimal_places)
    return 'NA', 'NA', 'NA', 'NA'

# Out of spec helpers
def check_if_out_of_spec(lower_limit, upper_limit, sys_min, sys_max):
    """ Return True/False if system min/max is out of spec """
    if isinstance(sys_min, float):
        return (sys_min < lower_limit) or (sys_max > upper_limit)
    return sys_min

def count_num_out_of_spec(series, lower_limit, upper_limit):
    """ Finds the out of spec data in input series
    Args:
        series (Series object): Data to be analyzed (e.g. - Sys 10 current)
        lower_limit (float): lower limit for data comparison
        upper_limit (float): upper limit for data comparison
    Returns:
        total count (int): total number of scans in series
        count_out_of_spec (int): number of scans outside of limits
        percent_out (string): percentage of scans outside of limits
    """
    total_count = series.count()
    count_out_of_spec = series[(series < lower_limit) | (series > upper_limit)].count()
    if total_count == 0:
        percent_out = '0.0%'
    else:
        percent_out = '%.2f' % (round(count_out_of_spec/total_count, 4)*100)
        percent_out += '%'
    return total_count, count_out_of_spec, percent_out

def write_out_of_spec_to_file(file, df, mode, temp, voltage):
    """ Append out of spec mode/temp/voltage condition to out of spec file """
    condition_header = '\t'.join(['\n\n\n\n\n' + str(temp) + u'\N{DEGREE SIGN}C',
                          mode.name, str(voltage) + 'V', '\n'])
    file.write(condition_header, df)

# Miscellaneous helpers
def retrieve_board_name(board_id, test_boards):
    """ Try to retrieve board name from input board id """
    for board in test_boards:
        if (board.id == board_id) and (board.name):
            return board.name
    return board_id

def replace_board_id_with_board_name(col_label, test_boards):
    board_id = col_label.split(' ')[0]
    board_name = retrieve_board_name(board_id, test_boards)
    return col_label.replace(board_id, board_name)

def delete_all_object_attributes(obj):
    for attr in list(obj.__dict__.keys()):
        delattr(obj, attr)

def clean_empty_keys(d):
    """ Removes empty keys from input dictionary """
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (clean_empty_keys(v) for v in d) if v]
    return {k: v for k, v in ((k, clean_empty_keys(v)) for k, v in d.items()) if v}

def run_from_ipython():
    """ Returns true if program is being run from ipython (jupyter) interactive shell """
    try:
        __IPYTHON__
        return True
    except NameError:
        return False

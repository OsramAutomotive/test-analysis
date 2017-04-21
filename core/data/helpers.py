#!/usr/bin/python3

from core.re_and_global import * 

### ------- Helper Functions for data package ------- ###

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
    try:  ## get current limits from limits file
        lower_limit, upper_limit = limits.lim[temp][mode.mode_tag][voltage][0], limits.lim[temp][mode.mode_tag][voltage][1]
        return lower_limit, upper_limit
    except:
        raise

def filter_temp_and_voltage(df, temp, voltage):
    dframe = df.loc[(df[VSETPOINT] == voltage) &
                    (df[AMB_TEMP] > (temp-TEMPERATURE_TOLERANCE)) &
                    (df[AMB_TEMP] < (temp+TEMPERATURE_TOLERANCE))]
    return dframe

def check_if_out_of_spec(lower_limit, upper_limit, sys_min, sys_max):
    return (sys_min < lower_limit) or (sys_max > upper_limit)

def get_system_stats_at_mode_temp_voltage(system, mode, temp, voltage):
    series = mode.hist_dict[temp][voltage][system]
    return series.min(), series.max(), series.mean(), series.std()

def get_vsense_stats_at_mode_temp_voltage(vsense, mode, temp, voltage):
    dframe = filter_temp_and_voltage(mode.df, temp, voltage)
    series = dframe[vsense]
    return series.min(), series.max(), series.mean()


    

#!/usr/bin/python3

''' This module uses "xlsxwriter" to create excel tables with conditional formatting
for out of spec currents/voltages and color modes as well. '''

import xlsxwriter
from core.data_import.mode import *
from core.re_and_global import *

def create_wb(filename):
    ''' Create a blank workbook '''
    return xlsxwriter.Workbook('!output/' + filename + '.xlsx')

def write_title_header(row_start, wb, ws, width, test_name):
    ''' Write a test title header for the table '''
    row, col = row_start, 0
    title_format = wb.add_format({'align': 'center', 'border': True, 'bold': True, 'font_color': 'black'})
    ws.merge_range(row, col, row, width, 'Test: ' + test_name, title_format)
    return row_start+1

def write_mode_temp_header(row_start, wb, ws, width, limits, color_dict, mode, temperature, voltage):
    ''' Write mode/temp/voltage header into row_start. Rows and columns are zero indexed. '''
    row, col = row_start, 0
    if mode.name in color_dict:
        bg_color = color_dict[mode.name]
    else:
        bg_color = 'gray'
    temperature_string = str(temperature) + u'\N{DEGREE SIGN}' + 'C'
    voltage_string = ''.join([str(voltage), 'V'])
    mode_string = '  '.join(['Mode:', mode.name, temperature_string, voltage_string])
    h_format = wb.add_format({'align':'center', 'border': True, 'bold': True,
                                    'font_color': 'black', 'bg_color': bg_color})
    ws.merge_range(row, col, row, width, mode_string, h_format)

def write_limits_header(row_start, wb, ws, width, limits, mode, temp, voltage):
    ''' Write limits header into the row after row_start '''
    row, col = row_start, 0
    if limits:
        LL, UL = get_limits_at_mode_temp_voltage(limits, mode, temp, voltage)
    else:
        LL, UL = None, None
    if False:  ## temporary until outage is implemented
        limits_string = 'LL: ' + str(LL) + '  UL: ' + str(UL)
    else:
        limits_string = ' '.join(['Limits:  ', 'Vin ', str(voltage)+u'\N{PLUS-MINUS SIGN}'+str(VOLTAGE_TOLERANCE)+'V', 
                                               'Iin '+str(LL)+' to '+ str(UL) + ' A'])
    lim_format = wb.add_format({'align':'center', 'border': True, 'bold': True,
                                      'font_color': 'black', 'bg_color': '#D3D3D3'})
    ws.merge_range(row, col, row, width, limits_string, lim_format)

def write_voltage_and_current_data(row_start, wb, ws, mode, temp, voltage, limits):
    ''' Starting from 3rd row, write in voltage/current data '''
    row = row_start
    decimal_places = 3
    d_format = wb.add_format({'align':'center', 'border': True, 'font_color': 'black'})

    header = ['TP:'] + mode.voltage_senses + mode.test.systems
    minimums = ['Min:'] + [mode.vsense_stats[temp][voltage][vsense][0] for vsense in mode.voltage_senses] + \
                          [mode.current_stats[temp][voltage][system][0] for system in mode.systems]
    maximums = ['Max:'] + [mode.vsense_stats[temp][voltage][vsense][1] for vsense in mode.voltage_senses] + \
                          [mode.current_stats[temp][voltage][system][1] for system in mode.systems]
    check_data = ['Check Data:'] + ['Out of Spec' if mode.vsense_stats[temp][voltage][vsense][-1] else 'G' for vsense in mode.voltage_senses]
    if limits:
        check_data += ['Out of Spec' if mode.current_stats[temp][voltage][system][-1] else 'G' for system in mode.systems]
    else:
        check_data += ['NA' for system in mode.systems]

    for data_line in (header, minimums, maximums, check_data):
        col = 0
        ws.write_row(row, col, data_line, d_format)
        row += 1
    return row

def highlight_workbook(wb, ws):
    out_of_spec_format = wb.add_format({'bg_color': 'yellow', 'font_color': 'red'})
    ws.conditional_format('A1:AZ600', {'type': 'text', 'criteria': 'containing', 'value': 'Out of Spec', 'format': out_of_spec_format})

def write_single_table(row_start, wb, ws, test, mode, temp, limits):
    width = len(mode.voltage_senses) + len(mode.systems)
    write_title_header(row_start, wb, ws, width, test.name)
    row_start += 1
    color_dict = TABLE_COLOR_DICT
    for voltage in mode.voltages:
        write_mode_temp_header(row_start, wb, ws, width, limits, color_dict, mode, temp, voltage)
        write_limits_header(row_start+1, wb, ws, width, limits, mode, temp, voltage)
        row_start = write_voltage_and_current_data(row_start+2, wb, ws, mode, temp, voltage, limits)
        if test.outage:
            pass
    return row_start+2

def fill_stats(test, limits=None, write_to_excel=True):
    ''' This function fills the mode objects with stats from test using mode method '''
    wb = create_wb(test.name)
    for temp in test.temps:
        ws = wb.add_worksheet(str(temp) + 'C') # add ws with temp as name
        row_start = 0  # start at row zero
        for mode in test.modes:
            print('\n\n\n*********', mode, '*********')
            mode.get_system_by_system_mode_stats(temp, limits)
            if write_to_excel:
                row_start = write_single_table(row_start, wb, ws, test, mode, temp, limits)
        highlight_workbook(wb, ws)
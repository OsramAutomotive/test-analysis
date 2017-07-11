#!/usr/bin/python3

''' This module uses "xlsxwriter" to create excel tables with conditional formatting
for out of spec currents/voltages and color modes as well. '''

import xlsxwriter
from core.data_import.mode import *
from core.data_import.board import *
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
    temperature_string = str(temperature) + u'\N{DEGREE SIGN}' + 'C' + u'\N{PLUS-MINUS SIGN}'+ \
                         str(mode.test.temperature_tolerance) + u'\N{DEGREE SIGN}' + 'C' 
    voltage_string = ''.join([str(voltage), 'V'])
    mode_string = '  '.join(['Mode:', mode.name, temperature_string, voltage_string])
    h_format = wb.add_format({'align':'center', 'border': True, 'bold': True,
                                    'font_color': 'black', 'bg_color': bg_color})
    ws.merge_range(row, col, row, width, mode_string, h_format)

def write_limits_header(row_start, wb, ws, width, test, mode, temp, voltage, limits):
    ''' Write limits header into the row after row_start '''
    row, col = row_start, 0
    limits_string = ' '.join(['Limits:  ', 'Vin ', str(voltage)+u'\N{PLUS-MINUS SIGN}'+str(test.voltage_tolerance)+'V'])
    if limits and test.run_limit_analysis:
        mode_limits_dict = get_limits_at_mode_temp_voltage(limits, mode, temp, voltage)
        if mode.has_led_binning:  ## led binning
            for lim_label, lim_value in sorted(mode_limits_dict.items()):
                limits_string += '  ' + lim_label + ': ' + str(lim_value) 
        else: ## no led binning
            limits_string += '  Iin '+str(mode_limits_dict['LL'])+' to '+ str(mode_limits_dict['UL']) + ' A'
    lim_format = wb.add_format({'align':'center', 'border': True, 'bold': True,
                                      'font_color': 'black', 'bg_color': '#D3D3D3'})
    ws.merge_range(row, col, row, width, limits_string, lim_format)

def write_voltage_and_current_data(row_start, wb, ws, test, mode, temp, voltage, limits):
    ''' Write in voltage/current data '''
    row = row_start
    decimal_places = 3
    d_format = wb.add_format({'align':'center', 'border': True, 'font_color': 'black'})

    header = ['TP:'] + mode.voltage_senses + mode.test.systems
    minimums = ['Min:'] + [mode.vsense_stats[temp][voltage][vsense][0] for vsense in mode.voltage_senses] + \
                          [mode.current_stats[temp][voltage][system][0] for system in mode.systems]
    maximums = ['Max:'] + [mode.vsense_stats[temp][voltage][vsense][1] for vsense in mode.voltage_senses] + \
                          [mode.current_stats[temp][voltage][system][1] for system in mode.systems]
    check_data = ['Check Data:'] + ['Out of Spec' if mode.vsense_stats[temp][voltage][vsense][-1] else 'G' for vsense in mode.voltage_senses]
    if limits and test.run_limit_analysis:
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
        write_limits_header(row_start+1, wb, ws, width, test, mode, temp, voltage, limits)
        row_start = write_voltage_and_current_data(row_start+2, wb, ws, test, mode, temp, voltage, limits)
    return row_start+2


### Outage tables
def write_outage_temp_header(row_start, wb, ws, width, limits, color_dict, outage_board, temp, voltage, outage_on_bool):
    ''' Write mode/temp/voltage header into row_start. Rows and columns are zero indexed. '''
    row, col = row_start, 0
    if outage_board.name in color_dict:
        bg_color = color_dict[outage_board.name]
    else:
        bg_color = 'gray'
    if outage_on_bool:
        mode_string = 'Mode:  '+outage_board.name+' '+'ON'
        voltage_string = ''.join([str(voltage), 'V'])
    else:
        mode_string = 'Mode:  '+outage_board.name+' '+'OFF'
        voltage_string = '(all voltages)'
    temp_string = str(temp) + u'\N{DEGREE SIGN}' + 'C'+ u'\N{PLUS-MINUS SIGN}'+str(outage_board.test.temperature_tolerance)
    title = '  '.join([mode_string, temp_string, voltage_string])
    h_format = wb.add_format({'align':'center', 'border': True, 'bold': True,
                                    'font_color': 'black', 'bg_color': bg_color})
    ws.merge_range(row, col, row, width, title, h_format)

def write_outage_on_limits_header(row_start, wb, ws, width, test, outage_board, voltage, limits):
    ''' Write outage limits header into the row after row_start '''
    row, col = row_start, 0
    limits_string = 'Limits:  '
    lim_format = wb.add_format({'align':'center', 'border': True, 'bold': True,
                                'font_color': 'black', 'bg_color': '#D3D3D3'})
    if limits and test.run_limit_analysis:
        limits_dict = get_limits_for_outage_on(limits, outage_board, voltage)
        limits_string += '  Voltage '+str(limits_dict['LL'])+' to '+ str(limits_dict['UL']) + ' V'
    ws.merge_range(row, col, row, width, limits_string, lim_format)

def write_outage_off_limits_header(row_start, wb, ws, width, test, outage_board, limits):
    ''' Write outage limits header into the row after row_start '''
    row, col = row_start, 0
    limits_string = 'Limits:  '
    lim_format = wb.add_format({'align':'center', 'border': True, 'bold': True,
                                'font_color': 'black', 'bg_color': '#D3D3D3'})
    if limits and test.run_limit_analysis:
        limits_dict = get_limits_for_outage_off(limits, outage_board)
        limits_string += '  Voltage '+str(limits_dict['LL'])+' to '+ str(limits_dict['UL']) + ' V'
    ws.merge_range(row, col, row, width, limits_string, lim_format)

def write_outage_on_data(row_start, wb, ws, test, outage_board, temp, voltage, limits):
    ''' Write in voltage/current data '''
    row = row_start
    decimal_places = 3
    d_format = wb.add_format({'align':'center', 'border': True, 'font_color': 'black'})
    header = ['TP:'] + outage_board.test.systems
    minimums = ['Min:'] + [outage_board.outage_stats['ON'][temp][voltage][system][0] for system in outage_board.systems]
    maximums = ['Max:'] + [outage_board.outage_stats['ON'][temp][voltage][system][1] for system in outage_board.systems]
    check_data = ['Check Data:']
    if limits and test.run_limit_analysis:
        check_data += ['Out of Spec' if outage_board.outage_stats['ON'][temp][voltage][system][-1] else 'G' for system in outage_board.systems]
    else:
        check_data += ['NA' for system in outage_board.systems]
    for data_line in (header, minimums, maximums, check_data):
        col = 0
        ws.write_row(row, col, data_line, d_format)
        row += 1
    return row

def write_outage_off_data(row_start, wb, ws, test, outage_board, temp, limits):
    ''' Write in voltage/current data '''
    row = row_start
    decimal_places = 3
    d_format = wb.add_format({'align':'center', 'border': True, 'font_color': 'black'})
    header = ['TP:'] + outage_board.test.systems
    minimums = ['Min:'] + [outage_board.outage_stats['OFF'][temp][system][0] for system in outage_board.systems]
    maximums = ['Max:'] + [outage_board.outage_stats['OFF'][temp][system][1] for system in outage_board.systems]
    check_data = ['Check Data:']
    if limits and test.run_limit_analysis:
        check_data += ['Out of Spec' if outage_board.outage_stats['OFF'][temp][system][-1] else 'G' for system in outage_board.systems]
    else:
        check_data += ['NA' for system in outage_board.systems]
    for data_line in (header, minimums, maximums, check_data):
        col = 0
        ws.write_row(row, col, data_line, d_format)
        row += 1
    return row

def write_outage_on_table(row_start, wb, ws, test, outage_board, temp, limits):
    width = len(outage_board.systems)
    write_title_header(row_start, wb, ws, width, test.name)
    row_start += 1
    color_dict = TABLE_COLOR_DICT
    for voltage in test.voltages:
        write_outage_temp_header(row_start, wb, ws, width, limits, color_dict, outage_board, temp, voltage, outage_on_bool=True)
        write_outage_on_limits_header(row_start+1, wb, ws, width, test, outage_board, voltage, limits)
        row_start = write_outage_on_data(row_start+2, wb, ws, test, outage_board, temp, voltage, limits)
    return row_start+2

def write_outage_off_table(row_start, wb, ws, test, outage_board, temp, limits):
    width = len(outage_board.systems)
    write_title_header(row_start, wb, ws, width, test.name)
    row_start += 1
    color_dict = TABLE_COLOR_DICT
    write_outage_temp_header(row_start, wb, ws, width, limits, color_dict, outage_board, temp, voltage=None, outage_on_bool=False)
    write_outage_off_limits_header(row_start+1, wb, ws, width, test, outage_board, limits)
    row_start = write_outage_off_data(row_start+2, wb, ws, test, outage_board, temp, limits)
    return row_start+2

def write_user_inputs_tab(test, wb):
    ws = wb.add_worksheet('user-inputs')
    user_inputs = [ ('Test Name: ',  test.name), 
                    ('Data Folder: ', test.folder), 
                    ('Limits File: ', test.limits.filepath),
                    ('Selected Temperatures: ', ' '.join(str(temp) for temp in test.temps)),
                    ('Selected Boards: ', ' '.join(str(board.id) for board in test.boards)), 
                    ('Limit Analysis: ', str(test.run_limit_analysis)),
                    ('Multimode: ', str(test.multimode)),
                    ('Temp Tolerance: ', str(test.temperature_tolerance)), 
                    ('Voltage Tolerance: ', str(test.voltage_tolerance)) ]
    row = 0
    for user_input in user_inputs:
        ws.write_row(row, 0, user_input)
        row += 1


#### MAIN WRITE FUNCTION ####
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
        if test.outage and write_to_excel:
            test.b6.get_system_by_system_outage_stats(temp, limits)
            row_start = write_outage_on_table(row_start, wb, ws, test, test.b6, temp, limits)
            row_start = write_outage_off_table(row_start, wb, ws, test, test.b6, temp, limits)
        highlight_workbook(wb, ws)
    write_user_inputs_tab(test, wb)
    wb.close()

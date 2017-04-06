#!/usr/bin/python3

''' This module uses "xlsxwriter" to create excel tables with conditional formatting
for out of spec currents/voltages and color modes as well. '''

import xlsxwriter

COLOR_DICT = { 'LB': '#FF5C5C', 'HB': '#FCFBE3', 'LBHB': '#7647A2', 'DRL': '#ADD8E6', 'PARK': '#FFA500', 
               'TURN': '#DA70D6', 'DRLTURN': '#40E0D0', 'PARKTURN': '#FF8C00' }

def create_wb_and_ws(filename):
    ''' Create a blank workbook and add a worksheet '''
    wb = xlsxwriter.Workbook('!output/' + filename + '.xlsx')
    ws = wb.add_worksheet(sheetname)
    return wb, ws

def excel_write_title_header(row_start, wb, wos, width, title_header):
    ''' Write a test title header for the table '''
    row, col = row_start, 0
    title_format = wb.add_format({'align': 'center', 'border': True, 'bold': True, 'font_color': 'black'})
    ws.merge_range(row, col, row, width, 'Test:     ' + title_header, title_format)
    return row_start+1

def write_mode_temp_header(row_start, wb, ws, color_dict):
    ''' Write mode/temp/voltage header into row_start. Rows and columns are zero indexed. '''
    row, col = row_start, 0
    if mode in color_dict:
        bg = color_dict[mode]
    else:
        bg = 'gray'
    temperature_string = str(temperature) + u'\N{DEGREE SIGN}' + 'C'
    voltage_string = ''.join([str(voltage), 'V'])
    mode_string = '  '.join(['Mode:   ', mode, temperature_string, voltage_string])
    h_format = wb.add_format({'align':'center', 'border': True, 'bold': True,
                                    'font_color': 'black', 'bg_color': bg})
    ws.merge_range(row, col, row, len(data[0])-1, mode_string, h_format)

def write_limits_header(row_start, limits):
    ''' Write limits header into the row after row_start '''
    row, col = row_start+1, 0
    voltage_lim_string = ' '.join([str(voltage)+u'\N{PLUS-MINUS SIGN}'+'0.5V'])
    limits_string = ''
    if 'outage' in mode.lower():
        limits_string = 'LL: ' + str(LL) + '  UL: ' + str(UL)
    else:
        limits_string = '     '.join(['Limits:  ', 'Vin ' + voltage_lim_string,
                        'Iin '+str(LL)+' to '+ str(UL) + ' A'])
    lim_format = workbook.add_format({'align':'center', 'border': True, 'bold': True,
                                      'font_color': 'black', 'bg_color': '#D3D3D3'})
    worksheet.merge_range(row, col, row, len(data[0])-1, limits_string, lim_format)

def write_voltage_and_current_data(row_start):
    ''' Starting from 3rd row, write in voltage/current data '''
    row = row_start+2
    d_format = workbook.add_format({'align':'center', 'border': True, 'font_color': 'black'})
    for data_line in (data):
        col = 0
        worksheet.write_row(row, col, data_line, d_format)
        row += 1
    return row

def highlight_workbook(wb, ws):
    out_of_spec_format = wb.add_format({'bg_color': 'yellow', 'font_color': 'red'})
    ws.conditional_format('A1:O600', {'type': 'text', 'criteria': 'containing', 'value': 'Out of Spec', 'format': out_of_spec_format})

def write_single_table(row_start, workbook, worksheet, product, test_title, mode, temperature, voltage, LL, UL, data):
    write_mode_temp_header(row_start, wb, ws, color_dict)
    write_limits_header(row_start, limits)
    write_voltage_and_current_data()





def write_excel_analysis_file():
    pass
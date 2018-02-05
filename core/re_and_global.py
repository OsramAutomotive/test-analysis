#!/usr/bin/python3

""" This module contains useful regular expressions and tolerance constants used
by some of the other modules. """

import re

### PLOT COLORS ###
MODULE_COLOR_LIST = ['#00A0A6', '#FFA500', '#DA70D6', '#E5E500',
                     '#FDFD96', '#B22222', '#061715']

SYSTEM_COLOR_LIST = ['brown', '#9932CC', 'maroon', 'red', 'olive',
                     'yellow','green', 'black', 'teal', 'navy',
                     'blue', 'fuchsia', 'magenta', '#e41a1c',
                     '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
                     '#ffff33', '#a65628', '#f781bf', 'burlywood',
                     'chartreuse', 'lime', 'brown', '#9932CC',
                     'maroon', 'red', 'olive', 'yellow', 'green',
                     'black', 'teal', 'navy', 'blue', 'fuchsia',
                     'magenta', '#e41a1c', '#377eb8', '#4daf4a',
                     '#984ea3', '#ff7f00', '#ffff33', '#a65628',
                     '#f781bf', 'burlywood', 'chartreuse', 'lime']

SYSTEM_MARKER_LIST = ['H', ',', 'o','v', '^', '8', 's', '*', '>', '+', 'x', 'D',
                      'H', ',', 'o','v', '^', '8', 's', '*', '>', '+', 'x', 'D',
                      'H', ',', 'o','v', '^', '8', 's', '*', '>', '+', 'x', 'D',
                      'H', ',', 'o','v', '^', '8', 's', '*', '>', '+', 'x', 'D']


### TABLE COLORS ###
TABLE_COLOR_DICT = {'LB':'#FF5C5C', 'HB':'#FCFBE3', 'LBHB':'#7647A2',
                    'DRL':'#ADD8E6', 'PARK':'#FFA500', 'TURN':'#DA70D6',
                    'DRLTURN':'#40E0D0', 'PARKTURN':'#FF8C00',
                    'Stop ECE': '#c39be1', 'Reverse':'#d9d9d9',
                    'Stop SAE':'#9751cb', 'CHMSL':'#de0000',
                    'Turn ECE':'#ff3f3f', 'Fog':'#808080',
                    'Turn SAE':'#702fa1', 'Outage':'#ffff99',
                    'OUTAGE':'#ffff99', 'Diagnostic':'#ffff99',
                    'DIAGNOSTIC': '#ffff99'}

### DATAFRAME COLUMN CONSTANTS ###
VSETPOINT = 'VSetpoint'
ON_OFF = 'ON/OFF'

### REGULAR EXPRESSIONS ###
REGEX_RAW_DATAFILE = '^\d{8}_\d{6}_.*_B_[0-9]*.txt$'
REGEX_TEMPS = '^Temp.*'
REGEX_BOARDS = '(^B[0-9]*)'
REGEX_SYSTEMS = '^B[0-9]*\s(TP[0-9]*:\s.*)'
REGEX_EMPTY_TEST_POSITION = '^B[0-9]*\sTP[0-9]*:\s$'
REGEX_VOLTAGE_SENSES = '^B[0-9]*\s(Vsense\s.*)'

def REGEX_SPECIFIC_BOARD_SYSTEMS(board_id):
    return '^' + re.escape(board_id) + '*\sTP[0-9]*:\s.*'

def REGEX_SPECIFIC_BOARD_VSENSES(board_id):
    return '^' + re.escape(board_id) + '*\sVsense\s.*'

def REGEX_SPECIFIC_BOARD_ON_OFF(board_id):
    return '^' + re.escape(board_id) + '*\sON/OFF$'

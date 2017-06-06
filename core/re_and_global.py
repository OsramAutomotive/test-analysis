#!/usr/bin/python3

''' This module contains useful regular expressions and tolerance global variables used
by some of the other modules. '''

import re

### PLOT COLORS ###
MODULE_COLOR_LIST = ['#00A0A6', '#FFA500', '#DA70D6', '#E5E500', '#FDFD96', '#B22222', '#061715']  
SYSTEM_COLOR_LIST = ['brown', '#9932CC', 'maroon', 'red', 'olive', 'yellow', 
                     'green', 'black', 'teal', 'navy', 'blue', 'fuchsia',
                     'magenta', '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', 
                     '#ffff33', '#a65628', '#f781bf', 'burlywood', 'chartreuse', 'lime']
SYSTEM_MARKER_LIST = ['H', ',', 'o','v', '^', '8', 's', '*', '>', '+', 'x', 'D', 
					  'H', ',', 'o','v', '^', '8', 's', '*', '>', '+', 'x', 'D']

### TABLE COLORS ###
TABLE_COLOR_DICT = { 'LB': '#FF5C5C', 'HB': '#FCFBE3', 'LBHB': '#7647A2', 'DRL': '#ADD8E6', 'PARK': '#FFA500', 
               		 'TURN': '#DA70D6', 'DRLTURN': '#40E0D0', 'PARKTURN': '#FF8C00' }

### DATAFRAME COLUMN CONSTANTS ###
AMB_TEMP = 'Amb Temp TC1'
VSETPOINT = 'VSetpoint'
ON_OFF = 'Board on/off'

### TOLERANCE CONSTANTS ###
TEMPERATURE_TOLERANCE = 5
VOLTAGE_TOLERANCE = 0.5

### REGULAR EXPRESSIONS  ###
REGEX_TEMPS = 'TC.*'
REGEX_SYSTEMS = '^TP[0-9]*:\s\S+'
REGEX_VOLTAGE_SENSES = '^VSense\s[1-2]'

def REGEX_BOARDFILE(board):
    return '^\d{8}_\d{6}_.*_\d{2}_'+board+'.txt$'
def REGEX_BNUMS(bnum):
    return '^TP[0-9]*:\s\S+.*'+bnum.upper()+'$'
def REGEX_TEMPS_BNUMS(bnum):
    return 'TC.*'+bnum.upper()+'$'
def REGEX_VSENSE(bnum):
    return '^VSense\s[1-2]\s'+bnum.upper()+'$'
def REGEX_VSENSE1(bnum):
    return '^VSense\s1\s'+bnum.upper()+'$'

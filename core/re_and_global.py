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
TABLE_COLOR_DICT = { 'LB':'#FF5C5C', 'HB':'#FCFBE3', 'LBHB':'#7647A2', 'DRL':'#ADD8E6', 'PARK':'#FFA500', 
                     'TURN':'#DA70D6', 'DRLTURN':'#40E0D0', 'PARKTURN':'#FF8C00',
                     'Stop ECE': '#c39be1', 'Reverse':'#d9d9d9', 'Stop SAE':'#9751cb',
                     'CHMSL':'#de0000', 'Turn ECE':'#ff3f3f', 'Fog':'#808080', 'Turn SAE':'#702fa1',
                     'Outage':'#ffff99', 'OUTAGE':'#ffff99', 'Diagnostic':'#ffff99', 'DIAGNOSTIC': '#ffff99'}

### DATAFRAME COLUMN CONSTANTS ###
AMB_TEMP = 'Amb Temp TC1'
VSETPOINT = 'VSetpoint'
ON_OFF = 'Board on/off'

### REGULAR EXPRESSIONS  ###
REGEX_RAW_DATAFILE = '^\d{8}_\d{6}_.*_\d{2}_.txt$'
REGEX_TEMPS = 'TC.*'
REGEX_BOARDS = '(^B[0-9]*)'
REGEX_SYSTEMS = '^B[0-9]*\s(TP[0-9]*:\s.*)'
REGEX_VOLTAGE_SENSES = '^B[0-9]*\s(VSense\s[1-2])'


def REGEX_BNUMS(bnum):
    return '^TP[0-9]*:\s\S+.*'+bnum.upper()+'$'
def REGEX_TEMPS_BNUMS(bnum):
    return 'TC.*'+bnum.upper()+'$'
def REGEX_VSENSE(bnum):
    return '^VSense\s[1-2]\s'+bnum.upper()+'$'
def REGEX_VSENSE1(bnum):
    return '^VSense\s1\s'+bnum.upper()+'$'

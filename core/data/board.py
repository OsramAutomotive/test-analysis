#!/usr/bin/python3

import pandas as pd
import numpy as np
import os
import re

from core.data.sample import *
from core.re_and_global import *


## parsing function for datetime index on dataframes
date_parser = lambda x: pd.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p')

class Board(object):
    """
    Holds information and test data collected on a test station board.

    Example highlights::
        test => belongs to a test station object that describes the test
        folder => directory folder of data that was analyzed
        id => 'B3'
        board => board object (includes board id)
        system => list of used test positions and system numbers (used for df query)
        df => dataframe of just this board
    """

    AMB_TEMP = 'Amb Temp TC1'
    VSETPOINT = 'VSetpoint'

    def __init__(self, test, board_number):
        self.test = test
        self.id = ''
        self.folder = test.folder
        self.files = []
        self.df = pd.DataFrame()
        self.systems = []
        self.voltage_senses = []
        self.thermocouples = []
        self.outage = False
        self.module = '(Module name not pulled from limits file)'  # e.g. - 'DRL'
        self.samples = []
        
        self.__set_bnum(board_number)
        self.__set_outage()
        self.__build_dataframe()
        self.__delete_empty_columns()
        self.__scan_for_systems()
        self.__scan_for_voltage_senses()
        self.__scan_for_thermocouples()
        self.__create_samples()

    def __repr__(self):
        return '{}: {} {}'.format(self.__class__.__name__,
                               self.id, self.module)

    def __set_bnum(self, board_number):
        if type(board_number) == int:
            self.id = 'B'+str(board_number)
        elif type(board_number) == str:
            if ('B' in board_number) or ('b' in board_number):
                self.id = board_number.upper()
            else:
                self.id = 'B' + board_number

    def __set_outage(self):
        ''' True/False if board is Outage '''
        self.outage = '6' in self.id

    def __build_dataframe(self):
        ''' Builds all files in folder for board into a single dataframe 
        using the pandas module '''
        print('Building ' + self.id + ' dataframe...')
        for filename in os.listdir(self.folder):
            if bool(re.search(REGEX_BOARDFILE(self.id), filename)):
                try:
                    next_file_df = pd.read_csv( self.folder+'\\'+filename, parse_dates={'Date Time': [0,1]},
                                        date_parser=date_parser, index_col='Date Time', sep='\t',
                                        skipfooter=1, engine='python', usecols=range(22))
                except Exception:
                    print('The following error occurred while attempting to convert the ' \
                          'data files to pandas dataframes:\n\n')
                    raise
                self.files.append(filename)
                self.df = self.df.append(next_file_df)
        try:
            self.df = self.df.replace(['OFF','No Reading'], [0,0])
            self.df = self.df.astype(float)
        except TypeError as e:
            print(e)    
        print('...dataframe complete.')
        
    def __delete_empty_columns(self):
        ''' Deletes emtpy columns in dataframe '''
        for col in self.df.columns.copy():
            if re.search('^TP[0-9]*:\s$', col):
                del self.df[col]
        temps = [self.df.columns[i] for i in range(len(self.df.columns)) if re.search(REGEX_TEMPS, self.df.columns[i])]
        for temp_col in temps.copy():  ## delete temperature columns with no readings
            if self.df[temp_col][0] == 'No Reading':
                del self.df[temp_col]

    def __scan_for_systems(self):
        ''' Scans data for all systems and gets rid of blank test positions '''
        self.systems = [self.df.columns[i] for i in range(len(self.df.columns)) if re.search(REGEX_SYSTEMS, self.df.columns[i])]

    def __scan_for_voltage_senses(self):
        ''' Scans for voltage sense columns '''
        self.voltage_senses = [self.df.columns[i] for i in range(len(self.df.columns)) if re.search(REGEX_VOLTAGE_SENSES, self.df.columns[i])]

    def __scan_for_thermocouples(self):
        ''' Scans for thermocouple columns '''
        possible_thermocouples = [self.df.columns[i] for i in range(len(self.df.columns)) if re.search(REGEX_TEMPS, self.df.columns[i])]
        ## series where index is thermocouples and column is a True/False value depending on whether all items in column are 0
        tc_series = self.df[possible_thermocouples].apply(lambda x: np.all(x==0))
        i = 0
        for tc_all_zero in tc_series:
            if not tc_all_zero:
                self.thermocouples.append(tc_series.index[i]) # append only thermocouples that were used in the test
            i += 1

    def __create_samples(self):
        ''' Creates a sample object for each system on the board '''
        for system in self.systems:
            self.samples.append(Sample(system, self))
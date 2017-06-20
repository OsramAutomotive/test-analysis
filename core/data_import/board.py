#!/usr/bin/python3

import pandas as pd
import numpy as np
import os
import re

from core.data_import.sample import *
from core.re_and_global import *
from core.data_import.helpers import *


## parsing function for datetime index on dataframes
date_parser = lambda x: pd.datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p')

class Board(object):
    """
    Holds information and test data collected on a test station board.

    Example highlights::
        test => belongs to a test station object that describes the test
        folder => directory folder of data that was analyzed
        id => e.g. - 'B3'
        name => e.g. - 'DRL'
        board => board object (includes board id)
        system => list of used test positions and system numbers (used for df query)
        df => dataframe of just this board
    """

    AMB_TEMP = 'Amb Temp TC1'
    VSETPOINT = 'VSetpoint'

    def __init__(self, test, board_number):
        self.test = test
        self.id = ''
        self.name = '(Module name not pulled from limits file)'  # e.g. - 'DRL'
        self.folder = test.folder
        self.files = []
        self.df = pd.DataFrame()
        self.systems = []
        self.voltage_senses = []
        self.thermocouples = []
        self.outage = False
        self.samples = []
        
        self.__set_bnum(board_number)
        self.__get_board_name()
        self.__build_dataframe()
        self.__delete_empty_columns()
        self.__scan_for_systems()
        self.__scan_for_voltage_senses()
        self.__scan_for_thermocouples()
        self.__create_samples()

    def __repr__(self):
        return '{}: {} {}'.format(self.__class__.__name__,
                               self.id, self.name)

    def __set_bnum(self, board_number):
        if type(board_number) == int:
            self.id = 'B'+str(board_number)
        elif type(board_number) == str:
            if ('B' in board_number) or ('b' in board_number):
                self.id = board_number.upper()
            else:
                self.id = 'B' + board_number

    def __build_dataframe(self):
        ''' Builds all files in folder for board into a single dataframe 
        using the pandas module '''
        print('Building ' + self.id + ' dataframe...')
        for filename in os.listdir(self.folder):
            if bool(re.search(REGEX_BOARDFILE(self.id), filename)):
                try:
                    if run_from_ipython():  # if running from ipython (jupyter)
                        next_file_df = pd.read_csv( self.folder+'/'+ filename, 
                                       parse_dates={'Date Time': [0,1]}, date_parser=date_parser, 
                                       index_col='Date Time', sep='\t', engine='python', usecols=range(22))
                    else:  # else running on local machine
                        next_file_df = pd.read_csv( os.path.abspath(os.path.join(os.sep, self.folder, filename)), 
                                       parse_dates={'Date Time': [0,1]}, date_parser=date_parser, 
                                       index_col='Date Time', sep='\t', engine='python', usecols=range(22))
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

    def __get_board_name(self):
        ''' Pull name of board (e.g. 'DRL') from limits file (if provided) '''
        try:
            self.name = self.test.limits.board_module_pairs[self.id]
        except:
            print('Could not load board name')

    def __create_samples(self):
        ''' Creates a sample object for each system on the board '''
        for system in self.systems:
            self.samples.append(Sample(system, self))


class Outage(Board):
    """
    Holds information and test data collected on an outage test station board.

    Example highlights::
        test => belongs to a test station object that describes the test
        folder => directory folder of data that was analyzed
        id => e.g. - 'B3'
        name => e.g. - 'DRL'
        board => board object (includes board id)
        system => list of used test positions and system numbers (used for df query)
        df => dataframe of just this board
    """

    def __init__(self, test, board_number):
        Board.__init__(self, test, board_number)
        self.outage = True
        self.outage_stats = {'ON':{}, 'OFF': {}}

    def get_system_by_system_outage_stats(self, temp, limits=None):
        if self.outage:
            df_on = filter_board_on_or_off(self.df, 1)
            df_off = filter_board_on_or_off(self.df, 0)
            self.get_outage_off_stats(df_off, temp, limits)
            self.get_outage_on_stats(df_on, temp, limits)

    def get_outage_off_stats(self, df_off, temp, limits=None):
        ''' OFF analysis (not voltage based) '''
        self.outage_stats['OFF'][temp] = {}
        for sys in self.systems:
            out_of_spec_bool = 'NA'
            outage_min, outage_max, mean = get_outage_off_stats_single_sys(df_off, self, sys, temp)
            if limits:
                lim_dict = get_limits_for_outage_off(limits, self)
                lower_limit, upper_limit = lim_dict['LL'], lim_dict['UL']
                out_of_spec_bool = check_if_out_of_spec(lower_limit, upper_limit, outage_min, outage_max)
            self.outage_stats['OFF'][temp][sys] = [outage_min, outage_max, mean, out_of_spec_bool]

    def get_outage_on_stats(self, df_on, temp, limits=None):
        ''' ON analysis (voltage based) '''
        self.outage_stats['ON'][temp] = {}
        for voltage in self.test.voltages:
            self.outage_stats['ON'][temp][voltage] = {}
            for sys in self.systems:
                out_of_spec_bool = 'NA'
                outage_min, outage_max, mean = get_outage_on_stats_at_temp_voltage(df_on, self, sys, temp, voltage)
                if limits:
                    lim_dict = get_limits_for_outage_on(limits, self, voltage)
                    lower_limit, upper_limit = lim_dict['LL'], lim_dict['UL']
                    out_of_spec_bool = check_if_out_of_spec(lower_limit, upper_limit, outage_min, outage_max)
                self.outage_stats['ON'][temp][voltage][sys] = [outage_min, outage_max, mean, out_of_spec_bool]


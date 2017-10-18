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

    AMB_TEMP = 'Temp TC1'
    VSETPOINT = 'VSetpoint'

    def __init__(self, test, board_number):
        self.test = test
        self.id = ''
        self.name = None  # e.g. - 'DRL'
        self.folder = test.folder
        self.files = []
        self.df = pd.DataFrame()
        self.systems = []
        self.voltage_senses = []
        self.thermocouples = []
        self.outage = False
        self.samples = []
        
        self.__set_id(board_number)
        self.__get_board_name()


    def __repr__(self):
        return '{}: {} {}'.format(self.__class__.__name__,
                                  self.id, self.name)

    def __set_id(self, board_number):
        if type(board_number) == int:
            self.id = 'B'+str(board_number)
        elif type(board_number) == str:
            if ('B' in board_number) or ('b' in board_number):
                self.id = board_number.upper()
            else:
                self.id = 'B' + board_number

    def __get_board_name(self):
        ''' Pull name of board (e.g. 'DRL') from limits file (if provided) '''
        try:
            self.name = self.test.limits.board_module_pairs[self.id]
        except:
            print('Could not load board name for', self.id)


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


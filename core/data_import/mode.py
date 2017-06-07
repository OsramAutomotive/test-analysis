#!/usr/bin/python3

import pandas as pd
import re

from core.data_import.helpers import *
from core.re_and_global import *


class Mode(object):
    """
    Holds information and test data collected for modes (board combos) excited in test.

    Example highlights::
        test => belongs to a test station object that describes the test
        board_mode => boards that are ON in this mode (e.g. - 'B3B4')
        temps => temperatures at which test data is analyzed
        systems => test system headers with mode_tag appended to each (for query on test mdf)
        hist_dict => temp key, voltage key, then currents df queried with that temp/voltage combo
        df => dataframe of only data when this mode is in operation
    """
    AMB_TEMP = 'Amb Temp TC1'
    VSETPOINT = 'VSetpoint'

    def __init__(self, test, board_mode, df, voltages, *temps):
        self.test = test
        self.board_mode = board_mode
        self.mode_tag = board_mode.replace('B6', '') # outage removed
        self.name = self.board_mode # actual name of mode (e.g. - 'DRLTURN')
        self.temps = temps
        self.voltages = voltages
        self.board_ids = re.findall('..', board_mode) # split string every 2 chars
        self.current_board_ids = copy_and_remove_b6_from(self.board_ids)
        self.systems = [' '.join([sys, self.mode_tag]) for sys in test.systems]
        self.hist_dict = {}  # temp -> voltage -> df of currents only at that temp/voltage combo
        self.multimode = False  # placeholder -> scans later to check if multimode or not
        self.df = pd.DataFrame() # dataframe of mode currents (added together if multi-mode)
        self.voltage_senses = [] # holds voltage sense positions for boards on in mode
        self.vsense_stats = {} # basic stats of vsenses
        self.current_stats = {} # basic stats of currents
        self.out_of_spec = pd.DataFrame()
        self.has_led_binning = False
        self.led_bins = []

        self.__scan_for_multimode()
        self.__make_hist_dict()
        self.__populate_hist_dict(df)
        self.__scan_for_voltage_senses()
        self.__get_mode_name_and_set_binning()

    def __repr__(self):
        return '{}: {} ({})'.format(self.__class__.__name__,
                               self.name, self.board_mode)

    def __scan_for_multimode(self):
        if len(self.current_board_ids) > 1:
            self.multimode = True     

    def __make_hist_dict(self):
        for temp in self.temps:
            self.hist_dict[temp] = dict.fromkeys(self.voltages)

    def __populate_hist_dict(self, df):    
        for temp in self.temps:
            for voltage in self.voltages:
                self.df = self.create_multimode_cols(df)
                dframe = filter_temp_and_voltage(self.df, temp, voltage)
                if not dframe.empty:
                    self.hist_dict[temp][voltage] = dframe
                else:
                    self.hist_dict[temp].pop(voltage, None)
            if not self.hist_dict[temp]:
                self.hist_dict.pop(temp, None)

    def __scan_for_voltage_senses(self):
        ''' Scans for voltage sense columns '''
        self.voltage_senses = [vsense+' '+board for board in self.current_board_ids for vsense in self.test.voltage_senses]

    def __get_mode_name_and_set_binning(self):
        ''' Pull name of mode from limits file (if provided) '''
        if self.test.limits:
            self.name = self.mode_tag
            for board in self.current_board_ids:
                self.name = self.name.replace(board, self.test.limits.board_module_pairs[board])
                if board in self.test.limits.led_binning_dict:
                    self.has_led_binning = True
                    self.led_bins = self.test.limits.led_binning_dict[board]

    def create_multimode_cols(self, dframe):
        ''' Adds multimode current column for each system '''
        if self.multimode:  # if mode is a multimode (multiple current boards ON)
            for sys in self.test.systems: # for each system (without appended board/mode tag label)
                sys_col_label = sys + ' ' + self.mode_tag 
                dframe[sys_col_label] = 0.0  # create multimode col of float zeroes
                for b in self.current_board_ids: # add each ON current board
                    dframe[sys_col_label] = dframe[sys_col_label] + pd.to_numeric(dframe[sys+' '+b], downcast='float')
        return dframe

    def strip_index_and_melt_to_series(self, dframe):
        hist_dframe = pd.melt(dframe, value_vars=self.systems, value_name='currents')
        hist_dframe = pd.to_numeric(hist_dframe['currents'], downcast='float')
        return hist_dframe

    def get_system_by_system_mode_stats(self, temp, limits=None):
        ''' Get voltage/current statistics and limit analysis for this mode '''
        self.current_stats[temp] = {}
        self.vsense_stats[temp] = {}
        for voltage in self.voltages:
            self.current_stats[temp][voltage] = {}
            self.vsense_stats[temp][voltage] = {}

            ## voltage analysis
            for vsense in self.voltage_senses:
                vsense_min, vsense_max, mean = get_vsense_stats_at_mode_temp_voltage(vsense, self, temp, voltage)
                out_of_spec_bool = check_if_out_of_spec(voltage-VOLTAGE_TOLERANCE, voltage+VOLTAGE_TOLERANCE, vsense_min, vsense_max)
                self.vsense_stats[temp][voltage][vsense] = [vsense_min, vsense_max, mean, out_of_spec_bool]

            ## current analysis
            for system in self.systems:
                out_of_spec = None
                sys_min, sys_max, mean, std = get_system_stats_at_mode_temp_voltage(system, self, temp, voltage)
                if limits:
                    if self.has_led_binning:
                        mode_limit_dict = get_limits_for_system_with_binning(limits, self, temp, voltage, system)
                    else:
                        mode_limit_dict = get_limits_at_mode_temp_voltage(limits, self, temp, voltage)
                    lower_limit, upper_limit = mode_limit_dict['LL'], mode_limit_dict['UL']
                    out_of_spec_bool = check_if_out_of_spec(lower_limit, upper_limit, sys_min, sys_max)
                self.current_stats[temp][voltage][system] = [sys_min, sys_max, mean, std, out_of_spec_bool]

    def get_out_of_spec_data(self):
        ''' Method for retrieving out_of_spec data from test in this mode '''
        for temp in self.temps:
            for voltage in self.voltages:
                df, out_of_spec_df = pd.DataFrame(), pd.DataFrame()
                df = filter_temp_and_voltage(self.df, temp, voltage)
                mode_limit_dict = get_limits_at_mode_temp_voltage(self.test.limits, self, temp, voltage)
                
                if self.has_led_binning:
                    pass ### TO DO: Make this work for LED binning
                else:
                    lower_limit, upper_limit = mode_limit_dict['LL'] , mode_limit_dict['UL']
                    ## select all rows where any system has out of spec currents
                    out_of_spec_df = df.loc[ (df[self.systems].values<lower_limit).any(1) | (df[self.systems].values>upper_limit).any(1) ]
                    if not out_of_spec_df.empty:  ## if out_of_spec df is not empty
                        write_out_of_spec_to_file(df, self, temp, voltage)
#!/usr/bin/python3

import pandas as pd
import re

from core.data.helper import *
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
        self.temps = temps
        self.voltages = voltages
        self.board_ids = re.findall('..', board_mode) # split string every 2 chars
        self.current_board_ids = copy_and_remove_b6_from(self.board_ids)
        self.systems = [' '.join([sys, self.mode_tag]) for sys in test.systems]
        self.hist_dict = {}  # temp -> voltage -> df of currents only at that temp/voltage combo
        self.multimode = False  # placeholder -> scans later to see if multimode or not
        self.df = pd.DataFrame() # dataframe of mode currents (added together if multi-mode)
        
        self.__scan_for_multimode()
        self.__make_hist_dict()
        self.__populate_hist_dict(df)

    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__,
                               self.board_mode)

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
                dframe = self.filter_temp_and_voltage(self.df, temp, voltage)
                dframe_for_hist = self.strip_index(dframe)
                self.hist_dict[temp][voltage] = dframe_for_hist

    def filter_temp_and_voltage(self, df, temp, voltage):
        dframe = df.loc[(df[self.VSETPOINT] == voltage) &
                        (df[self.AMB_TEMP] > (temp-TEMPERATURE_TOLERANCE)) &
                        (df[self.AMB_TEMP] < (temp+TEMPERATURE_TOLERANCE))]
        return dframe

    def create_multimode_cols(self, dframe):
        ''' NEED TO FIX: returned dframe is not holding multimode added current columns  '''
        if self.multimode:  # if mode is a multimode (multiple current boards ON)
            for sys in self.test.systems: # for each system (without appended board/mode tag label)
                sys_col_label = sys + ' ' + self.mode_tag 
                dframe[sys_col_label] = 0.0  # create multimode col of float zeroes
                for b in self.current_board_ids: # add each ON current board
                    dframe[sys_col_label] = dframe[sys_col_label] + pd.to_numeric(dframe[sys+' '+b], downcast='float')
        return dframe

    def strip_index(self, dframe):
        hist_dframe = pd.melt(dframe, value_vars=self.systems, value_name='currents')
        hist_dframe = pd.to_numeric(hist_dframe['currents'], downcast='float')
        return hist_dframe

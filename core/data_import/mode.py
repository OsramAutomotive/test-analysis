#!/usr/bin/python3

import pandas as pd
import re
from lxml import etree

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
    VSETPOINT = 'VSetpoint'

    def __init__(self, test, board_mode, df, voltages, *temps):
        self.test = test
        self.board_mode = board_mode
        self.mode_tag = board_mode.replace('B6', '') # outage removed
        self.name = self.board_mode # actual name of mode (e.g. - 'DRLTURN')
        self.temps = temps
        self.voltages = voltages
        self.board_ids = re.findall('B[]0-9]*', board_mode) # find boards present in mode
        self.current_board_ids = copy_and_remove_b6_from(self.board_ids)
        self.boards = [board for board in self.test.boards if board.id in self.current_board_ids]
        self.systems = []

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
        self.__set_systems()
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

    def __set_systems(self):
        ## create systems laber if MM else use only board's systems
        if self.multimode:
            ## same system/SN labels
            if self.boards[0].systems[0].split(' ', 1)[1] == self.boards[1].systems[0].split(' ', 1)[1]:
                self.systems = [ self.mode_tag + ' ' + self.boards[0].systems[i].split(' ', 1)[1] 
                                 for i in range(0, len(self.boards[0].systems)) ]
            else: ## unique system/SN labels
                self.systems = [ self.mode_tag + ' ' + self.boards[0].systems[i].split(' ')[1] 
                                 + ' MM' + str(i+1) for i in range(0, len(self.boards[0].systems)) ]
        else:
            self.systems = self.boards[0].systems

    def __make_hist_dict(self):
        for temp in self.temps:
            self.hist_dict[temp] = dict.fromkeys(self.voltages)

    def __populate_hist_dict(self, df):
        for temp in self.temps:
            for voltage in self.voltages:
                self.df = self.create_multimode_cols(df)
                dframe = filter_temp_and_voltage(self.df, self.test.ambient, temp, 
                                                 voltage, self.test.temperature_tolerance)
                if not dframe.empty:
                    self.hist_dict[temp][voltage] = dframe
                else:
                    self.hist_dict[temp].pop(voltage, None)
            if not self.hist_dict[temp]:
                self.hist_dict.pop(temp, None)

    def __scan_for_voltage_senses(self):
        ''' Scans for voltage sense columns '''
        self.voltage_senses = [vsense for board in self.current_board_ids for vsense in self.test.voltage_senses if board in vsense]

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
            # for sys in self.test.systems: # for each system (without appended board/mode tag label)
            #     sys_col_label = self.mode_tag + ' ' + sys 
            #     dframe[sys_col_label] = 0.0  # create multimode col of float zeroes
            #     for b in self.current_board_ids: # add each ON current board
            #         dframe[sys_col_label] = dframe[sys_col_label] + pd.to_numeric(dframe[b + ' ' + sys], downcast='float')
            for i, sys in enumerate(self.systems):
                dframe[sys] = 0.0  # create multimode col of float zeroes
                for board in self.boards: # add each ON current board
                    dframe[sys] = dframe[sys] + pd.to_numeric(dframe[board.systems[i]], downcast='float')
        return dframe

    def strip_index_and_melt_to_series(self, dframe):
        hist_dframe = pd.melt(dframe, value_vars=self.systems, value_name='currents')
        hist_dframe = pd.to_numeric(hist_dframe['currents'], downcast='float')
        return hist_dframe

    def strip_index_and_melt_to_series_for_binning(self, dframe, led_bin):
        systems = [system for system in self.systems if led_bin in system]
        hist_dframe = pd.melt(dframe, value_vars=systems, value_name='currents')
        hist_dframe = pd.to_numeric(hist_dframe['currents'], downcast='float')
        return hist_dframe

    def get_system_by_system_mode_stats(self, xml_temp, temp, run_limit_analysis=False, limits=None):
        ''' Get voltage/current statistics and limit analysis for this mode '''
        xml_header_width = str(len(self.voltage_senses)+len(self.systems)+1)
        xml_mode = etree.SubElement(xml_temp, "mode", id=self.name, width=xml_header_width)
        self.current_stats[temp] = {}
        self.vsense_stats[temp] = {}
        
        for voltage in self.voltages:
            xml_voltage = etree.SubElement(xml_mode, "voltage", value=str(voltage)+'V', width=xml_header_width)
            if run_limit_analysis and limits:
                xml_limits = etree.SubElement(xml_voltage, "limits", width=xml_header_width)
                min_current = limits.lim[self.name][temp][voltage][0]
                max_current = limits.lim[self.name][temp][voltage][1]
                xml_limits.text = 'Limits:  ' + str(min_current)+'A to '+str(max_current)+'A' 

            self.current_stats[temp][voltage] = {}
            self.vsense_stats[temp][voltage] = {}

            ## vsense analysis
            xml_vsenses = etree.SubElement(xml_voltage, "vsenses")
            for vsense in self.voltage_senses:
                xml_vsense = etree.SubElement(xml_vsenses, "vsense")
                vsense_min, vsense_max, vsense_mean = get_vsense_stats_at_mode_temp_voltage(vsense, self, temp, voltage)
                out_of_spec_bool = check_if_out_of_spec(voltage-self.test.voltage_tolerance, 
                                                        voltage+self.test.voltage_tolerance, 
                                                        vsense_min, vsense_max)
                self.vsense_stats[temp][voltage][vsense] = [vsense_min, vsense_max, vsense_mean, out_of_spec_bool]
                xml_name = etree.SubElement(xml_vsense, "name")
                xml_name.text = str(vsense).rsplit(' ', 1)[0]
                xml_min = etree.SubElement(xml_vsense, "min")
                xml_min.text = str(vsense_min)
                xml_max = etree.SubElement(xml_vsense, "max")
                xml_max.text = str(vsense_max)
                xml_mean = etree.SubElement(xml_vsense, "mean")
                xml_mean.text = str(vsense_mean)
                xml_check = etree.SubElement(xml_vsense, "check")
                xml_check.text = 'Out of Spec' if out_of_spec_bool else 'G'

            ## current analysis
            xml_systems = etree.SubElement(xml_voltage, "systems")
            for system in self.systems:
                xml_system = etree.SubElement(xml_systems, "system")
                out_of_spec_bool = 'NA'
                out_of_spec_count = 'NA'
                sys_min, sys_max, sys_mean, sys_std = get_system_stats_at_mode_temp_voltage(system, self, temp, voltage)
                if limits:
                    if self.has_led_binning:
                        mode_limit_dict = get_limits_for_system_with_binning(limits, self, temp, voltage, system)
                    else:
                        mode_limit_dict = get_limits_at_mode_temp_voltage(limits, self, temp, voltage)
                    lower_limit, upper_limit = mode_limit_dict['LL'], mode_limit_dict['UL']
                    out_of_spec_bool = check_if_out_of_spec(lower_limit, upper_limit, sys_min, sys_max)
                    out_of_spec_count, percent_out = count_num_out_of_spec(self.hist_dict[temp][voltage][system], lower_limit, upper_limit)
                self.current_stats[temp][voltage][system] = [sys_min, sys_max, sys_mean, sys_std, out_of_spec_bool]
                xml_name = etree.SubElement(xml_system, "name")
                xml_name.text = str(system)
                xml_min = etree.SubElement(xml_system, "min")
                xml_min.text = str(sys_min)
                xml_max = etree.SubElement(xml_system, "max")
                xml_max.text = str(sys_max)
                xml_mean = etree.SubElement(xml_system, "mean")
                xml_mean.text = str(sys_mean)
                xml_std = etree.SubElement(xml_system, "std")
                xml_std.text = str(sys_std)
                xml_check = etree.SubElement(xml_system, "check")
                xml_check.text = 'NA' if (not run_limit_analysis or not limits) else 'Out of Spec' if out_of_spec_bool else 'G'
                xml_count = etree.SubElement(xml_system, "count")
                xml_count.text = str(out_of_spec_count)
                xml_percent_out = etree.SubElement(xml_system, "percent-out")
                xml_percent_out.text = str(percent_out)

    def get_out_of_spec_data(self):
        ''' Method for retrieving out_of_spec raw data from test in this mode '''
        for temp in self.temps:
            for voltage in self.voltages:
                df, out_of_spec_df = pd.DataFrame(), pd.DataFrame()
                df = filter_temp_and_voltage(self.df, self.test.ambient, temp, voltage, self.test.temperature_tolerance)
                mode_limit_dict = get_limits_at_mode_temp_voltage(self.test.limits, self, temp, voltage)
                
                if self.has_led_binning:
                    pass ### TO DO: Make this work for LED binning
                else:
                    lower_limit, upper_limit = mode_limit_dict['LL'] , mode_limit_dict['UL']
                    ## select all rows where any system has out of spec currents
                    out_of_spec_df = df.loc[ (df[self.systems].values<lower_limit).any(1) | (df[self.systems].values>upper_limit).any(1) ]
                    if not out_of_spec_df.empty:  ## if out_of_spec df is not empty
                        write_out_of_spec_to_file(df, self, temp, voltage)
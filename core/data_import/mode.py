#!/usr/bin/python3

"""
This module contains the Mode class which models a mode excited in a lighting
project. For eaxample, "DRL" or "Park" or "Park+Turn" could be modes.
"""

import re
import pandas as pd
from lxml import etree

from core.data_import.helpers import copy_and_remove_b6_from, \
                                     filter_temp_and_voltage, \
                                     get_system_stats_at_mode_temp_voltage, \
                                     check_if_out_of_spec, \
                                     count_num_out_of_spec, \
                                     get_vsense_stats_at_mode_temp_voltage, \
                                     write_out_of_spec_to_file

from core.data_import.rotating_file import RotatingFile

from core.limits_import.limits import get_limits_for_system_with_binning, \
                                      get_limits_at_mode_temp_voltage


class Mode(object):
    """
    Holds information and test data collected for modes (board combos) excited in test.

    Attributes: 
        test => belongs to a test station object that describes the test
        board_mode => boards that are ON in this mode (e.g. - 'B3B4')
        temps => temperatures at which test data is analyzed
        systems => test system headers with mode_tag appended to each (for query on test mdf)
        hist_dict => temp key, voltage key, then currents df queried with that temp/voltage combo
        df => dataframe of only data when this mode is in operation

    Essential methods:

    """
    VSETPOINT = 'Vsetpoint'

    def __init__(self, test, board_mode, df, voltages, *temps):
        self.test = test
        self.board_mode = board_mode # board id(s) (e.g. - 'B3B4')
        self.name = self.board_mode # name of mode (e.g. - 'DRLTURN'), to be pulled from limits
        self.temps = temps
        self.voltages = voltages
        self.current_board_ids = re.findall('B[]0-9]*', board_mode) # find boards present in mode
        self.boards = [board for board in self.test.boards if board.id in self.current_board_ids]
        self.systems = []
        self.hist_dict = {}  # temp -> voltage -> df of currents only at that temp/voltage combo
        self.multimode = False  # placeholder -> scans later to check if multimode or not
        self.df = pd.DataFrame() # dataframe of mode currents (added together if multi-mode)
        self.voltage_senses = [] # holds voltage sense positions for boards on in mode
        self.out_of_spec = pd.DataFrame()
        self.has_led_binning = False
        self.led_bins = []

        self.__scan_for_multimode()
        self.__set_systems()
        self.__create_hist_dict(df)
        self.__scan_for_voltage_senses()
        self.__get_mode_name_and_set_binning()

    def __repr__(self):
        return '{}: {} ({})'.format(self.__class__.__name__,
                                    self.name, self.board_mode)

    def __scan_for_multimode(self):
        """ Check if mode is multimode (current sharing with multiple modules) """
        if len(self.current_board_ids) > 1:
            self.multimode = True

    def __set_systems(self):
        """ Create systems label if multimode else use only board's systems """
        if self.multimode:
            # same system/SN labels
            if self.boards[0].systems[0].split(' ', 1)[1] == self.boards[1].systems[0].split(' ', 1)[1]:
                self.systems = [self.board_mode + ' ' + self.boards[0].systems[i].split(' ', 1)[1]
                                for i in range(0, len(self.boards[0].systems))]
            else: # unique system/SN labels
                self.systems = [self.board_mode + ' ' + self.boards[0].systems[i].split(' ')[1]
                                + ' MM' + str(i+1) for i in range(0, len(self.boards[0].systems))]
        else:
            self.systems = self.boards[0].systems

    def __create_hist_dict(self, df):
        """ Creates histogram dictionary, which holds a series for each
            system's currents at each temperature/voltage condition """
        for temp in self.temps:
            self.hist_dict[temp] = dict.fromkeys(self.voltages)
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
        """ Scans for voltage sense columns for boards in mode """
        for board in self.current_board_ids:
            for vsense in self.test.voltage_senses:
                if board in vsense:
                    self.voltage_senses.append(vsense)

    def __get_mode_name_and_set_binning(self):
        """ Pull name of mode from limits file (if provided) """
        if self.test.limits:
            for board in self.current_board_ids:
                self.name = self.name.replace(board,
                                              self.test.limits.board_module_pairs[board])
                if board in self.test.limits.led_binning_dict:
                    self.has_led_binning = True
                    self.led_bins = self.test.limits.led_binning_dict[board]

    def create_multimode_cols(self, dframe):
        """ If multimode, a multimode current column is computed and added to dframe for each system """
        if self.multimode:  # if mode is a multimode (multiple current boards ON)
            for i, sys in enumerate(self.systems):
                dframe[sys] = 0.0  # create multimode col of float zeroes
                for board in self.boards: # add each ON current board
                    dframe[sys] = dframe[sys] + pd.to_numeric(dframe[board.systems[i]], downcast='float')
        return dframe

    def strip_index_and_melt_to_series(self, dframe):
        """ Collect system currents into single pool for histogram analysis """
        hist_dframe = pd.melt(dframe, value_vars=self.systems, value_name='currents')
        hist_dframe = pd.to_numeric(hist_dframe['currents'], downcast='float')
        return hist_dframe

    def strip_index_and_melt_to_series_for_binning(self, dframe, led_bin):
        """ Collect like led bin sys currents into slingle pool for histogram analysis """
        systems = [system for system in self.systems if led_bin in system]
        hist_dframe = pd.melt(dframe, value_vars=systems, value_name='currents')
        hist_dframe = pd.to_numeric(hist_dframe['currents'], downcast='float')
        return hist_dframe

    def get_system_by_system_mode_stats(self, xml_temp, temp, run_limit_analysis=False, limits=None):
        """ Get voltage/current statistics and limit analysis for this mode
        Args:
            xml_temp (xml obj): part of tables xml file to write stats to
            temp (int): temperature at which to analyze
            run_limit_analysis (boolean): T/F user entry on whether to run limit analysis
            limits (Limits obj): input limits for test samples (currents and perhaps outage)
        Returns:
            None
        """
        if (temp in self.hist_dict): # data exists at this temperature
            xml_header_width = str(len(self.voltage_senses)+len(self.systems)+1)
            xml_mode = etree.SubElement(xml_temp, "mode", id=self.name, width=xml_header_width)
            for voltage in self.voltages:
                xml_voltage = etree.SubElement(xml_mode, "voltage", value=str(voltage)+'V', width=xml_header_width)
                if run_limit_analysis and limits:
                    xml_limits = etree.SubElement(xml_voltage, "limits", width=xml_header_width)
                    min_current = limits.lim[self.name][temp][voltage][0]
                    max_current = limits.lim[self.name][temp][voltage][1]
                    xml_limits.text = 'Limits:  ' + str(min_current)+'A to '+str(max_current)+'A'
                # vsense analysis
                xml_vsenses = etree.SubElement(xml_voltage, "vsenses")
                for vsense in self.voltage_senses:
                    self.run_vsense_analysis(temp, voltage, vsense, xml_vsenses)
                # current analysis
                xml_systems = etree.SubElement(xml_voltage, "systems")
                for system in self.systems:
                    self.run_current_analysis(temp, voltage, system, xml_systems, limits, run_limit_analysis)
        else:  # data does not exist at this temperature
            print('\tData does not exist for', self.name, 'at', temp, 'C.')

    def run_vsense_analysis(self, temp, voltage, vsense, xml_vsenses):
        """ Run voltage sensing analysis for each temp/voltage/system condition in this mode.
            Builds an xml table displaying basic results and statistics.
        Args:
            temp (int): temperature at which to analyze
            voltage (float): voltage at which to analyze
            vsense (string): dataframe column header of mode vsense
            xml_vsenses (xml object): part of tables file to write vsense stats to
        Returns:
            None
        """
        if (temp in self.hist_dict):
            xml_vsense = etree.SubElement(xml_vsenses, "vsense")
            vsense_min, vsense_max, vsense_mean, vsense_std = get_vsense_stats_at_mode_temp_voltage(
                                                                        vsense, self, temp, voltage)
            out_of_spec_bool = check_if_out_of_spec(voltage - self.test.voltage_tolerance,
                                                    voltage + self.test.voltage_tolerance,
                                                    vsense_min, vsense_max)
            vsense_series = filter_temp_and_voltage(self.df, self.test.ambient, temp, voltage,
                                                    self.test.temperature_tolerance)[vsense]
            total_count, out_of_spec_count, percent_out = count_num_out_of_spec(
                 vsense_series, voltage-self.test.voltage_tolerance, voltage+self.test.voltage_tolerance)
            xml_name = etree.SubElement(xml_vsense, "name")
            xml_name.text = str(vsense)
            xml_min = etree.SubElement(xml_vsense, "min")
            xml_min.text = str(vsense_min)
            xml_max = etree.SubElement(xml_vsense, "max")
            xml_max.text = str(vsense_max)
            xml_mean = etree.SubElement(xml_vsense, "mean")
            xml_mean.text = str(vsense_mean)
            xml_mean = etree.SubElement(xml_vsense, "std")
            xml_mean.text = str(vsense_std)
            xml_count = etree.SubElement(xml_vsense, "count")
            xml_count.text = str(total_count)
            xml_count = etree.SubElement(xml_vsense, "count-out")
            xml_count.text = str(out_of_spec_count)
            xml_percent_out = etree.SubElement(xml_vsense, "percent-out")
            xml_percent_out.text = str(percent_out)
            xml_check = etree.SubElement(xml_vsense, "check")
            xml_check.text = 'Out of Spec' if out_of_spec_bool else 'G'

    def run_current_analysis(self, temp, voltage, system, xml_systems, limits, run_limit_analysis):
        """ Run current analysis for each temp/voltage/system condition in this mode. Builds
            an xml table displaying basic results and statistics.
        Args:
            temp (int): temperature at which to analyze
            voltage (float):  
            system (string): dataframe column header of system in this mode
            xml_systems (xml object): part of tables file to write system stats to
            limits (Limits object): input limits for test samples (currents and perhaps outage)
            run_limit_analysis (boolean): T/F user entry on whether to run limit analysis
        Returns:
            None
        """
        xml_system = etree.SubElement(xml_systems, "system")
        out_of_spec_bool = 'NA'
        out_of_spec_count = 'NA'
        sys_min, sys_max, sys_mean, sys_std = get_system_stats_at_mode_temp_voltage(
            system, self, temp, voltage)
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
        xml_count = etree.SubElement(xml_system, "count")
        xml_count.text = "0"
        if (temp in self.hist_dict) and (voltage in self.hist_dict[temp]):
            xml_count.text = str(self.hist_dict[temp][voltage][system].count())
            if limits and run_limit_analysis:
                out_of_spec_bool= self.run_current_limit_analysis(temp, voltage, system, xml_system, 
                                                                  limits, sys_min, sys_max)
            if self.multimode:
                self.run_multimode_ratio_analysis(temp, voltage, system, xml_system)
        xml_check = etree.SubElement(xml_system, "check")
        xml_check.text = 'NA' if (not run_limit_analysis or not limits) \
                         else 'Out of Spec' if out_of_spec_bool else 'G'

    def run_current_limit_analysis(self, temp, voltage, system, xml_system, limits, sys_min, sys_max):
        """ Conducts limit analysis of current with input limits file. 
            Limit row denoting 'G' or 'Out of Spec' added to xml tables output. """
        if self.has_led_binning:
            mode_limit_dict = get_limits_for_system_with_binning(
                                  limits, self, temp, voltage, system)
        else:
            mode_limit_dict = get_limits_at_mode_temp_voltage(
                                  limits, self, temp, voltage)
        lower_limit, upper_limit = mode_limit_dict['LL'], mode_limit_dict['UL']
        out_of_spec_bool = check_if_out_of_spec(lower_limit, upper_limit, 
                                                sys_min, sys_max)
        total_count, out_of_spec_count, percent_out = count_num_out_of_spec(
                    self.hist_dict[temp][voltage][system], lower_limit, upper_limit)
        xml_count_out = etree.SubElement(xml_system, "count-out")
        xml_count_out.text = str(out_of_spec_count)
        xml_percent_out = etree.SubElement(xml_system, "percent-out")
        xml_percent_out.text = str(percent_out)
        return out_of_spec_bool

    def run_multimode_ratio_analysis(self, temp, voltage, system, xml_system):
        """ Conducts multimode ratio analysis. For example the amount of current 
            drawn by DRL and TURN in DRL+TURN mode. Rows added to xml tables output. """
        dframe = filter_temp_and_voltage(self.df, self.test.ambient, temp, voltage, 
                                         self.test.temperature_tolerance)
        for i, board_id in enumerate(self.current_board_ids):
            field = system.replace(self.board_mode, board_id)
            series = dframe[field]
            try: # retrieve board name from limits
                board_name = self.test.limits.board_module_pairs[board_id]
            except:
                board_name = board_id
            xml_board_min = etree.SubElement(xml_system, "board_min"+str(i+1), id=board_name)
            xml_board_max = etree.SubElement(xml_system, "board_max"+str(i+1), id=board_name)
            xml_board_min.text = str(series.min())
            xml_board_max.text = str(series.max())

    def get_out_of_spec_data(self):
        """ Retrieves out_of_spec raw data from test in this mode. """
        out_of_spec_file = RotatingFile(directory='!output//', 
                                        filename=self.test.name+' - out of spec')
        for temp in self.temps:
            for voltage in self.voltages:
                df, out_of_spec_df = pd.DataFrame(), pd.DataFrame()
                df = filter_temp_and_voltage(self.df, self.test.ambient, temp, voltage, 
                                             self.test.temperature_tolerance)
                mode_limit_dict = get_limits_at_mode_temp_voltage(self.test.limits, 
                                                                  self, temp, voltage)
                if self.has_led_binning:
                    # TODO: Make this work for LED binning
                    raise NotImplementedError
                else:
                    # select all rows where any Vsense has out of spec voltages
                    lower_limit, upper_limit = voltage - self.test.voltage_tolerance , voltage + self.test.voltage_tolerance
                    out_of_spec_df = df.loc[ (df[self.voltage_senses].values<lower_limit).any(1) | (df[self.voltage_senses].values>upper_limit).any(1) ]
                    # add them to the out of spec file
                    if not out_of_spec_df.empty:
                        analysis_type = 'Out of spec data rows - Vin'
                        out_of_spec_df = out_of_spec_df[~out_of_spec_df.index.duplicated(keep='first')]  # remove duplicates
                        write_out_of_spec_to_file(out_of_spec_file, out_of_spec_df, self, temp, voltage, analysis_type)

                    # select all rows where any system has out of spec currents
                    lower_limit, upper_limit = mode_limit_dict['LL'] , mode_limit_dict['UL']
                    out_of_spec_df = df.loc[ (df[self.systems].values<lower_limit).any(1) | (df[self.systems].values>upper_limit).any(1) ]
                    # add them to the out of spec file
                    if not out_of_spec_df.empty:
                        analysis_type = 'Out of spec data rows - Iin'
                        out_of_spec_df = out_of_spec_df[~out_of_spec_df.index.duplicated(keep='first')]  # remove duplicates
                        write_out_of_spec_to_file(out_of_spec_file, out_of_spec_df, self, temp, voltage, analysis_type)

        try:
            out_of_spec_file.close()
        except:
            print('File already closed')

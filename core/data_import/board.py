#!/usr/bin/python3

import pandas as pd
import numpy as np
import os
import re
from lxml import etree

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
        self.systems = []
        self.outage = False
        
        self.__set_id(board_number)
        self.__get_board_name()
        self.__get_board_systems()

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
            self.name = self.id
            print('Could not load board name for', self.id)

    def __get_board_systems(self):
        set_of_systems = set()
        for system in [re.search(REGEX_SPECIFIC_BOARD_SYSTEMS(self.id), column).group(0) for column in self.test.df.columns if re.search(REGEX_SPECIFIC_BOARD_SYSTEMS(self.id), column)]:
            set_of_systems.add(system)
        self.systems = sorted(list(set_of_systems), key=lambda sys: get_system_test_position_int(sys, index=1))


class Outage(Board):
    """
    Holds information and test data collected on an outage test station board.

    Example highlights::
        test => belongs to a test station object that describes the test
        folder => directory folder of data that was analyzed
        id => e.g. - 'B3'
        name => e.g. - 'Outage' or 'Diagnostic'
        board => board object (includes board id)
        system => list of used test positions and system numbers (used for df query)
        df => dataframe of just this board
    """

    def __init__(self, test, board_number):
        Board.__init__(self, test, board_number)
        self.outage = True
        self.outage_stats = {'ON':{}, 'OFF': {}}
        self.systems = [column for column in self.test.df.columns if re.search(REGEX_SPECIFIC_BOARD_SYSTEMS(self.id), column)]
        self.board_on_off = [column for column in self.test.df.columns if re.search(REGEX_SPECIFIC_BOARD_ON_OFF(self.id), column)]
        self.xml_header_width = str(len(self.systems)+1)

    def get_system_by_system_outage_stats(self, xml_temp, temp, run_limit_analysis, limits):        
        xml_outages = etree.SubElement(xml_temp, "outages", id=self.name, width=self.xml_header_width)
        
        df = self.test.df[ [self.test.VSETPOINT] + self.test.thermocouples + self.board_on_off + self.systems ]
        df_on = filter_board_on_or_off(df, self.id, 1)
        df_off = filter_board_on_or_off(df, self.id, 0)
        self.get_outage_stats_in_state(df_off, xml_outages, temp, run_limit_analysis, limits, outage_state='OFF')
        self.get_outage_stats_in_state(df_on, xml_outages, temp, run_limit_analysis, limits, outage_state='ON')

    def get_outage_stats_in_state(self, df, xml_outages, temp, run_limit_analysis, limits, outage_state):
        ''' OFF analysis '''
        xml_outage = etree.SubElement(xml_outages, "outage", id=self.name+' '+outage_state, width=self.xml_header_width)
        self.outage_stats[outage_state][temp] = {}
        for voltage in self.test.voltages:
            xml_voltage = etree.SubElement(xml_outage, "voltage", value=str(voltage)+'V', width=self.xml_header_width)
            xml_systems = etree.SubElement(xml_voltage, "systems")
            self.outage_stats[outage_state][temp][voltage] = {}
            for system in self.systems:
                xml_system = etree.SubElement(xml_systems, "system")
                out_of_spec_bool = 'NA'
                outage_min, outage_max, outage_mean, outage_std = get_outage_stats_at_temp_voltage(df, self, system, temp, voltage)
                if run_limit_analysis and limits:
                    if outage_state == 'ON':
                        lower_limit, upper_limit = get_limits_for_outage_on(limits, self, voltage)
                    else:
                        lower_limit, upper_limit = get_limits_for_outage_off(limits, self, voltage)   
                    out_of_spec_bool = check_if_out_of_spec(lower_limit, upper_limit, outage_min, outage_max)
                    series = filter_temp_and_voltage(df, self.test.ambient, temp, voltage, self.test.temperature_tolerance)[system]
                    out_of_spec_count, percent_out = count_num_out_of_spec(series, lower_limit, upper_limit)
                self.outage_stats[outage_state][temp][voltage][system] = [outage_min, outage_max, outage_mean, out_of_spec_bool]
                xml_name = etree.SubElement(xml_system, "name")
                xml_name.text = str(system).split(' ', 1)[1]
                xml_min = etree.SubElement(xml_system, "min")
                xml_min.text = str(outage_min)
                xml_max = etree.SubElement(xml_system, "max")
                xml_max.text = str(outage_max)
                xml_mean = etree.SubElement(xml_system, "mean")
                xml_mean.text = str(outage_mean)
                xml_std = etree.SubElement(xml_system, "std")
                xml_std.text = str(outage_std)
                xml_count = etree.SubElement(xml_system, "count")
                xml_count.text = str(out_of_spec_count)
                xml_percent_out = etree.SubElement(xml_system, "percent-out")
                xml_percent_out.text = str(percent_out)
                xml_check = etree.SubElement(xml_system, "check")
                xml_check.text = 'NA' if (not run_limit_analysis or not limits) else 'Out of Spec' if out_of_spec_bool else 'G'

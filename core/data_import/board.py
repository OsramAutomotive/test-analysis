#!/usr/bin/python3

"""
This module contains the Board class and Outage class. These classes
model the test station boards. """

import re
from lxml import etree

from core.re_and_global import REGEX_SPECIFIC_BOARD_SYSTEMS, \
                               REGEX_SPECIFIC_BOARD_ON_OFF

from core.data_import.helpers import filter_board_on_or_off, \
                                     filter_temp_and_voltage, \
                                     get_system_test_position_int, \
                                     check_if_out_of_spec, \
                                     get_outage_stats_at_temp_voltage, \
                                     count_num_out_of_spec

from core.limits_import.limits import get_limits_for_outage_on, \
                                      get_limits_for_outage_off

class Board(object):
    """
    Holds information and test data collected on a C&M test station board.

    Attributes:
        test => belongs to a test station object that describes the test
        folder => directory folder of data that was analyzed
        id => e.g. - 'B3'
        name => e.g. - 'DRL'
        board => board object (includes board id)
        system => list of used test positions and system numbers (used for df query)
        df => dataframe of just this board
    
    Essential Methods:

    """

    AMB_TEMP = 'Temp TC1'
    VSETPOINT = 'VSetpoint'

    def __init__(self, test, board_number):
        self.test = test
        self.id = '' # e.g. - 'B3'
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
        """ Set the board id attribute (e.g. - 'B5') """
        if isinstance(board_number, int):
            self.id = 'B'+str(board_number)
        elif isinstance(board_number, str):
            if ('B' in board_number) or ('b' in board_number):
                self.id = board_number.upper()
            else:
                self.id = 'B' + board_number

    def __get_board_name(self):
        """ Pull name of board (e.g. 'DRL') from limits file (if provided) """
        try:
            self.name = self.test.limits.board_module_pairs[self.id]
        except:
            self.name = self.id
            print('Could not load board name for', self.id)

    def __get_board_systems(self):
        """ Retrieves the systems measured on this board and populates the
            'systems' attribute with these systems.
            (e.g. - 'B3 TP4: System 46')
        """
        set_of_systems = set()
        for col_name in self.test.df.columns:
            if re.search(REGEX_SPECIFIC_BOARD_SYSTEMS(self.id), col_name):
                system_name = re.search(REGEX_SPECIFIC_BOARD_SYSTEMS(self.id), col_name).group()
                set_of_systems.add(system_name)

        self.systems = sorted(list(set_of_systems),
                              key=lambda sys: get_system_test_position_int(sys, index=1))


class Outage(Board):
    """
    Inherits from Board class. Holds information and test data collected
    on an Outage test station board.

    Attributes:
        outage (boolean): True
        outage_stats (dict): stores min/max values at different voltages
                             for Outage ON and OFF conditions
        systems (list): list of Outage systems

    Essential Methods:
        get_system_by_system_outage_stats:

    """

    def __init__(self, test, board_number):
        Board.__init__(self, test, board_number)
        self.outage = True
        self.outage_stats = {'ON':{}, 'OFF': {}}
        self.systems = self.__find_systems()
        self.board_on_off = self.__find_on_off_col()
        self.xml_header_width = str(len(self.systems)+1)

    def __find_systems(self):
        """ Find the systems for this board
        Returns:
            systems (list): list of systems used on this board
        """
        systems = []
        for col_name in self.test.df.columns:
            if re.search(REGEX_SPECIFIC_BOARD_SYSTEMS(self.id), col_name):
                systems.append(col_name)
        return systems

    def __find_on_off_col(self):
        """ Find board_on_off column for outage board
        Returns:
            board_on_off (list): list of the board_on_off df column
        """
        board_on_off = []
        for col_name in self.test.df.columns:
            if re.search(REGEX_SPECIFIC_BOARD_ON_OFF(self.id), col_name):
                board_on_off.append(col_name)
        return board_on_off

    def get_system_by_system_outage_stats(self, xml_temp, temp, run_limit_analysis, limits):
        """ Retrieve outage stats for each system """
        xml_outages = etree.SubElement(xml_temp, "outages",
                                       id=self.name, width=self.xml_header_width)
        df = self.test.df[[self.test.VSETPOINT] + self.test.thermocouples + \
                          self.board_on_off + self.systems]
        df_on = filter_board_on_or_off(df, self.id, 1)
        df_off = filter_board_on_or_off(df, self.id, 0)
        self.get_outage_stats_in_state(df_off, xml_outages, temp, run_limit_analysis,
                                       limits, outage_state='OFF')
        self.get_outage_stats_in_state(df_on, xml_outages, temp, run_limit_analysis,
                                       limits, outage_state='ON')

    def get_outage_stats_in_state(self, df, xml_outages, temp, run_limit_analysis,
                                  limits, outage_state):
        """ Get outage stats for outage 'ON' or 'OFF' state """
        ## TODO => refactor this method
        xml_outage = etree.SubElement(xml_outages, "outage", id=self.name+' '+outage_state,
                                      width=self.xml_header_width)
        self.outage_stats[outage_state][temp] = {}
        for voltage in self.test.voltages:
            xml_voltage = etree.SubElement(xml_outage, "voltage", value=str(voltage)+'V',
                                           width=self.xml_header_width)
            xml_systems = etree.SubElement(xml_voltage, "systems")
            self.outage_stats[outage_state][temp][voltage] = {}
            for system in self.systems:
                xml_system = etree.SubElement(xml_systems, "system")
                out_of_spec_bool = 'NA'
                outage_min, outage_max, outage_mean, outage_std = get_outage_stats_at_temp_voltage(
                    df, self, system, temp,
                    voltage)
                if run_limit_analysis and limits:
                    if outage_state == 'ON':
                        lower_limit, upper_limit = get_limits_for_outage_on(limits, self, voltage)
                    else:
                        lower_limit, upper_limit = get_limits_for_outage_off(limits, self, voltage)
                    out_of_spec_bool = check_if_out_of_spec(lower_limit, upper_limit,
                                                            outage_min, outage_max)
                    series = filter_temp_and_voltage(df, self.test.ambient, temp, voltage,
                                                     self.test.temperature_tolerance)[system]
                    total_count, out_of_spec_count, percent_out = count_num_out_of_spec(series,
                                                                                        lower_limit,
                                                                                        upper_limit)
                self.outage_stats[outage_state][temp][voltage][system] = [outage_min,
                                                                          outage_max,
                                                                          outage_mean,
                                                                          out_of_spec_bool]
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
                if run_limit_analysis and limits:
                    xml_count = etree.SubElement(xml_system, "count")
                    xml_count.text = str(total_count)
                    xml_count = etree.SubElement(xml_system, "count-out")
                    xml_count.text = str(out_of_spec_count)
                    xml_percent_out = etree.SubElement(xml_system, "percent-out")
                    xml_percent_out.text = str(percent_out)
                xml_check = etree.SubElement(xml_system, "check")
                xml_check.text = 'NA' if (not run_limit_analysis or not limits) else \
                                 'Out of Spec' if out_of_spec_bool else 'G'

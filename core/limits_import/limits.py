"""
This module contains a Limits class that stores current limits from
a specified project limits filepath.
"""

import pprint as pp
from bs4 import BeautifulSoup

class Limits(object):
    """
    Attributes:
        filepath (string): The filepath to the limits file
        lim (dict): Holds current limits in form:
                    {Mode->Temp->Voltage->(min current, max current)}
        boards (list of strings): Boards that are present in data
        modules (list of strings): Modules that are present in data 
                        e.g. - 'PARK' or 'TURN' etc.
        board_module_pairs (dict): keys: boards, values: modules
        temps (list of integers): Temperatures to load limits for
                                  e.g. - 85 or -40 or 23 etc.
    Essential methods:
        get_board_info: Retrieves board/module info from file
        get_limits: Retrieves current limits for all modes from file
        print_info: Prints board module pairs and the current limits
    """
    def __init__(self, filepath):
        # TODO --> reduce number of attributes to 5
        self.filepath = filepath
        self.lim = {}
        self.soup = ''
        self.modules = []
        self.board_module_pairs = {}
        self.outage_board = ''
        self.outage_present = False
        self.binning = False
        self.led_binning_dict = {}

        self.set_soup()
        self.get_board_info()
        self.get_limits()

    def set_soup(self):
        """ Set BeautifulSoup instance to parse limits file """
        with open(self.filepath) as filepath:
            self.soup = BeautifulSoup(filepath, 'lxml')

    def get_board_info(self):
        """ Retrieve board information from limits file """
        board_rows = self.soup.find_all(class_='board')
        for board_row in board_rows:
            data = board_row.find_all('td')
            board = data[0].string
            module = data[1].string
            led_bins = data[2].string
            is_outage = data[3].string
            self.board_module_pairs[board] = module
            self.modules.append(module)
            if led_bins:
                self.binning = True
                self.led_binning_dict[board] = led_bins.split(' ')
            # if is_outage == 'YES':
            if is_outage:
                self.outage_board = board
                self.outage_present = True

    def get_limits(self):
        """ Get limits for each mode present """
        modes = self.soup.find_all(class_='mode')
        for mode in modes:
            self._get_mode_limits(mode)
        if 'OUTAGE' in self.modules:
            self._get_outage_limits()

    def _get_mode_limits(self, mode):
        """ Need docstring """
        mode_id = mode.get('id')
        self.lim[mode_id] = {}
        temp_tables = mode.find_all(class_='temp-table')
        for temp_table in temp_tables:
            temp = temp_table.get('class')[-1].replace('temp', '')
            temp = int(temp.replace('C', ''))
            self.lim[mode_id][temp] = {}
            voltage_rows = temp_table.find_all(lambda tag: tag.get('id') == 'voltage')
            for voltage_row in voltage_rows:
                voltage = round(float(voltage_row.get('class')[0]), 1)
                minimum = round(float(voltage_row.find(class_='min').string), 3)
                maximum = round(float(voltage_row.find(class_='max').string), 3)
                self.lim[mode_id][temp][voltage] = (minimum, maximum)

    def _get_outage_limits(self):
        """ Need docstring """
        outage_tables = self.soup.find_all(class_='outage-table')
        self.lim['OUTAGE'] = {}
        for outage_table in outage_tables:
            outage_state = outage_table.get('state')
            self.lim['OUTAGE'][outage_state] = {}
            voltage_rows = outage_table.find_all(lambda tag: tag.get('id') == 'voltage')
            for voltage_row in voltage_rows:
                voltage = round(float(voltage_row.get('class')[0]), 1)
                minimum = round(float(voltage_row.find(class_='min').string), 3)
                maximum = round(float(voltage_row.find(class_='max').string), 3)
                self.lim['OUTAGE'][outage_state][voltage] = (minimum, maximum)

    def print_info(self):
        """ Need docstring """
        print('\n*** Limits Details ***')
        print('\nBoard-Module Pairs:')
        pp.pprint(self.board_module_pairs)
        print('\nCurrent Limits:')
        pp.pprint(self.lim)
        print('\n')


### Limits helper functions
def get_limits_at_mode_temp_voltage(limits, mode, temp, voltage):
    """ Attempt to pull mode/temp/voltage condition current limits from Limits object
    Args:
        limits (Limits object): Product limits data object (extracted previously from limits file)
        mode (Mode object): Mode of desired current limits
        temp (int): Temperature of desired current limits
        voltage (float): Voltage of desired current limits
    Returns:
        mode_limits_dict (dict): Limits at input mode/temp/voltage
                                 (e.g. - {'LL': 1.369, 'UL': 1.673})
    """
    if mode.has_led_binning:
        mode_limits_dict = get_all_mode_limits_with_binning(
                               limits, mode, temp, voltage)
    else:
        mode_limits_dict = get_limits_without_binning(
                               limits, mode, temp, voltage)
    return mode_limits_dict

def get_limits_without_binning(limits, mode, temp, voltage):
    """ Returns: dict of current LL and UL for input mode/temp/voltage
        condition (no LED binning) """
    try:
        lower_limit = limits.lim[mode.name][temp][voltage][0]
        upper_limit = limits.lim[mode.name][temp][voltage][1]
        return {'LL': lower_limit, 'UL': upper_limit}
    except:
        raise

def get_all_mode_limits_with_binning(limits, mode, temp, voltage):
    """ Need docstring """
    mode_bin_limits_dict = {}
    for led_bin in mode.led_bins:
        module_header = led_bin + ' ' + mode.name
        try:
            mode_bin_limits_dict[led_bin+' LL'] = limits.lim[module_header][temp][voltage][0]
            mode_bin_limits_dict[led_bin+' UL'] = limits.lim[module_header][temp][voltage][1]
        except:
            raise
    return mode_bin_limits_dict

def get_limit_for_single_led_bin(led_bin, limits, mode, temp, voltage):
    """ Need docstring """
    mode_bin_limits_dict = {}
    module_header = led_bin + ' ' + mode.name
    try:
        mode_bin_limits_dict[led_bin+' LL'] = limits.lim[module_header][temp][voltage][0]
        mode_bin_limits_dict[led_bin+' UL'] = limits.lim[module_header][temp][voltage][1]
    except:
        raise
    return mode_bin_limits_dict

def get_limits_for_system_with_binning(limits, mode, temp, voltage, system):
    """ Need docstring """
    led_bin = get_system_bin(mode, system)
    module_header = led_bin + ' ' + mode.name
    try:
        lower_limit = limits.lim[module_header][temp][voltage][0]
        upper_limit = limits.lim[module_header][temp][voltage][1]
        return {'LL': lower_limit, 'UL': upper_limit}
    except:
        raise

def get_system_bin(mode, system):
    """ Need docstring """
    possible_bins = system.split(' ')
    for led_bin in possible_bins:
        if led_bin in mode.led_bins:
            return led_bin
    return None

def get_limits_for_outage_off(limits, board, voltage):
    """ Returns: tuple of LL and UL for Outage when OFF """
    try:
        lower_limit = limits.lim[board.name]['OFF'][voltage][0]
        upper_limit = limits.lim[board.name]['OFF'][voltage][1]
        return lower_limit, upper_limit
    except:
        raise

def get_limits_for_outage_on(limits, board, voltage):
    """ Returns: tuple of LL and UL for Outage when ON """
    try:
        lower_limit = limits.lim[board.name]['ON'][voltage][0]
        upper_limit = limits.lim[board.name]['ON'][voltage][1]
        return lower_limit, upper_limit
    except:
        raise

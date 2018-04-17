#!/usr/bin/python3

""" This module contains functions that help build dataframes (data type created using "pandas")
from the selected test data text files. These dataframes  are passed on to other modules for
analysis (statistics, tables, plotting, histograms, etc.). The "dataframe" data type is
lightweight and efficient; it is extremely useful format for conducting this type of large
data size analysis. """

import os
import re
import itertools
import pandas as pd

from core.data_import.helpers import run_from_ipython, \
                                     get_system_test_position_int, \
                                     copy_and_remove_b6_from, \
                                     mask_to_mode
from core.data_import.board import Board, Outage
from core.data_import.mode import Mode
from core.exceptions.custom_exceptions import BoardNotFoundError
from .. re_and_global import REGEX_RAW_DATAFILE, \
                             REGEX_EMPTY_TEST_POSITION, \
                             REGEX_TEMPS, \
                             REGEX_BOARDS, \
                             REGEX_SYSTEMS, \
                             REGEX_VOLTAGE_SENSES, \
                             ON_OFF

pd.options.mode.chained_assignment = None  # default='warn'


## parsing function for datetime index on dataframes
DATE_PARSER = lambda x: pd.datetime.strptime(x, '%Y/%m/%d %H:%M:%S.%f')

class TestStation(object):
    """
    Holds information and test data collected on a test station board.

    Attributes:
        folder => directory folder containing raw csv file data that was analyzed
        systems => list of used test positions and system numbers (also used for df query)
        boards => list of boards (as board objects) that were used for test
        mode_df_dict =>
        modes =>
        df => dataframe that holds all board data
    Essential Methods:
    """

    VSETPOINT = 'Vsetpoint'
    VSENSE1 = 'VSense1'

    def __init__(self, name, folder, boards, limits=None, run_limit_analysis=False,
                 multimode=False, temperature_tolerance=3, voltage_tolerance=0.5, *temps):
        self.name = name
        self.folder = folder
        self.files = []
        self.boards = []
        self.board_ids = boards if isinstance(boards, list) else []
        self.current_board_ids = []
        self.systems = []
        self.limits = limits
        self.run_limit_analysis = run_limit_analysis
        self.temperature_tolerance = temperature_tolerance
        self.voltage_tolerance = voltage_tolerance
        self.voltages = []
        self.temps = temps
        self.voltage_senses = []
        self.thermocouples = []
        self.on_off = [ON_OFF]
        self.df = pd.DataFrame() # 'mother' dataframe holds all measured data
        self.mode_df_dict = {}  # holds mode_df for each data mask
        self.mode_ids = []
        self.modes = []
        self.multimode = multimode
        self.outage = False
        self.out_of_spec_df = pd.DataFrame()
        self.error_msg = ''
        self.ambient = None

        self.__build_dataframe()
        if not self.df.empty:
            self.__scan_for_boards()
            self.__scan_for_systems()
            self.__scan_for_vsetpoints()
            self.__scan_for_voltage_senses()
            self.__scan_for_thermocouples()
            self.__set_ambient_thermocouple()
            self.__create_boards()
            self.__set_current_board_ids()
            self.__make_df_dict()
            self.__make_modes()

    def __repr__(self):
        return '{}: {} {}'.format(self.__class__.__name__,
                                  self.board_ids, self.folder)

    def __build_dataframe(self):
        """ Builds all files in folder for board into a single dataframe
        using the pandas module """
        print('Scanning folder for datafiles...')
        if os.listdir(self.folder): # if folder not empty
            datafiles = os.listdir(self.folder)
            datafiles.sort(key=lambda fn: os.path.getmtime(os.path.join(self.folder, fn)))
            for filenumber, filename in enumerate(datafiles):
                if bool(re.search(REGEX_RAW_DATAFILE, filename)):
                    print('\tAppending File', '#'+str(filenumber+1)+': ', filename)
                    try:
                        if run_from_ipython():  # if running from ipython (jupyter)
                            next_file_df = pd.read_csv(self.folder+'/'+ filename,
                                                       parse_dates={'Date Time': [0, 1]},
                                                       date_parser=DATE_PARSER,
                                                       index_col='Date Time', sep='\t',
                                                       engine='python')
                        else:  # else running on local machine
                            next_file_df = pd.read_csv( 
                                               os.path.abspath(os.path.join(os.sep, self.folder, filename)),
                                               parse_dates={'Date Time': [0, 1]}, date_parser=DATE_PARSER,
                                               index_col='Date Time', sep='\t', engine='python')
                    except Exception:
                        print('The following error occurred while attempting to convert the ' \
                              'data files to pandas dataframes:\n\n')
                        raise
                    self.files.append(filename)
                    self.df = self.df.append(next_file_df)
            self.delete_empty_columns()
            try:
                self.df = self.df.replace(['OFF'], [0])
                self.df = self.df.astype(float)
            except TypeError as e:
                pass
            if self.df.empty:
                self.error_msg = '\nNo files in the selected folder match ' + \
                                 'the Labview raw datafile convention.\n'
        else:
            self.error_msg = '\nThere are no datafiles in the selected folder.\n'


    def delete_empty_columns(self):
        """ Deletes empty test position and thermocouple columns in dataframe """
        for col in self.df.columns.copy():
            if re.search(REGEX_EMPTY_TEST_POSITION, col):
                del self.df[col]
        temps = list(filter(lambda col_name: re.search(REGEX_TEMPS, col_name), self.df.columns))
        for temp_col in temps.copy():  # delete temperature columns with no readings
            if self.df[temp_col][0] == 'No Reading':
                del self.df[temp_col]

    def __scan_for_boards(self):
        """ Scan for boards present in dataframe """
        set_of_boards = set()
        for col_name in self.df.columns:
            if re.search(REGEX_BOARDS, col_name):
                set_of_boards.add(re.search(REGEX_BOARDS, col_name).group())
        present_board_ids = sorted(list(set_of_boards))
        # Real Time mode (autosense what boards are present)
        if not self.board_ids:
            self.board_ids = present_board_ids
        # Normal mode (boards to analyze are chosen by user)
        else:
            for board_id in self.board_ids:
                if board_id not in present_board_ids:
                    raise BoardNotFoundError("BoardNotFoundError: " + '"'+board_id+'"' + \
                       " was not found in the raw data. Are you sure it is ON for this test?")

    def __scan_for_systems(self):
        """ Scans data for all systems and removes blank test positions """
        set_of_systems = set()
        for col_name in self.df.columns:
            if re.search(REGEX_SYSTEMS, col_name):
                system_name = re.search(REGEX_SYSTEMS, col_name).groups()[0]
                set_of_systems.add(system_name)
        self.systems = sorted(list(set_of_systems),
                              key=lambda sys: get_system_test_position_int(sys))

    def __scan_for_voltage_senses(self):
        """ Scans for voltage sense columns """
        for col_name in self.df.columns:
            if re.search(REGEX_VOLTAGE_SENSES, col_name):
                self.voltage_senses.append(col_name)

    def __scan_for_thermocouples(self):
        """ Scans for thermocouple columns and removes those that have misreadings """
        possible_thermocouples = []
        for col_name in self.df.columns:
            if re.search(REGEX_TEMPS, col_name):
                possible_thermocouples.append(col_name)
        for tc in possible_thermocouples:
            tc_series = self.df[tc]
            if not (tc_series > 150).any() and not (tc_series < -150).any():
                self.thermocouples.append(tc) # only thermocouples without test errors

    def __set_ambient_thermocouple(self):
        """ Set ambient thermocouple to first thermocouple """
        if self.thermocouples:
            for tc in self.thermocouples:
                if "tc1" in tc.lower():
                    self.ambient = tc
                    break
            if self.ambient is None:
                self.ambient = self.thermocouples[0]
                print('\n"TC1" not found in any thermocouple names. By default, using first tc as ambient.\n')

    def __create_boards(self):
        """ Creates board dataframes for each board passed into TestStation init """
        print('\nRetrieving board module names: ')
        for board in self.board_ids:
            if self.limits and (board == self.limits.outage_board):
                self.outage = Outage(self, board)
                self.boards.append(self.outage)
            else:
                self.boards.append(Board(self, board))

    def __set_current_board_ids(self):
        """ Set list of present current boards (no voltage/outage boards) """
        self.current_board_ids = sorted([board.id for board in self.boards if not board.outage])

    def __scan_for_vsetpoints(self):
        self.voltages = sorted(set(self.df[self.VSETPOINT]))

    def __make_df_dict(self):
        """ Outputs dictionary of ON time mask modes dataframes. This includes
            all boards in df (even off ones, outage included). """
        # TODO ==> refactor
        if self.multimode:
            # list of all combinations on/off
            masks = [''.join(seq) for seq in itertools.product('01', repeat=len(self.boards))]
            for mask in masks:  # retrieve only excited modes
                if '1' not in mask:
                    continue
                mode = mask_to_mode(mask, self.board_ids)
                # float type to compare with df board on/off col
                float_mask = [float(digit) for digit in mask]
                data = self.df.copy()  # make copy of 'mother' dataframe
                # for each specific mode (mask), join together all board dfs that are ON in mask
                i = 0
                for i in range(len(mask)):
                    board, on_off_state = self.boards[i].id, float_mask[i]
                    data = data.loc[(self.df[board + ' ' + ON_OFF] == on_off_state)]
                    i += 1
                if not data.empty:
                    self.mode_df_dict[mode] = data  # save mode data in dictionary with mode key

        else: # (NOT multimode)
            data = pd.DataFrame  # make copy of 'mother' dataframe
            for board in self.boards:
                mode = board.id
                if mode != 'TEMPORARY OUTAGE STRING': # TODO -> skip voltage/outage boards
                    data = self.df.loc[(self.df[mode + ' ' + ON_OFF] == 1.0)]
                    if not data.empty:
                        self.mode_df_dict[mode] = data

        self.mode_ids = list(self.mode_df_dict.keys())  # assign mode ids
        # sort by length first, then board number
        self.mode_ids = sorted(sorted(self.mode_ids), key=lambda x: len(x))

    def __make_modes(self):
        """ Create Mode instances for each mode present in data and append to 'modes' attribute """
        for mode_id in self.mode_ids:
            board_ids = self.get_current_boards_from_mode_id(mode_id)
            mode_id_no_outage = ''.join(sorted(board_ids))
            if len(board_ids) == 1:
                self.modes.append(Mode(self, mode_id_no_outage, self.mode_df_dict[mode_id],
                                       self.voltages, *self.temps))
            elif len(board_ids) == 2 and self.boards_have_same_system_labels(*board_ids):
                self.modes.append(Mode(self, mode_id_no_outage, self.mode_df_dict[mode_id],
                                       self.voltages, *self.temps))

    def get_current_boards_from_mode_id(self, mode_id):
        """ Gets current board ids for input mode
        Args:
            mode_id (string): Input mode (e.g. - 'B1B2')
        Returns:
            list of board ids (list): Current board ids that are ON in input mode
        """
        board_ids = re.findall('B[0-9]*', mode_id)
        return list(set(board_ids) & set(self.current_board_ids))

    def boards_have_same_system_labels(self, board_id_1, board_id_2):
        """ Return True/False if boards have the same system label """
        board_dict = {board.id: board for board in self.boards}
        board_1 = board_dict[board_id_1]
        board_2 = board_dict[board_id_2]
        return board_1.systems[0].split(' ', 1)[1] == board_2.systems[0].split(' ', 1)[1]

    def print_board_information(self):
        print('\nBoards:', self.boards)
        print('Board combos present: ', self.mode_ids, '\n')

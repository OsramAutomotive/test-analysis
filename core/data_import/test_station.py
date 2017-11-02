#!/usr/bin/python3

''' This module contains functions that help build dataframes (data type created using "pandas")
from the selected test data text files. These dataframes  are passed on to other modules for analysis
(statistics, tables, plotting, histograms, etc.). The "dataframe" data type is lightweight and efficient;
it is extremely useful format for conducting this type of large data size analysis. '''

import itertools
import pandas as pd
import sys

from .. re_and_global import *
from core.data_import.helpers import *
from core.data_import.board import *
from core.data_import.mode import *

pd.options.mode.chained_assignment = None  # default='warn'


class TestStation(object):
    """
    Holds information and test data collected on a test station board.

    Example highlights::
        folder => directory folder containing raw csv file data that was analyzed
        systems => list of used test positions and system numbers (also used for df query)
        boards => list of boards (as board objects) that were used for test
        mode_df_dict => 
        modes => 
        df => dataframe that holds all board data
    """

    VSETPOINT = 'VSetpoint'
    VSENSE1 = 'Vsense 1st'

    def __init__(self, name, folder, boards, limits=None, run_limit_analysis=False, 
                 multimode= False, temperature_tolerance=3, voltage_tolerance=0.5, *temps):
        self.name = name
        self.folder = folder
        self.files = []
        self.boards = []
        self.board_ids = boards if (type(boards) == list) else []
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
            self.__delete_empty_columns()
            self.__scan_for_boards()
            self.__scan_for_systems()
            self.__scan_for_vsetpoints()
            self.__scan_for_voltage_senses()
            self.__scan_for_thermocouples()
            self.__create_boards()
            self.__set_current_board_ids()
            self.__make_df_dict()
            self.__make_modes()

    def __repr__(self):
        return '{}: {} {}'.format(self.__class__.__name__,
                               self.board_ids, self.folder)

    def __build_dataframe(self):
        ''' Builds all files in folder for board into a single dataframe 
        using the pandas module '''
        print('Scanning folder for datafiles...')
        if os.listdir(self.folder): ## if folder not empty
            for filenumber, filename in enumerate(os.listdir(self.folder)):
                if bool(re.search(REGEX_RAW_DATAFILE, filename)):
                    print('\tAppending File', '#'+str(filenumber+1)+': ', filename)
                    try:
                        if run_from_ipython():  # if running from ipython (jupyter)
                            next_file_df = pd.read_csv( self.folder+'/'+ filename, 
                                           parse_dates={'Date Time': [0,1]}, date_parser=date_parser, 
                                           index_col='Date Time', sep='\t', engine='python')
                        else:  # else running on local machine
                            next_file_df = pd.read_csv( os.path.abspath(os.path.join(os.sep, self.folder, filename)), 
                                           parse_dates={'Date Time': [0,1]}, date_parser=date_parser, 
                                           index_col='Date Time', sep='\t', engine='python')
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
                pass
            if self.df.empty:
                self.error_msg= '\nNo files in the selected folder match the Labview raw datafile convention.\n'
        else:
            self.error_msg = '\nThere are no datafiles in the selected folder.\n'

    def __delete_empty_columns(self):
        ''' Deletes emtpy test position and thermocouple columns in dataframe '''
        for col in self.df.columns.copy():
            if re.search(REGEX_EMPTY_TEST_POSITION, col):
                del self.df[col]
        temps = [self.df.columns[i] for i in range(len(self.df.columns)) if re.search(REGEX_TEMPS, self.df.columns[i])]
        for temp_col in temps.copy():  ## delete temperature columns with no readings
            if self.df[temp_col][0] == 'No Reading':
                del self.df[temp_col]

    def __scan_for_boards(self):
        ''' TO DO --> Add logic that alerts user if entered boards in normal mode are not present in data '''
        if not self.board_ids: ## if board ids list is empty then autosense what boards are present (REAL TIME MODE)
            set_of_boards = set()
            for board in [re.search(REGEX_BOARDS, column).group(0) for column in self.df.columns if re.search(REGEX_BOARDS, column)]:
                set_of_boards.add(board)
            self.board_ids = sorted(list(set_of_boards))

    def __scan_for_systems(self):
        ''' Scans data for all systems and gets rid of blank test positions '''
        set_of_systems = set()
        for system in [re.search(REGEX_SYSTEMS, column).groups()[0] for column in self.df.columns if re.search(REGEX_SYSTEMS, column)]:
            set_of_systems.add(system)
        self.systems = sorted(list(set_of_systems), key=lambda sys: get_system_test_position_int(sys))

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
        self.thermocouples = sorted(self.thermocouples)
        if self.thermocouples:
            self.ambient = self.thermocouples[0]

    def __create_boards(self):
        ''' Creates board dataframes for each board passed into TestStation init '''
        for board in self.board_ids:
            if board == 'B6': ## outage board
                self.outage = Outage(self, board)
                self.boards.append(self.outage)
            else:  ## current board
                self.boards.append(Board(self, board))

    def __set_current_board_ids(self):
        self.current_board_ids = copy_and_remove_b6_from(self.board_ids)

    def __scan_for_vsetpoints(self):
        self.voltages = sorted(set(self.df[self.VSETPOINT]))

    def __make_df_dict(self):
        ''' Outputs dictionary of ON time mask modes dataframes. This includes
            all boards in df (even off ones, outage included). '''
        if self.multimode: ## (multimode)
            masks = [''.join(seq) for seq in itertools.product('01', repeat=len(self.boards))]  ## list of all combinations on/off   
            ## print('\t=> Possible board combinations: ', masks)
            for mask in masks:  ## retrieve only excited modes
                if '1' not in mask:
                    continue
                mode = mask_to_mode(mask, self.board_ids)
                float_mask = [float(digit) for digit in mask]  ## float type to compare with df board on/off col
                data = self.df.copy()  ## make copy of 'mother' dataframe
                ## for each specific mode (mask), join together all board dfs that are ON in mask
                i = 0
                for i in range(len(mask)):
                    board, on_off_state = self.boards[i].id, float_mask[i]
                    data = data.loc[(self.df[board + ' ' + ON_OFF] == on_off_state)]
                    i += 1
                if not data.empty:
                    self.mode_df_dict[mode] = data  ## save mode data in dictionary with mode key

        else: ## (NOT multimode)
            data = pd.DataFrame  ## make copy of 'mother' dataframe
            for board in self.boards:
                mode = board.id
                if mode != 'B6': ## skip outage board 
                    data = self.df.loc[(self.df[mode + ' ' + ON_OFF] == 1.0)]
                    if not data.empty:
                        self.mode_df_dict[mode] = data

        self.mode_ids = list(self.mode_df_dict.keys())  ## assign mode ids
        self.mode_ids = sorted(sorted(self.mode_ids), key=lambda x: len(x))  ## order by length first, then board number

    def __make_modes(self):
        for mode_id in self.mode_ids:
            self.modes.append(Mode(self, mode_id, self.mode_df_dict[mode_id], self.voltages, *self.temps))

    def print_board_information(self):
        print('\nBoards:', self.boards)
        print('Board combos present: ', self.mode_ids, '\n')

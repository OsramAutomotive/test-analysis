#!/usr/bin/python3

''' This module contains functions that help build dataframes (data type created using "pandas")
from the selected test data text files. These dataframes  are passed on to other modules for analysis
(statistics, tables, plotting, histograms, etc.). The "dataframe" data type is lightweight and efficient;
it is extremely useful format for conducting this type of large data size analysis. '''

import itertools
import pandas as pd

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
        mdf => 'mother' dataframe that holds all board data (?? plus mode data ??)
    """

    AMB_TEMP = 'Amb Temp TC1'
    VSETPOINT = 'VSetpoint'

    def __init__(self, name, boards, folder, limits=None, run_limit_analysis=False, multimode= False, *temps):
        self.name = name
        self.folder = folder
        self.systems = []
        self.limits = limits
        self.run_limit_analysis = run_limit_analysis
        self.voltages = []
        self.temps = temps
        self.voltage_senses = []
        self.thermocouples = []
        self.on_off = [ON_OFF]
        self.boards = []
        self.board_ids = []
        self.current_board_ids = []
        self.b1 = 'Not Used'
        self.b2 = 'Not Used'
        self.b3 = 'Not Used'
        self.b4 = 'Not Used'
        self.b5 = 'Not Used'
        self.b6 = 'Not Used'
        self.b7 = 'Not Used' # Tesla needs extra fake Board 7 for analysis
        self.mdf = pd.DataFrame() # 'mother' dataframe holds all measured data
        self.mode_df_dict = {}  # holds mode_df for each data mask
        self.mode_ids = []
        self.modes = []
        self.multimode = multimode
        self.outage = False
        self.out_of_spec_df = pd.DataFrame()

        self.__create_boards(boards)
        self.__set_on_boards()
        self.__set_board_ids()
        self.__set_systems()
        self.__set_voltage_senses()
        self.__set_thermocouples()
        self.__scan_for_outage()
        self.__build_test_station_dataframe()
        self.__scan_for_vsetpoints()
        self.__make_df_dict()
        self.__make_modes()

    def __repr__(self):
        return '{}: {} {}'.format(self.__class__.__name__,
                               self.board_ids, self.folder)

    def __create_boards(self, boards):
        ''' Creates board dataframes for each board passed into TestStation init '''
        boards = str(boards)  ## e.g. - boards: 123456 or 3456, etc
        for board in boards:
            if '1' in board:
                self.b1 = Board(self, board)
            elif '2' in board:
                self.b2 = Board(self, board)
            elif '3' in board:
                self.b3 = Board(self, board)
            elif '4' in board:
                self.b4 = Board(self, board)
            elif '5' in board:
                self.b5 = Board(self, board)
            elif '6' in board:
                self.b6 = Board(self, board)
            elif '7' in board:
                self.b7 = Board(self, board)

    def __set_on_boards(self):
        ''' Appends all test boards that were used to boards list '''
        for board in [self.b1, self.b2, self.b3, self.b4, self.b5, self.b6]:
            if board != 'Not Used':
                self.boards.append(board)

    def __set_board_ids(self):
        for board in self.boards:
            self.board_ids.append(board.id)
        self.current_board_ids = copy_and_remove_b6_from(self.board_ids)

    def __set_systems(self):
        ''' Sets the systems tested to the systems scanned on the first board '''
        self.systems = self.boards[0].systems

    def __set_voltage_senses(self):
        ''' Sets the voltage senses used to the voltage senses scanned on the first board '''
        self.voltage_senses = self.boards[0].voltage_senses

    def __set_thermocouples(self):
        ''' Sets the thermocouples used to the tcs scanned on the first board '''
        self.thermocouples = self.boards[0].thermocouples

    def __build_test_station_dataframe(self):
        ''' Builds a single test station "mother dataframe" (mdf) that includes
            all of the boards used for the test '''
        for board in self.boards:
            if self.mdf.empty:  ## if mdf is empty, assign mdf to first board dataframe 
                self.mdf = board.df.copy() 
            else:  ## append board df with board id suffix for matching columns
                self.mdf = self.mdf.join(board.df[self.on_off+self.voltage_senses+self.systems], 
                                         rsuffix=' '+board.id)
        rename_columns(self.mdf, self.boards[0], self.on_off+self.voltage_senses+self.systems) ## rename columns of first df appended

    def __scan_for_vsetpoints(self):
        ## TO DO --> ensure test position was used to prevent analysis of empty vsetpoint data
        self.voltages = sorted(set(self.mdf[self.VSETPOINT]))

    def __scan_for_outage(self):
        if any(board.outage for board in self.boards):
            self.outage = True

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
                data = self.mdf.copy()  ## make copy of 'mother' dataframe
                ## for each specific mode (mask), join together all board dfs that are ON in mask
                i = 0
                for i in range(len(mask)):
                    board, on_off_state = self.boards[i].id, float_mask[i]
                    data = data.loc[(self.mdf[ON_OFF+' '+board] == on_off_state)]
                    i += 1
                if not data.empty:
                    self.mode_df_dict[mode] = data  ## save mode data in dictionary with mode key
        else: ## (NOT multimode)
            data = pd.DataFrame  ## make copy of 'mother' dataframe
            for board in self.boards:
                mode = board.id
                if mode != 'B6': ## skip outage board 
                    data = self.mdf.loc[(self.mdf[ON_OFF+' '+mode] == 1.0)]
                    if not data.empty:
                        self.mode_df_dict[mode] = data

        self.mode_ids = list(self.mode_df_dict.keys())  ## assign mode ids
        self.mode_ids = sorted(sorted(self.mode_ids), key=lambda x: len(x))  ## order by length first, then board number
        print('\n=> Board combos present: ', self.mode_ids, '\n')

    def __make_modes(self):
        for mode_id in self.mode_ids:
            self.modes.append(Mode(self, mode_id, self.mode_df_dict[mode_id], self.voltages, *self.temps))

    def print_board_numbers(self):
        ''' Prints the ON boards used in test station for test '''
        for board in self.boards:
            print(board.id)

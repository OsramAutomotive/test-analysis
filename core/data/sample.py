#!/usr/bin/python3


class Sample(object):
    """
    Holds test data for a single light sample module (board/system pair).

    Example::
        system => test position and system number (used for df query)
        board => board object (includes board id)
        df => dataframe of just this system
    """

    AMB_TEMP = 'Amb Temp TC1'
    VSETPOINT = 'VSetpoint'
    
    def __init__(self, system, board):
        self.system = system
        self.board = board
        self.df = board.df[ [self.AMB_TEMP, self.VSETPOINT, self.system] ] 

    def __repr__(self):
        return '{}: {} {}'.format(self.__class__.__name__,
                           self.system, self.board)
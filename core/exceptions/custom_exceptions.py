#!/usr/bin/python3

"""
This module contains custom exceptions
"""

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class BoardNotFoundError(Error):
    """Raised when user inputs a board not present in the data.

    Attributes:
        board_id (str): board that was not found in data (e.g. - "B3")
        message (str): error message displayed to user
    """
    def __init__(self, message):
        self.message = message

class TemperatureNotFoundError(Error):
    """Raised when user inputs a temperature not present in the data.

    Attributes:
        temperature (int): temperature not present in data (e.g. - "85")
        message (str): error message displayed to user
    """
    def __init__(self, message):
        self.message = message

class LimitNotFoundError(Error):
    """Raised when a non-existent limit is attempted to be accessed.
    
    Attributes:
        message (str): error message displayed to user
    """
    def __init__(self, message):
        self.message = message

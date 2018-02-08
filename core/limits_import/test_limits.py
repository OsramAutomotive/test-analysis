"""
This test module contains tests on the Limits class
and its associated methods. 
"""


import pytest
from core.limits_import.limits import *


class MockMode(object):
    """ Mock up mode class for test setup """
    def __init__(self, name, binning_boolean):
        self.name = name
        self.has_led_binning = binning_boolean

@pytest.fixture
def mock_up_mode(name, binning_boolean=False):
    """ Mock up mode instance to use for testing """
    mode = MockMode(name, binning_boolean)
    return mode

@pytest.fixture
def p552_mca_limits():
    """ Returns Limits instance for P552 MCA """
    filepath = r"C:\Users\bruno\Programming Projects\Test Data Analysis" \
               r"\test files\limits files\mca-outage-true.htm"
    p552_limits = Limits(filepath)
    return p552_limits


def test_valid_p552_mca_limits(p552_mca_limits):
    """ Test valid limits inputs create a Limit instance with
        the correct board_module_pairs and lim attributes """
    expected_board_module_pairs = {'B1': 'LB',
                                   'B2': 'HB',
                                   'B3': 'PARK',
                                   'B4': 'DRL',
                                   'B5': 'TURN',
                                   'B6': 'OUTAGE'}
    expected_lim_dict = {'DRL': {23: {9.0: (1.093, 1.335),
                                      14.1: (0.7, 0.856),
                                      16.0: (0.616, 0.753)},
                                 -40: {9.0: (1.090, 1.333),
                                      14.1: (0.702, 0.858),
                                      16.0: (0.618, 0.755)},
                                 85: {9.0: (1.083, 1.324),
                                      14.1: (0.693, 0.847),
                                      16.0: (0.610, 0.745)}},
                         'PARK': {23: {9.0: (0.445, 0.544), 
                                      14.1: (0.272, 0.332),
                                      16.0: (0.240, 0.293)},
                                  -40: {9.0: (0.459, 0.561),
                                        14.1: (0.280, 0.342),
                                        16.0: (0.247, 0.302)},
                                  85: {9.0: (0.447, 0.546),
                                      14.1: (0.270, 0.330),
                                      16.0: (0.239, 0.292)}},
                         'TURN': {23: {9.0: (1.505, 1.839),
                                      14.1: (0.904, 1.105),
                                      16.0: (0.794, 0.971)},
                                  -40: {9.0: (1.571, 1.920),
                                        14.1: (0.940, 1.148),
                                        16.0: (0.824, 1.007)},
                                  85: {9.0: (1.462, 1.787),
                                      14.1: (0.877, 1.072),
                                      16.0: (0.770, 0.941)}},
                         'PARKTURN': {23: {9.0: (1.905, 2.329),
                                           14.1: (1.148, 1.403),
                                           16.0: (1.006, 1.230)},
                                      -40: {9.0: (1.972, 2.411),
                                            14.1: (1.190, 1.454),
                                            16.0: (1.043, 1.275)},
                                      85: {9.0: (1.866, 2.280),
                                           14.1: (1.118, 1.366),
                                           16.0: (0.981, 1.200)}},
                         'DRLTURN': {23: {9.0: (2.560, 3.129),
                                          14.1: (1.558, 1.905),
                                          16.0: (1.369, 1.673)},
                                     -40: {9.0: (2.580, 3.154),
                                           14.1: (1.583, 1.934),
                                           16.0: (1.392, 1.701)},
                                     85: {9.0: (2.527, 3.089),
                                          14.1: (1.528, 1.867),
                                          16.0: (1.356, 1.657)}},
                         'OUTAGE': {'OFF': {9.0: (-0.3, 0.3),
                                            14.1: (-0.3, 0.3),
                                            16.0: (-0.3, 0.3)},
                                    'ON': {9.0: (7.7, 20.0),
                                           14.1: (12.8, 20.0),
                                           16.0: (14.7, 20.0)}}}
    assert p552_mca_limits.board_module_pairs == expected_board_module_pairs
    assert p552_mca_limits.lim == expected_lim_dict


@pytest.mark.parametrize("limits, mode, temp, voltage, expected", [
  (p552_mca_limits(), mock_up_mode('DRL'), 23, 9.0, {'LL': 1.093, 'UL': 1.335}),
  (p552_mca_limits(), mock_up_mode('DRL'), -40, 14.1, {'LL': 0.702, 'UL': 0.858}),
  (p552_mca_limits(), mock_up_mode('DRL'), 85, 16.0, {'LL': 0.610, 'UL': 0.745}),

  (p552_mca_limits(), mock_up_mode('PARK'), 23, 9.0, {'LL': 0.445, 'UL': 0.544}),
  (p552_mca_limits(), mock_up_mode('PARK'), -40, 14.1, {'LL': 0.280, 'UL': 0.342}),
  (p552_mca_limits(), mock_up_mode('PARK'), 85, 16.0, {'LL': 0.239, 'UL': 0.292}),

  (p552_mca_limits(), mock_up_mode('PARKTURN'), 23, 9.0, {'LL': 1.905, 'UL': 2.329}),
  (p552_mca_limits(), mock_up_mode('PARKTURN'), -40, 14.1, {'LL': 1.190, 'UL': 1.454}),
  (p552_mca_limits(), mock_up_mode('PARKTURN'), 85, 16.0, {'LL': 0.981, 'UL': 1.200}),
])
def test_get_limits_at_mode_temp_voltage(limits, mode, temp, voltage, expected):
    """ Test correct current limits for input mode/temp/voltage condition 
        are retrieved (no LED binning) """
    mode_limits_dict = get_limits_at_mode_temp_voltage(limits, mode, temp, voltage)
    assert mode_limits_dict == expected


@pytest.mark.parametrize("limits, mode, voltage, expected", [
  (p552_mca_limits(), mock_up_mode('OUTAGE'), 9.0, (-0.3, 0.3)),
  (p552_mca_limits(), mock_up_mode('OUTAGE'), 14.1, (-0.3, 0.3)),
  (p552_mca_limits(), mock_up_mode('OUTAGE'), 16.0, (-0.3, 0.3)),
])
def test_get_limits_for_outage_off(limits, mode, voltage, expected):
    """ Test correct limits for Outage OFF are retrieved """
    lower_limit, upper_limit = get_limits_for_outage_off(limits, mode, voltage)
    assert (lower_limit, upper_limit) == expected


@pytest.mark.parametrize("limits, mode, voltage, expected", [
  (p552_mca_limits(), mock_up_mode('OUTAGE'), 9.0, (7.7, 20)),
  (p552_mca_limits(), mock_up_mode('OUTAGE'), 14.1, (12.8, 20)),
  (p552_mca_limits(), mock_up_mode('OUTAGE'), 16.0, (14.7, 20)),
])
def test_get_limits_for_outage_on(limits, mode, voltage, expected):
    """ Test correct limits for Outage ON are retrieved """
    lower_limit, upper_limit = get_limits_for_outage_on(limits, mode, voltage)
    assert (lower_limit, upper_limit) == expected

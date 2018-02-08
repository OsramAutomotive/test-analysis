""" 
This module tests the functions in helpers.py 
"""

import pytest
import pandas as pd
from core.data_import.helpers import *


@pytest.fixture
def temp_dataframe():
    """ Returns dataframe with temperature, voltage, and one sys current """
    dframe = pd.DataFrame([{'Amb': 72.1, 'VSetpoint': 9.0, 'Sys 1': 1.56},
                           {'Amb': 73.4, 'VSetpoint': 9.0, 'Sys 1': 1.54},
                           {'Amb': 74.2, 'VSetpoint': 14.1, 'Sys 1': 1.55},
                           {'Amb': 75.5, 'VSetpoint': 14.1, 'Sys 1': 1.57},
                           {'Amb': 77.7, 'VSetpoint': 14.1, 'Sys 1': 1.53},
                           {'Amb': 79.8, 'VSetpoint': 14.1, 'Sys 1': 1.55},
                           {'Amb': 80.1, 'VSetpoint': 14.1, 'Sys 1': 1.54},
                           {'Amb': 81.6, 'VSetpoint': 14.1, 'Sys 1': 1.52},
                           {'Amb': 82.3, 'VSetpoint': 16.0, 'Sys 1': 1.57},
                           {'Amb': 83.5, 'VSetpoint': 16.0, 'Sys 1': 1.50}])
    return dframe


@pytest.fixture
def on_off_dataframe():
    """ Returns dataframe with on/off, temp, and sys current """
    dframe = pd.DataFrame([{'B4 ON/OFF': 0, 'B5 ON/OFF': 2, 'VSetpoint': 9.0, 'Sys 1': 1.13},
                           {'B4 ON/OFF': 0, 'B5 ON/OFF': 1, 'VSetpoint': 9.0, 'Sys 1': 1.43},
                           {'B4 ON/OFF': 0, 'B5 ON/OFF': 1, 'VSetpoint': 9.0, 'Sys 1': 1.56},
                           {'B4 ON/OFF': 0, 'B5 ON/OFF': 1, 'VSetpoint': 14.1, 'Sys 1': 1.76},
                           {'B4 ON/OFF': 0, 'B5 ON/OFF': 0, 'VSetpoint': 14.1, 'Sys 1': 0.01},
                           {'B4 ON/OFF': 1, 'B5 ON/OFF': 0, 'VSetpoint': 14.1, 'Sys 1': -0.02},
                           {'B4 ON/OFF': 1, 'B5 ON/OFF': 0, 'VSetpoint': 16.0, 'Sys 1': 0.07},
                           {'B4 ON/OFF': 1, 'B5 ON/OFF': 1, 'VSetpoint': 16.0, 'Sys 1': 2.72},
                           {'B4 ON/OFF': 1, 'B5 ON/OFF': 1, 'VSetpoint': 16.0, 'Sys 1': 2.66},
                           {'B4 ON/OFF': 1, 'B5 ON/OFF': 2, 'VSetpoint': 16.0, 'Sys 1': 2.11}])
    return dframe


@pytest.mark.parametrize("list_of_boards, expected_output", [
    (['B1', 'B2', 'B3', 'B4', 'B5', 'B6'], ['B1', 'B2', 'B3', 'B4', 'B5']),
    (['B2', 'B3', 'B4', 'B5', 'B6'], ['B2', 'B3', 'B4', 'B5']), 
    (['B3', 'B4', 'B5', 'B6'], ['B3', 'B4', 'B5']),
    (['B4', 'B5', 'B6'], ['B4', 'B5']),
    (['B5', 'B6'], ['B5']),
    (['B6'], [])
])
def test_copy_and_remove_b6_from(list_of_boards, expected_output):
    list_without_outage = copy_and_remove_b6_from(list_of_boards)
    assert list_without_outage == expected_output


@pytest.mark.parametrize("system, expected_test_position_int", [
    ('TP1: System 1', 1),
    ('TP2: System 15', 2),
    ('TP3: System 89', 3),
    ('TP4: System 610', 4),
    ('TP5: System 31', 5),
    ('TP6: System 56', 6),
    ('TP7: System 76', 7),
    ('TP8: System 89', 8),
    ('TP9: System 100', 9),
    ('TP10: System 165', 10),
    ('TP11: System 13', 11),
    ('TP12: System 2', 12),
    ('TP13: System 9', 13),
    ('TP14: System 66', 14),
    ('TP15: System 43', 15),
    ('TP16: SN654046', 16),
    ('TP17: Vib Fail SF make', 17),
    ('TP18: C1YB proto', 18),
    ('TP19: 8K 6J System 33', 19),
    ('TP20: 9C 5B System 20', 20),
    ('TP21: adklfjaldfj', 21),
    ('TP22: alfkej', 22),
    ('TP23: Something', 23),
    ('TP24: Really long string that is long', 24)
])
def test_get_system_test_position_int(system, expected_test_position_int):
    test_position_num = get_system_test_position_int(system)
    assert test_position_num == expected_test_position_int


@pytest.mark.parametrize("temp, voltage, temp_tol," \
                         "expected_filtered_df", [
    (85.0, 14.1, 5.0, pd.DataFrame([{'Amb': 80.1, 'VSetpoint': 14.1, 'Sys 1': 1.54},
                                    {'Amb': 81.6, 'VSetpoint': 14.1, 'Sys 1': 1.52}],
                                    index = [6, 7])),
    (70.0, 9.0, 5.0, pd.DataFrame([{'Amb': 72.1, 'VSetpoint': 9.0, 'Sys 1': 1.56},
                                   {'Amb': 73.4, 'VSetpoint': 9.0, 'Sys 1': 1.54}],
                                   index = [0, 1])),
    (80.0, 16.0, 3.0, pd.DataFrame([{'Amb': 82.3, 'VSetpoint': 16.0, 'Sys 1': 1.57}],
                                    index = [8])),
    (75.0, 14.1, 2.0, pd.DataFrame([{'Amb': 74.2, 'VSetpoint': 14.1, 'Sys 1': 1.55},
                                    {'Amb': 75.5, 'VSetpoint': 14.1, 'Sys 1': 1.57}],
                                    index = [2, 3]))
])
def test_filter_temp_and_voltage(temp, voltage, temp_tol,
                                 expected_filtered_df):
    df = temp_dataframe()
    filtered_df = filter_temp_and_voltage(df, 'Amb', temp, voltage, temp_tol)
    pd.testing.assert_frame_equal(filtered_df, expected_filtered_df)


@pytest.mark.parametrize("temp, temp_tol, expected_filtered_df", [
    (73.0, 2.0, pd.DataFrame([{'Amb': 72.1, 'VSetpoint': 9.0, 'Sys 1': 1.56},
                              {'Amb': 73.4, 'VSetpoint': 9.0, 'Sys 1': 1.54},
                              {'Amb': 74.2, 'VSetpoint': 14.1, 'Sys 1': 1.55}])),
    (80.0, 0.5, pd.DataFrame([{'Amb': 79.8, 'VSetpoint': 14.1, 'Sys 1': 1.55},
                              {'Amb': 80.1, 'VSetpoint': 14.1, 'Sys 1': 1.54}],
                              index = [5,6])),
])
def test_filter_temperature(temp, temp_tol, expected_filtered_df):
    df = temp_dataframe()
    filtered_df = filter_temperature(df, 'Amb', temp, temp_tol)
    pd.testing.assert_frame_equal(filtered_df, expected_filtered_df)


@pytest.mark.parametrize("board_id, board_on_off_code, expected_filtered_df", [
    ('B4', 0, pd.DataFrame([{'B4 ON/OFF': 0, 'B5 ON/OFF': 2, 'VSetpoint': 9.0, 'Sys 1': 1.13},
                            {'B4 ON/OFF': 0, 'B5 ON/OFF': 1, 'VSetpoint': 9.0, 'Sys 1': 1.43},
                            {'B4 ON/OFF': 0, 'B5 ON/OFF': 1, 'VSetpoint': 9.0, 'Sys 1': 1.56},
                            {'B4 ON/OFF': 0, 'B5 ON/OFF': 1, 'VSetpoint': 14.1, 'Sys 1': 1.76},
                            {'B4 ON/OFF': 0, 'B5 ON/OFF': 0, 'VSetpoint': 14.1, 'Sys 1': 0.01}],
                            index = [0, 1, 2, 3, 4])),
    ('B4', 1, pd.DataFrame([{'B4 ON/OFF': 1, 'B5 ON/OFF': 0, 'VSetpoint': 14.1, 'Sys 1': -0.02},
                            {'B4 ON/OFF': 1, 'B5 ON/OFF': 0, 'VSetpoint': 16.0, 'Sys 1': 0.07},
                            {'B4 ON/OFF': 1, 'B5 ON/OFF': 1, 'VSetpoint': 16.0, 'Sys 1': 2.72},
                            {'B4 ON/OFF': 1, 'B5 ON/OFF': 1, 'VSetpoint': 16.0, 'Sys 1': 2.66},
                            {'B4 ON/OFF': 1, 'B5 ON/OFF': 2, 'VSetpoint': 16.0, 'Sys 1': 2.11}],
                            index = [5, 6, 7, 8, 9])),
    ('B5', 0, pd.DataFrame([{'B4 ON/OFF': 0, 'B5 ON/OFF': 0, 'VSetpoint': 14.1, 'Sys 1': 0.01},
                            {'B4 ON/OFF': 1, 'B5 ON/OFF': 0, 'VSetpoint': 14.1, 'Sys 1': -0.02},
                            {'B4 ON/OFF': 1, 'B5 ON/OFF': 0, 'VSetpoint': 16.0, 'Sys 1': 0.07}],
                            index = [4, 5, 6])),
    ('B5', 1, pd.DataFrame([{'B4 ON/OFF': 0, 'B5 ON/OFF': 1, 'VSetpoint': 9.0, 'Sys 1': 1.43},
                            {'B4 ON/OFF': 0, 'B5 ON/OFF': 1, 'VSetpoint': 9.0, 'Sys 1': 1.56},
                            {'B4 ON/OFF': 0, 'B5 ON/OFF': 1, 'VSetpoint': 14.1, 'Sys 1': 1.76},
                            {'B4 ON/OFF': 1, 'B5 ON/OFF': 1, 'VSetpoint': 16.0, 'Sys 1': 2.72},
                            {'B4 ON/OFF': 1, 'B5 ON/OFF': 1, 'VSetpoint': 16.0, 'Sys 1': 2.66}],
                            index = [1, 2, 3, 7, 8])),
    ('B5', 2, pd.DataFrame([{'B4 ON/OFF': 0, 'B5 ON/OFF': 2, 'VSetpoint': 9.0, 'Sys 1': 1.13}, 
                            {'B4 ON/OFF': 1, 'B5 ON/OFF': 2, 'VSetpoint': 16.0, 'Sys 1': 2.11}],
                            index = [0, 9])),
])
def test_filter_board_on_or_off(board_id, board_on_off_code, expected_filtered_df):
    df = on_off_dataframe()
    filtered_df = filter_board_on_or_off(df, board_id, board_on_off_code)
    pd.testing.assert_frame_equal(filtered_df, expected_filtered_df)


@pytest.mark.parametrize("lower_limit, upper_limit, sys_min, sys_max," \
                         "expected_output", [
    (1.0, 2.0, 0.5, 2.5, True),
    (1.0, 2.0, 1.3, 3.0, True),
    (1.0, 2.0, 0.75, 1.7, True),
    (1.0, 2.0, 1.2, 1.7, False),
    (0.355, 0.455, 0.250, 0.510, True),
    (0.355, 0.455, 0.360, 0.456, True),
    (0.355, 0.455, 0.353, 0.440, True),
    (0.355, 0.455, 0.360, 0.440, False),
])
def test_check_if_out_of_spec(lower_limit, upper_limit, sys_min, sys_max,
                              expected_output):
    """ Test check_if_out_of_spec returns True if min or max is above/below limits """
    out_of_spec = check_if_out_of_spec(lower_limit, upper_limit, sys_min, sys_max)
    assert out_of_spec == expected_output


@pytest.fixture
def current_series():
    """ Returns generic current series """
    series = pd.Series([0.45, 0.46, 0.47, 0.48, 0.49, 0.50, 0.51, 0.52, 0.53, 0.54, 0.55])
    return series

@pytest.mark.parametrize("lower_limit, upper_limit," \
                         "expected_total_count, expected_count_out_of_spec," \
                         "expected_percent_out", [
    (0.40, 0.60, 11, 0, '0.0%'),
    (0.45, 0.55, 11, 0, '0.0%'),
    (0.50, 0.60, 11, 5, '45.45%'),
    (0.40, 0.535, 11, 2, '18.18%'),
    (0.0, 0.2, 11, 11, '100.0%'),
    (0.60, 0.70, 11, 11, '100.0%'),
])
def test_count_num_out_of_spec(lower_limit, upper_limit, expected_total_count,
                               expected_count_out_of_spec, expected_percent_out):
    series = current_series()
    total_count, count_out_of_spec, percent_out = count_num_out_of_spec(series, 
                                                                        lower_limit, upper_limit)
    assert total_count == expected_total_count
    assert count_out_of_spec == expected_count_out_of_spec
    assert percent_out == expected_percent_out

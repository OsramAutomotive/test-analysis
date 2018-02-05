""" 
This module tests the functions in helpers.py 
"""

import pytest
from core.data_import.helpers import *


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
    ('TP24: REally long string that is long', 24)
])
def test_get_system_test_position_int(system, expected_test_position_int):
    test_position_num = get_system_test_position_int(system)
    assert test_position_num == expected_test_position_int

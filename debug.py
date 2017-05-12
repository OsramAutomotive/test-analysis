import sys
from core.data.test_station import *
from core.plotting.plots import *
from core.histograms.histograms import *
from core.tables.excel_write import *
from core.limits.limits import *

datapath = r"C:\Users\bruno\Programming Projects\Test Data Analysis\test files\PTC Raw Data"
limits_file = r"C:\Users\bruno\Programming Projects\Test Data Analysis\test files\P552 MCA PV AUX LIMITS.xlsx"

BOARDS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']  # all possible test station boards

boards = ['B3', 'B4', 'B5', 'B6']  # boards selected by user
temps = [-40, 85]  # temps selected by user

limits = Limits(limits_file, 'Sheet1', BOARDS, temps)
limits.print_info()

test = TestStation('Test', boards, datapath, limits, *temps)
test.boards # all boards that were used in the test
test.modes # all modes that were excited during the test
test.limits.board_module_pairs
test.systems  # names of systems/samples on all used test positions (up to 12 test positions) 
test.voltages # the voltages applied during the test
test.temps # all test temperatures


for mode in test.modes:
    for temp in temps:
        mode.get_system_by_system_mode_stats(temp, limits)

for mode in test.modes:
    mode.get_out_of_spec_data()
        

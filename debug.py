import sys
from core.data_import.test_station import *
from core.analysis.plots import *
from core.analysis.histograms import *
from core.analysis.tables import *
from core.limits.limits import *

#datapath = r"C:\Users\bruno\Programming Projects\Test Data Analysis\test files\MCA PTC Raw Data"
datapath = r"C:\Users\bruno\Programming Projects\Test Data Analysis\test files\A1XC PTC"
limits_file = r"C:\Users\bruno\Programming Projects\Test Data Analysis\test files\A1XC Limits.xlsx"

BOARDS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']  # all possible test station boards

boards = ['B3', 'B4', 'B5', 'B6']  # boards selected by user
temps = [-40, 70]  # temps selected by user

multimode = False
##limits = Limits(limits_file, 'Sheet1', BOARDS, temps)
##limits.print_info()
limits = None

test = TestStation('Test', boards, datapath, limits, multimode, *temps)

#make_mode_histograms(test, system_by_system=False, limits=limits)
fill_stats(test, limits, write_to_excel=True)

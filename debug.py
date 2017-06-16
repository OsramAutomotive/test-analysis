import sys
from core.data_import.test_station import *
from core.analysis.plots import *
from core.analysis.histograms import *
from core.analysis.tables import *
from core.limits.limits import *

#datapath = r"C:\Users\bruno\Programming Projects\Test Data Analysis\test files\MCA PTC Raw Data"
datapath = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\Tesla Model 3\DVPR\PV\De-rating\Env\!Raw Data"
limits_file = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\Tesla Model 3\DVPR\PV\Limits\Tesla Model 3 PV LIMITS de-rating.xlsx"

BOARDS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']  # all possible test station boards

#boards = ['B3', 'B4', 'B5', 'B6']  # boards selected by user
boards = ['B2', 'B4', 'B5']  # boards selected by user
temps = [23, 45, 65, 75, 80, 85, 90, 95]  # temps selected by user

multimode = False
run_limits = False
##limits = Limits(limits_file, 'Sheet1', BOARDS, temps)
##limits.print_info()
limits = Limits(limits_file, 'Sheet1', BOARDS, temps)

test = TestStation('Test', boards, datapath, limits, run_limits, multimode, *temps)

#plot_modes(test)
#make_mode_histograms(test, system_by_system=False, limits=limits)
#fill_stats(test, limits, write_to_excel=True)



##amb = 'Amb Temp TC1'
##vset = 'VSetpoint'
##
##i = 1
##for board in [test.b2, test.b4, test.b5]:
##    df8, df13, df16 = pd.DataFrame(), pd.DataFrame(),pd.DataFrame()
##    df8 = board.df[board.df[vset]==8.0]
##    df13 = board.df[board.df[vset]==13.5]
##    df16 = board.df[board.df[vset]==16]
##    voltages = [8.0, 13.5, 16]
##    dataframes = [df8, df13, df16]
##    data_dict = dict(zip(voltages, dataframes))
##
##    for v, df in data_dict.items():        
##        fig = plt.figure(i)
##        voltage = str(v)+'V'
##        fig.canvas.set_window_title('Current vs. Temp '+board.name+' '+voltage)
##        plt.title('Current vs. Temp: '+board.name+' '+voltage)
##        plt.xlabel('Temperature (C)')
##        plt.ylabel('Current (A)')
##        for sys in board.systems:
##            plt.scatter(df[amb], df[sys], alpha=0.5, label=sys)
##        plt.legend(bbox_to_anchor=(1.0, 0.5))
##        plt.subplots_adjust(right=0.77)
##        i+=1
##            

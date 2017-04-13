#!/usr/bin/python3

from core.tables.excel_write import *

# def get_limits_at_mode_temp_voltage(limits, mode, temp, voltage):
#     try:
#         lower_limit, upper_limit = limits.lim[temp][mode.mode_tag][voltage][0], limits.lim[temp][mode.mode_tag][voltage][1]  ## set current limits
#         return lower_limit, upper_limit
#     except:
#         raise

# def check_if_out_of_spec(lower_limit, upper_limit, sys_min, sys_max):
#     return (sys_min < lower_limit) or (sys_max > upper_limit)

# def get_system_stats_at_mode_temp_voltage(system, mode, temp, voltage):
#     series = mode.hist_dict[temp][voltage][system]
#     return series.min(), series.max(), series.mean(), series.std()

# def get_system_by_system_mode_stats(mode, limits=False):
#     stats = {}
#     for temp in mode.temps:
#         print('\n\n###### TEMPERATURE AT', temp)
#         stats[temp] = {}
#         for voltage in mode.voltages:
#             stats[temp][voltage] = {}
#             if limits:
#                 lower_limit, upper_limit = get_limits_at_mode_temp_voltage(limits, mode, temp, voltage)
#             print('\n==> VOLTAGE AT', voltage, 'V')
#             for system in mode.systems:
#                 out_of_spec = ''
#                 sys_min, sys_max, mean, std = get_system_stats_at_mode_temp_voltage(system, mode, temp, voltage)
#                 print(system, 'MIN: '+str(sys_min), 'MAX: '+str(sys_max), 'MEAN: '+str(mean), 'STD: '+str(std))
#                 if limits:
#                     out_of_spec = check_if_out_of_spec(lower_limit, upper_limit, sys_min, sys_max)
#                     print('OUT OF SPEC: '+str(out_of_spec))
#                 stats[temp][voltage][system] = [sys_min, sys_max, mean, std, out_of_spec]
#     return stats




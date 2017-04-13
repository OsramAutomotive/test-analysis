#!/usr/bin/python3

from core.data.test_station import *
from core.plotting.plots import *
from core.histograms.histograms import *
from core.limits.limits_parser import *
from core.analysis.analysis import *


### ----------------- TESTING ---------------- ###
## Setup
#prepath = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\P552 MCA Headlamp\P552 MCA Aux\ADVPR\PV Aux"

#endpath = r"\\TL A&B\Initial Tri Temp FT\-40C rerun\Raw Data"
#endpath = r"\\TL A&B\LTO\Raw Data"
#endpath = r"\\TL E\HTEnd\HTEnd restart\Raw Data"
#endpath = r"\\TL A&B\PTC\Raw Data"
#endpath = r"\\TL A&B\Humidity\Raw Data"
#endpath = r"\\TL A&B\PTC\System 83 DRL-TURN issue\Troubleshooting testing\85C 9V DRL+TURN (DRL on B2 no Vsense)\Raw Data"
#endpath = "\\TL A&B\PTC\System 83 DRL-TURN issue\Troubleshooting testing\85C 9V DRL+TURN (B4 w Vsense)\Raw Data"
#endpath = r"\\TL A&B\PTC\System 83 DRL-TURN issue\Troubleshooting testing\90C 9V (full PTC FC cycle)\Raw Data"
#endpath = r"\\TL A&B\PTC\System 83 DRL-TURN issue\Troubleshooting testing\90C 9V (condensed PTC FC cycle)\Raw Data"
#endpath = r"\\TL A&B\Sys 83 troubleshooting\System 83 DRL-TURN issue\Troubleshooting testing\90C 9V 9.5V 10V\Raw Data"

#datapath = prepath + endpath
datapath = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\A1XC\DVPR\Thermal Cycle Profile Development\Raw Data\powered\B1 to B9"

#limits_file = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\P552 MCA Headlamp\P552 MCA Aux\ADVPR\PV Aux\Limits\P552 MCA PV AUX LIMITS.xlsx"
#limits_file = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\P552 MCA Headlamp\P552 MCA Aux\ADVPR\PV Aux\Limits\P552 MCA PV AUX LIMITS DRL on B2.xlsx"
limits_file = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\A1XC\DVPR\Limits\A1XC Limits.xlsx"
ws = "Sheet1"
limits = Limits(limits_file, ws)


## Build/Analysis
#test = TestStation(3456, datapath, 85)
#test = TestStation(256, datapath, 85)
#test = TestStation(3456, datapath, -40, 85)
#test = TestStation(3456, datapath, 45, 60)
test = TestStation(3456, datapath, 70)

plot_modes(test)
#make_mode_histograms(test, system_by_system=True, limits = limits.lim)
make_mode_histograms(test, system_by_system=False)
#web_plot_board_currents(test)
fill_stats(test, limits = limits)

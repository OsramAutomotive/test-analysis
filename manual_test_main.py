#!/usr/bin/python3

from core.data.test_station import *
from core.plotting.plots import *
from core.histograms.histograms import *
from core.limits.limits_parser import *
from core.analysis.analysis import *


### ----------------- TESTING ---------------- ###
## Setup
datapath = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\P552 MCA Headlamp\P552 MCA Aux\ADVPR\PV Aux\TL A&B\PTC\Raw Data"

limits_file = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\P552 MCA Headlamp\P552 MCA Aux\ADVPR\PV Aux\Limits\P552 MCA PV AUX LIMITS.xlsx"
#limits_file = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\P552 MCA Headlamp\P552 MCA Aux\ADVPR\PV Aux\Limits\P552 MCA PV AUX LIMITS DRL on B2.xlsx"
#limits_file = r"\\Chfile1\ecs_landrive\Automotive_Lighting\LED\A1XC\DVPR\Limits\A1XC Limits.xlsx"
ws = "Sheet1"
limits = Limits(limits_file, ws)


## Build/Analysis
test = TestStation(3456, datapath, limits, -40, 85)

#plot_modes(test)
#make_mode_histograms(test, system_by_system=True, limits = limits.lim)
#make_mode_histograms(test, system_by_system=True)
#web_plot_board_currents(test)
fill_stats(test, limits = limits)

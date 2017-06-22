#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from core.data_import.test_station import *
from core.analysis.plots import *
from core.analysis.histograms import *
from core.analysis.tables import *
from core.limits.limits import *

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


## constants for user input parameters
TEMPERATURES = ['-40C', '23C', '45C', '60C', '70C', '85C']
BOARDS = ['B1','B2','B3','B4','B5','B6']
ANALYSIS_TOOLS = ['Plot', 'Histograms', 'Tables', 'Out of Spec']
PLOT_INFO = 'Create a temporal plot of the selected test'
HIST_INFO = 'Plot current histograms at each temp/mode/voltage'
TABLE_INFO = 'Generate an excel file with basic stats for each DUT at each temp/mode/voltage'
OUT_OF_SPEC_INFO = 'Generate a file containing only raw data that was out of spec'
ANALYSIS_TOOLTIP_INFO = [PLOT_INFO, HIST_INFO, TABLE_INFO, OUT_OF_SPEC_INFO]
DEFAULT_TEMP_TOL = 5
DEFAULT_VOLTAGE_TOL = 0.5
DEFAULT_PCTG_TOL = 10

TEXTFIELD_WIDTH = max(len(TEMPERATURES), len(BOARDS))
SELECT_WIDTH = 120
CELL_WIDTH = 50
TOL_WIDTH = 5

class TestAnalysisUI(QWidget):

    def __init__(self):
        super().__init__()
        self.test_name = ''
        self.data_folder = ''
        self.limits_file = ''
        self.temp_buttons = []
        self.board_buttons = []
        self.analysis_buttons = []
        self.stylesheet = 'styles\style_blue.qss'
        self.width = 800
        self.height = 380
        self.init_ui()

    def init_ui(self):
        ## use grid layout for GUI
        grid = QGridLayout()
        self.setLayout(grid)
        grid.setSpacing(10)  # spacing between widgets

        ## data folder
        self.data_folder_textfield = QLineEdit('(No Folder Selected)', self)
        self.data_folder_button = FolderButton('Select Data Folder', self.data_folder_textfield, self)
        grid.addWidget(self.data_folder_button, 0, 0)
        grid.addWidget(self.data_folder_textfield, 0, 1, 1, TEXTFIELD_WIDTH)

        ## limits
        self.limits_textfield = QLineEdit('(Leave blank if no limits)', self)
        self.limits_button = LimitsButton('Select Limits File', self.limits_textfield, self)
        grid.addWidget(self.limits_button, 1, 0)
        grid.addWidget(self.limits_textfield, 1, 1, 1, TEXTFIELD_WIDTH)

        ## temperature/board/analysis buttons
        self.temp_buttons = self.populate_buttons(grid, 2, 'Temperatures:', TempButton, TEMPERATURES)
        self.board_buttons = self.populate_buttons(grid, 3, 'Boards:', DataButton, BOARDS) 
        self.analysis_buttons = self.populate_buttons(grid, 4, 'Analysis:', ToolTipButton, ANALYSIS_TOOLS, info=ANALYSIS_TOOLTIP_INFO)

        ## analysis conditions
        self.conditions_label = QLabel('Conditions:')
        grid.addWidget(self.conditions_label, 5, 0, 1, 1)
        self.multimode_box = QCheckBox('Multimode')
        grid.addWidget(self.multimode_box, 5, 1, 1, 1)
        self.limit_analysis_box = QCheckBox('Limit Analysis')
        grid.addWidget(self.limit_analysis_box, 5, 2, 1, 1)
        self.raw_merge_box = QCheckBox('Raw Merge')
        grid.addWidget(self.raw_merge_box, 5, 3, 1, 1)        
        self.hist_by_tp_box = QCheckBox('Hists by TP')
        grid.addWidget(self.hist_by_tp_box, 5, 4, 1, 1)   

        ## tolerances
        self.tolerances_label = QLabel('Tolerances:')
        grid.addWidget(self.tolerances_label, 6, 0, 1, 1)

        self.temp_tol_label = QLabel('Temperature (C)')
        self.temp_tol_label.setAlignment(Qt.AlignBottom)
        self.temp_tol_field = QLineEdit('5', self)
        self.temp_tol_field.setFixedWidth(TOL_WIDTH)
        self.temp_tol_field.setValidator(QDoubleValidator())
        temp_tol_layout = QVBoxLayout()
        temp_tol_layout.addWidget(self.temp_tol_label)
        temp_tol_layout.addWidget(self.temp_tol_field)
        grid.addLayout(temp_tol_layout, 6, 1, 1, 1)

        self.voltage_tol_label = QLabel('Voltage (V)')
        self.voltage_tol_label.setAlignment(Qt.AlignBottom)
        self.voltage_tol_field = QLineEdit('0.5', self)
        self.voltage_tol_field.setFixedWidth(TOL_WIDTH)
        self.voltage_tol_field.setValidator(QDoubleValidator())
        voltage_tol_layout = QVBoxLayout()
        voltage_tol_layout.addWidget(self.voltage_tol_label)
        voltage_tol_layout.addWidget(self.voltage_tol_field)
        grid.addLayout(voltage_tol_layout, 6, 2, 1, 1)

        self.pctg_tol_label = QLabel('Percentage (%)')
        self.pctg_tol_label.setAlignment(Qt.AlignBottom)
        self.pctg_tol_field = QLineEdit('10', self)
        self.pctg_tol_field.setFixedWidth(TOL_WIDTH)
        self.pctg_tol_field.setValidator(QIntValidator())
        pctg_tol_layout = QVBoxLayout()
        pctg_tol_layout.addWidget(self.pctg_tol_label)
        pctg_tol_layout.addWidget(self.pctg_tol_field)
        grid.addLayout(pctg_tol_layout, 6, 3, 1, 1)

        ## test name
        grid.addWidget(QLabel('Test Name:'), 7, 0)
        self.test_name = QLineEdit('', self)
        grid.addWidget(self.test_name, 7, 1, 1, TEXTFIELD_WIDTH)

        ## analyze button
        self.analyze_button = AnalyzeButton('Analyze', self)
        grid.addWidget(self.analyze_button, 8, 2, 1, 3)

        ## gui window properties
        self.setStyleSheet(open(self.stylesheet, "r").read())
        self.setWindowTitle('Automotive Testing Data Analysis')
        self.setWindowIcon(QIcon('images\car.png'))
        self.move(300, 150) # center window
        self.resize(self.width, self.height)
        self.show()

    def populate_buttons(self, grid, row, label, button_type, text_list, info=None):
        ''' Populates button list onto GUI '''
        grid.addWidget(QLabel(label), row, 0)
        button_list = []
        positions = [(row, j+1) for j in range(len(text_list))]
        info_index = 0
        for position, text in zip(positions, text_list):
            if info:
                button = button_type(self, text, info[info_index])
            else:
                button = button_type(self, text)
            grid.addWidget(button, *position)
            button.setFixedWidth(CELL_WIDTH)
            button_list.append(button)
            info_index += 1
        return button_list


class FolderButton(QPushButton):

    def __init__(self, text, text_box, ui):
        super().__init__()
        self.ui = ui
        self.setText(text)
        self.setFixedWidth(SELECT_WIDTH)
        self.text_box = text_box
        self.name = r''
        self.clicked.connect(self.set_folder)
        self.setToolTip('Select the directory containing the raw data of the test you would like to analyze')

    def set_folder(self):
        self.name = str(QFileDialog.getExistingDirectory(self, "Select directory for data analysis"))
        self.text_box.setText(self.name)
        self.ui.data_folder = self.name


class LimitsButton(QPushButton):

    def __init__(self, text, text_box, ui):
        super().__init__()
        self.ui = ui
        self.setText(text)
        self.setFixedWidth(SELECT_WIDTH)
        self.text_box = text_box
        self.name = ''
        self.clicked.connect(self.set_limits)
        self.setToolTip('If doing limit analysis, select the appropriate product and rev limits file')

    def set_limits(self):
        self.name = str(QFileDialog.getOpenFileName(self, "Select limits file to use for data analysis")[0])
        self.text_box.setText(self.name)
        self.ui.limits_file = self.name


class DataButton(QPushButton):

    def __init__(self, ui, name):
        super().__init__()
        self.init_button(name)

    def init_button(self, name):
        self.setText(name)
        self.name = name
        self.setCheckable(True)
        self.pressed = False
        self.clicked[bool].connect(self.toggle)

    def toggle(self):
        self.pressed = not self.pressed
        if self.pressed:
            self.setStyleSheet('background-color: #9ACD32') # yellowgreen when pressed
        else:
            self.setStyleSheet('background-color: None')

class TempButton(DataButton):

    def __init__(self, ui, name):
        super().__init__(ui, name)
        self.init_temp()

    def init_temp(self):
        self.temp = int(self.name[:-1])


class ToolTipButton(DataButton):

    def __init__(self, ui, name, info):
        super().__init__(ui, name)
        self.init_tool(info)

    def init_tool(self, info):
        self.setToolTip(info)


class AnalyzeButton(QPushButton):
    
    def __init__(self, name, ui):
        super().__init__()
        self.init_button(name)
        self.ui = ui

    def init_button(self, name):
        self.setText(name)
        self.name = name
        self.clicked[bool].connect(self.analyze)

    def analyze(self):
        test, limits = None, None ## clear test objects (from prevoius usage)
        test_name = self.ui.test_name.text()
        temps = [t.temp for t in self.ui.temp_buttons if t.pressed]
        boards = [b.name for b in self.ui.board_buttons if b.pressed]
        datapath = self.ui.data_folder
        limits = self.load_limits(boards, temps)
        run_limit_analysis = self.ui.limit_analysis_box.isChecked()
        multimode = self.ui.multimode_box.isChecked()
        raw_merge = self.ui.raw_merge_box.isChecked()
        hists_by_tp = self.ui.hist_by_tp_box.isChecked()
        temperature_tolerance = float(self.ui.temp_tol_field.text())
        voltage_tolerance = float(self.ui.voltage_tol_field.text())
        percent_multiplier = int(self.ui.pctg_tol_field.text())/100.0  ## e.g. - 10% altered to 0.10

        if boards and temps and datapath:
            self.print_test_conditions(test_name, temps, boards, limits, temperature_tolerance, voltage_tolerance)
            test = TestStation(test_name, boards, datapath, limits, run_limit_analysis, multimode, *temps)
            for analysis_type in self.ui.analysis_buttons:
                if analysis_type.pressed:
                    self.run_analysis(analysis_type.name, test, limits, hists_by_tp)
            if raw_merge:
                test.mdf.to_csv(r'!output/'+'raw_data_all_boards.txt', header=test.mdf.columns,
                                index=True, sep='\t', mode='w')
            print('\n\n\n ==> Analysis complete.')
            try:
                plt.show()
            except:
                print('There are no plots to show')
        else:
            print('\nYou must select a data folder, temperatures, and test boards')

    def print_test_conditions(self, test_name, temps, boards, limits, temperature_tolerance, voltage_tolerance):
        print('\nTest Name:', test_name)
        print('Data Folder:', self.ui.data_folder)
        print('Temperatures:', temps)
        print('Boards:', boards, '\n')
        print('Temp Tolerance:', temperature_tolerance)
        print('Voltage Tolerance:', voltage_tolerance)
        print('Limits File:', self.ui.limits_file)
        if limits:
            limits.print_info()

    def run_analysis(self, analysis_name, test, limits, hists_by_tp):
        if analysis_name == 'Plot':
            plot_modes(test)
        elif analysis_name == 'Histograms':
            make_mode_histograms(test, system_by_system=hists_by_tp, limits=limits)
        elif analysis_name == 'Tables':
            fill_stats(test, limits, write_to_excel=True)
        elif analysis_name == 'Out of Spec':
            for mode in test.modes:
                if limits:
                    mode.get_out_of_spec_data()
        else:
            print('Analysis tool not found')

    def load_limits(self, boards, temps):
        if self.ui.limits_file:
            return Limits(self.ui.limits_file, 'Sheet1', BOARDS, temps)
        else:
            return None


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    gui = TestAnalysisUI()
    sys.exit(app.exec_())

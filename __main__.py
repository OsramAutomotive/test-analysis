#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from core.data.test_station import *
from core.plotting.plots import *
from core.histograms.histograms import *
from core.limits.limits_parser import *
from core.analysis.analysis import *

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from random import randint


class TestAnalysisUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.test_name = ''
        self.data_folder = ''
        self.limits_file = ''
        self.temp_buttons = []
        self.board_buttons = []
        self.analysis_buttons = []
        self.init_ui()

    def init_ui(self):
        grid = QGridLayout()
        self.setLayout(grid)
        grid.setSpacing(10)

        order = [self.data_folder, self.limits_file, self.temp_buttons, self.board_buttons] # dynamic row order?

        ## data folder
        self.data_folder_text_box = QLineEdit('(No Folder Selected)', self)
        self.data_folder_button = FolderButton('Select Data Folder', self.data_folder_text_box, self)
        grid.addWidget(self.data_folder_button, 0, 0)
        grid.addWidget(self.data_folder_text_box, 0, 1, 1, 6)

        ## limits
        self.limits_text_box = QLineEdit('(Leave blank if no limits)', self)
        self.limits_button = LimitsButton('Select Limits File', self.limits_text_box, self)
        grid.addWidget(self.limits_button, 1, 0)
        grid.addWidget(self.limits_text_box, 1, 1, 1, 6)

        ## temperature/board/analysis buttons
        self.temp_buttons = self.populate_buttons('Temperatures:', TempButton, ['-40C', '23C', '45C', '60C', '85C'], 2, grid)
        self.board_buttons = self.populate_buttons('Boards:', DataButton, ['B1','B2','B3','B4','B5','B6'], 3, grid) 
        self.analysis_buttons = self.populate_buttons('Analysis:', DataButton, ['Plot', 'Histograms', 'Tables'], 4, grid)

        ## test name
        grid.addWidget(QLabel('Test Name:'), 5, 0)
        self.test_name = QLineEdit('', self)
        grid.addWidget(self.test_name, 5, 1, 1, 6)

        ## analyze button
        self.analyze_button = AnalyzeButton('Analyze', self)
        grid.addWidget(self.analyze_button, 6, 2, 1, 3)

        ## gui window properties
        self.move(300, 150) # center window
        self.setWindowTitle('Automotive Testing Data Analysis')
        self.setWindowIcon(QIcon('images\car.png'))
        self.show()

    def populate_buttons(self, label, button_type, text_list, row, grid):
        grid.addWidget(QLabel(label), row, 0)
        button_list = []
        positions = [(row, j+1) for j in range(len(text_list))]
        for position, text in zip(positions, text_list):
            button = button_type(text, self)
            grid.addWidget(button, *position)
            button_list.append(button)
        return button_list

    def get_row(self, widget):
        ''' Idea (not implemented): get row for passed widget or widget group '''
        pass


class FolderButton(QPushButton):

    def __init__(self, text, text_box, ui):
        super().__init__()
        self.ui = ui
        self.setText(text)
        self.text_box = text_box
        self.name = ''
        self.clicked.connect(self.set_folder)

    def set_folder(self):
        self.name = str(QFileDialog.getExistingDirectory(self, "Select directory for data analysis"))
        self.text_box.setText(self.name)
        self.ui.data_folder = self.name


class LimitsButton(QPushButton):

    def __init__(self, text, text_box, ui):
        super().__init__()
        self.ui = ui
        self.setText(text)
        self.text_box = text_box
        self.name = ''
        self.clicked.connect(self.set_limits)

    def set_limits(self):
        self.name = str(QFileDialog.getOpenFileName(self, "Select limits file to use for data analysis")[0])
        self.text_box.setText(self.name)
        self.ui.limits_file = self.name


class DataButton(QPushButton):
    
    def __init__(self, name, ui):
        super().__init__()
        self.init_button(name)
    
    def init_button(self, name):
        self.setText(name)
        self.name = name
        self.pressed = False
        self.setCheckable(True)
        self.clicked[bool].connect(self.toggle)

    def toggle(self):
        self.pressed = not self.pressed
        if self.pressed:
            self.setStyleSheet('background-color: green; color: green;')
        else:
            self.setStyleSheet('background-color: None; color: None;')


class TempButton(DataButton):

    def __init__(self, name, ui):
        super().__init__(name, ui)
        self.init_temp()

    def init_temp(self):
        self.temp = int(self.name[:-1])


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
        test_name = self.ui.test_name.text()
        temps = [t.temp for t in self.ui.temp_buttons if t.pressed]
        boards = [b.name for b in self.ui.board_buttons if b.pressed]
        datapath = self.ui.data_folder
        limits = self.load_limits()     
       
        if boards and temps and datapath:
            self.print_test_conditions(test_name, temps, boards)
            test = TestStation(boards, datapath, limits, *temps)
            for analysis_type in self.ui.analysis_buttons:
                if analysis_type.pressed:
                    self.run_analysis(analysis_type.name, test, limits)
        else:
            print('You must select a data folder, temperatures, and test boards')

    def print_test_conditions(self, test_name, temps, boards):
        print('\nTest Name:', test_name)
        print('Data Folder:', self.ui.data_folder)
        print('Limits File:', self.ui.limits_file)
        print('Temperatures:', temps)
        print('Boards:', boards, '\n')

    def run_analysis(self, analysis_name, test, limits):
        if analysis_name == 'Plot':
            plot_modes(test)
        elif analysis_name == 'Histograms':
            make_mode_histograms(test, system_by_system=False, limits=limits)
        elif analysis_name == 'Tables':
            fill_stats(test, limits)

    def load_limits(self):
        if self.ui.limits_file:
            return Limits(self.ui.limits_file, 'Sheet1')
        else:
            return None


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    gui = TestAnalysisUI()
    sys.exit(app.exec_())

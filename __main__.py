#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *

class Example(QWidget):
    
    def __init__(self):
        super().__init__()
        self.data_folder = ''
        self.limits_file = ''
        self.temp_buttons = []
        self.board_buttons = []
        self.init_ui()

    def init_ui(self):      
        grid = QGridLayout()
        self.setLayout(grid)
        grid.setSpacing(10)

        order = [self.data_folder, self.limits_file, self.temp_buttons, self.board_buttons]

        self.data_folder_label = QLabel('(No folder selected)', self)
        self.data_folder_button = FolderButton('Select Data Folder', self.data_folder_label, self)
        grid.addWidget(self.data_folder_button, 0, 0)
        grid.addWidget(self.data_folder_label, 0, 1)

        self.limits_label = QLabel('(No folder selected)', self)
        self.limits_button = FolderButton('Select Data Folder', self.data_folder_label, self)
        grid.addWidget(self.data_folder_button, 0, 0)
        grid.addWidget(self.data_folder_label, 0, 1)

        self.temp_buttons = self.populate_buttons(DataButton, ['-40C', '23C', '85C'], 1, grid)
        self.board_buttons = self.populate_buttons(DataButton, ['B1','B2','B3','B4','B5','B6'], 2, grid) 

        self.move(300, 150) # center window
        self.setWindowTitle('Testing...')
        self.show()


    def populate_buttons(self, button_type, text_list, row, grid):
        button_list = []
        positions = [(row, j) for j in range(len(text_list))]
        for position, text in zip(positions, text_list):
            button = button_type(text, self)
            grid.addWidget(button, *position)
            button_list.append(button)
        return button_list

    def get_row(self, widget):
        ''' Idea: get row for passed widget or widget group '''
        pass


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


class FolderButton(QPushButton):

    def __init__(self, text, label, ui):
        super().__init__()
        self.setText(text)
        self.label = label
        self.name = ''
        self.clicked.connect(self.pressed)

    def pressed(self):
        self.name = str(QFileDialog.getExistingDirectory(self, "Select Directory for Data Analysis"))
        self.label.setText(self.name)


class LimitsButton(QPushButton):

''' do this instead:
http://stackoverflow.com/questions/31728253/pyqt-open-file-dialog-display-path-name
'''

    def __init__(self, text, label, ui):
        super().__init__()
        self.setText(text)
        self.label = label
        self.name = ''
        self.clicked.connect(self.pressed)

    def pressed(self):
        self.name = str(QFileDialog.getExistingDirectory(self, "Select Directory for Data Analysis"))
        self.label.setText(self.name)


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

#!/usr/bin/python3
# -*- coding: utf-8 -*-

from core.data.test_station import *
from core.plotting.plots import *
from core.histograms.histograms import *
from core.tables.excel_write import *
from core.limits.limits import *

import sys
from multiprocessing import Queue
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


## constants for user input parameters
TEMPERATURES = ['-40C', '23C', '45C', '60C', '70C', '85C']
BOARDS = ['B1','B2','B3','B4','B5','B6']
ANALYSIS_TOOLS = ['Plot', 'Histograms', 'Tables', 'Out of Spec']
PLOT_INFO = 'Create a temporal plot of the selected test'
HIST_INFO = 'Plot current histograms at each temp/mode/voltage'
TABLE_INFO = 'Generate an excel file with basic stats for each DUT at each temp/mode/voltage'
OUT_OF_SPEC_INFO = 'Generate a file containing only raw data that was out of spec'
ANALYSIS_TOOLTIP_INFO = [PLOT_INFO, HIST_INFO, TABLE_INFO, OUT_OF_SPEC_INFO]

TEXTFIELD_WIDTH = max(len(TEMPERATURES), len(BOARDS))
STYLESHEET = 'styles\style_blue.qss'

class TestAnalysisUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.test_name = ''
        self.data_folder = ''
        self.limits_file = ''
        self.temp_buttons = []
        self.board_buttons = []
        self.analysis_buttons = []
        self.width = 1000
        self.height = 500
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

        ## test name
        grid.addWidget(QLabel('Test Name:'), 5, 0)
        self.test_name = QLineEdit('', self)
        grid.addWidget(self.test_name, 5, 1, 1, TEXTFIELD_WIDTH)
        
        ## analyze button
        self.analyze_button = AnalyzeButton('Analyze', self)
        self.analyze_button.clicked.connect(self.start_thread)
        grid.addWidget(self.analyze_button, 6, 2, 1, 3)

        ## text stream (stdout)
        self.textedit = QTextEdit()
        grid.addWidget(self.textedit, 7, 0, 5, TEXTFIELD_WIDTH+1)

        ## gui window properties
        self.setStyleSheet(open(STYLESHEET, "r").read())
        self.setWindowTitle('Automotive Testing Data Analysis')
        self.setWindowIcon(QIcon('images\car.png'))
        self.move(300, 150) # center window
        self.resize(self.width, self.height)
        self.show()

    @pyqtSlot(str)
    def append_text(self, text):
        self.textedit.moveCursor(QTextCursor.End)
        self.textedit.insertPlainText(text)

    @pyqtSlot()
    def start_thread(self):
        self.thread = QThread()
        self.analysis = Analysis(self)
        self.analysis.moveToThread(self.thread)
        self.thread.started.connect(self.analysis.analyze)
        self.thread.start()

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
            button_list.append(button)
            info_index += 1
        return button_list


class FolderButton(QPushButton):

    def __init__(self, text, text_box, ui):
        super().__init__()
        self.ui = ui
        self.setText(text)
        self.text_box = text_box
        self.name = ''
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
        self.pressed = False
        self.setCheckable(True)
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
        #self.clicked[bool].connect(self.analyze)


class Analysis(QObject):

    def __init__(self, ui):
        super().__init__()
        self.ui = ui

    @pyqtSlot()
    def print_stuff(self):
        test_name = self.ui.test_name.text()
        temps = [t.temp for t in self.ui.temp_buttons if t.pressed]
        boards = [b.name for b in self.ui.board_buttons if b.pressed]
        datapath = self.ui.data_folder
        
        print('\nTest Name:', test_name)
        print('Data Folder:', self.ui.data_folder)
        print('Temperatures:', temps)
        print('Boards:', boards, '\n')
        print('Limits File:', self.ui.limits_file)
    
    @pyqtSlot()
    def analyze(self):
        test_name = self.ui.test_name.text()
        temps = [t.temp for t in self.ui.temp_buttons if t.pressed]
        boards = [b.name for b in self.ui.board_buttons if b.pressed]
        datapath = self.ui.data_folder
        limits = load_limits(boards, temps)

        if boards and temps and datapath:
            self.print_test_conditions(test_name, temps, boards, limits)
            test = TestStation(test_name, boards, datapath, limits, *temps)
            out_of_spec_true = self.write_out_of_spec_true()
            for analysis_type in self.ui.analysis_buttons:
                if analysis_type.pressed:
                    if out_of_spec_true:
                        self.run_analysis(analysis_type.name, test, limits, write_out_of_spec=True)
                    else:
                        self.run_analysis(analysis_type.name, test, limits, write_out_of_spec=False)
        else:
            print('\nYou must select a data folder, temperatures, and test boards')

    @pyqtSlot()
    def load_limits(self, boards, temps):
        if self.ui.limits_file:
            return Limits(self.ui.limits_file, 'Sheet1', BOARDS, temps)
        else:
            return None

    @pyqtSlot()
    def write_out_of_spec_true(self):
        return any( (button.name=='Out of Spec' and button.pressed) for button in self.ui.analysis_buttons )

    @pyqtSlot()
    def print_test_conditions(self, test_name, temps, boards, limits):
        print('\nTest Name:', test_name)
        print('Data Folder:', self.ui.data_folder)
        print('Temperatures:', temps)
        print('Boards:', boards, '\n')
        print('Limits File:', self.ui.limits_file)
        if limits:
            limits.print_info()

    @pyqtSlot()
    def run_analysis(self, analysis_name, test, limits, write_out_of_spec=False):
        if analysis_name == 'Plot':
            plot_modes(test)
        elif analysis_name == 'Histograms':
            make_mode_histograms(test, system_by_system=False, limits=limits)
        elif analysis_name == 'Tables':
            fill_stats(test, limits, write_to_excel=True, write_out_of_spec=write_out_of_spec)
        elif analysis_name == 'Out of Spec':
            pass
        else:
            print('Analysis tool not found')



# The new Stream Object which replaces the default stream associated with sys.stdout
# This object just puts data in a queue!
class WriteStream(object):
    def __init__(self,queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

# A QObject (to be run in a QThread) which sits waiting for data to come through a Queue.Queue().
# It blocks until data is available, and one it has got something from the queue, it sends
# it to the "MainThread" by emitting a Qt Signal 
class MyReceiver(QObject):
    mysignal = pyqtSignal(str)

    def __init__(self,queue,*args,**kwargs):
        QObject.__init__(self,*args,**kwargs)
        self.queue = queue

    @pyqtSlot()
    def run(self):
        while True:
            text = self.queue.get()
            self.mysignal.emit(text)


# Create Queue and redirect sys.stdout to this queue
queue = Queue()
sys.stdout = WriteStream(queue)

# Create QApplication and QWidget
app = QApplication(sys.argv)
gui = TestAnalysisUI()
gui.show()

# Create thread that will listen on the other end of the queue, and send the text to the textedit in our application
thread = QThread()
my_receiver = MyReceiver(queue)
my_receiver.mysignal.connect(gui.append_text)
my_receiver.moveToThread(thread)
thread.started.connect(my_receiver.run)
thread.start()

app.exec_()

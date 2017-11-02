
from bs4 import BeautifulSoup
import pprint as pp

class Limits(object):
    def __init__(self, filepath, boards, temps):
        self.filepath = filepath
        self.boards = boards  # e.g. - 'B1' or 'B4'
        self.temps = temps  # integers, e.g. - 85 or -40 or 23

        self.lim = {} # holds current limits {MODE->TEMP->VOLTAGE->(min current, max current)}
        self.soup = ''
        self.modules = []  # e.g. - 'PARK' or 'TURN'
        self.board_module_pairs = {}  # keys: boards; values: modules
        self.outage_link_board = ''
        self.outage_present = False
        self.binning = False
        self.led_binning_dict = {}

        self.set_soup()
        self.get_board_info()
        self.get_limits()

    def set_soup(self):
        with open(self.filepath) as fp:
            self.soup = BeautifulSoup(fp, 'lxml')

    def get_board_info(self):
        board_rows = self.soup.find_all(class_='board')
        for board_row in board_rows:
            data = board_row.find_all('td')
            board = data[0].string
            module = data[1].string
            led_bins = data[2].string
            has_outage = data[3].string
            self.board_module_pairs[board] = module
            self.modules.append(module)
            if led_bins:
                self.binning = True
                self.led_binning_dict[board] = led_bins.split(' ')
            if has_outage == 'YES':
                self.outage_link_board = board
                self.outage_present = True

    def get_limits(self):
        modes = self.soup.find_all(class_='mode')
        for mode in modes:
            self._get_mode_limits(mode)
        if 'OUTAGE' in self.modules:
            self._get_outage_limits()

    def _get_mode_limits(self, mode):
        mode_id = mode.get('id')
        self.lim[mode_id] = {}
        temp_tables = mode.find_all(class_='temp-table')
        for temp_table in temp_tables:
            temp = temp_table.get('class')[-1].replace('temp', '')
            temp = int(temp.replace('C', ''))
            self.lim[mode_id][temp] = {}
            voltage_rows = temp_table.find_all(lambda tag: tag.get('id')=='voltage')
            for voltage_row in voltage_rows:
                voltage = round(float(voltage_row.get('class')[0]), 1);
                minimum = round(float(voltage_row.find(class_='min').string), 3)
                maximum = round(float(voltage_row.find(class_='max').string), 3)
                self.lim[mode_id][temp][voltage] = (minimum, maximum)

    def _get_outage_limits(self):
        outage_tables = self.soup.find_all(class_='outage-table')
        self.lim['OUTAGE'] = {}
        for outage_table in outage_tables:
            outage_state = outage_table.get('state')
            self.lim['OUTAGE'][outage_state] = {}
            voltage_rows = outage_table.find_all(lambda tag: tag.get('id')=='voltage')
            for voltage_row in voltage_rows:
                voltage = round(float(voltage_row.get('class')[0]), 1);
                minimum = round(float(voltage_row.find(class_='min').string), 3)
                maximum = round(float(voltage_row.find(class_='max').string), 3)
                self.lim['OUTAGE'][outage_state][voltage] = (minimum, maximum)

    def print_info(self):
        print('\n*** Limits Details ***')
        print('\nBoard-Module Pairs:')
        pp.pprint(self.board_module_pairs)
        print('\nCurrent Limits:')
        pp.pprint(self.lim)
        print('\n')


# filepath = r"C:\Users\bruno\Desktop\mca-with-outage.htm"
# boards = ['B3', 'B4', 'B5', 'B6']
# temps = [23]
# limits = Limits(filepath, boards, temps)

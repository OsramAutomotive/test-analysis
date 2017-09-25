
from bs4 import BeautifulSoup
import pprint as pp

class Limits(object):
    def __init__(self, filepath, boards, temps):
        self.filepath = filepath
        self.boards = boards  # e.g. - 'B1' or 'B4'
        self.temps = temps  # integers, e.g. - 85 or -40 or 23

        self.lim = {} # holds current limits
        self.soup = ''
        self.modules = []  # e.g. - 'PARK' or 'TURN'
        self.module_modes = []  # e.g. - 'DRLTURN' or 'PARK'
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
            if has_outage:
                self.outage_link_board = board
                self.outage_present = True

    def get_limits(self):
        modes = self.soup.find_all(class_='mode')
        for mode in modes:
            self.get_mode_limits(mode)

    def get_mode_limits(self, mode):
        mode_id = mode.get('id')
        print('\n', mode_id)
        self.lim[mode_id] = {}
        temp_tables = mode.find_all(class_='temp-table')
        for temp_table in temp_tables:
            temp = temp_table.get('class')[-1].replace('temp', '')
            temp = int(temp.replace('C', ''))
            print('Temperature: ', temp)
            self.lim[mode_id][temp] = {}
            voltage_rows = temp_table.find_all(lambda tag: tag.get('id')=='voltage')
            for voltage_row in voltage_rows:
                voltage = round(float(voltage_row.get('class')[0]), 1);
                print(voltage)
                print('min value:', voltage_row.find(class_='min').string)
                minimum = round(float(voltage_row.find(class_='min').string), 3)
                maximum = round(float(voltage_row.find(class_='max').string), 3)
                self.lim[mode_id][temp][voltage] = (minimum, maximum)


    def print_info(self):
        pp.pprint(self.board_module_pairs)
        pp.pprint(self.lim)
        print('\n\n')


# limitspath = r"C:\Users\bruno\Programming Projects\Test Data Analysis\test files\test.htm"
# limits = Limits(limitspath, ['B3', 'B4', 'B5', 'B6'], [23, -40, 85])
# limitspath = r"C:\Users\bruno\Programming Projects\Test Data Analysis\test files\tesladv.htm"
# limits = Limits(limitspath, ['B2', 'B4', 'B5'], [23, -40, 85])

# pp.pprint(limits.board_module_pairs)
# print('\n')
# pp.pprint(limits.lim)


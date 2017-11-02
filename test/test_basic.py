import unittest
from random import randint
from core.data_import.helpers import *


class RemoveB6FromTests(unittest.TestCase):

    def testBoardsOneToSix(self):
        input_list = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']
        output_list = ['B1', 'B2', 'B3', 'B4', 'B5']
        self.assertEqual(copy_and_remove_b6_from(input_list), output_list)

    def testBoardsThreeToSix(self):
        input_list = ['B3', 'B4', 'B5', 'B6']
        output_list = ['B3', 'B4', 'B5']
        self.assertEqual(copy_and_remove_b6_from(input_list), output_list)

    def testHighBoards(self):
        input_list = ['B5', 'B6', 'B7', 'B8', 'B9', 'B10']
        output_list = ['B5', 'B7', 'B8', 'B9', 'B10']
        self.assertEqual(copy_and_remove_b6_from(input_list), output_list)


class GetSystemTestPositionIntTests(unittest.TestCase):

    def setUp(self):
        self.twenty_four_systems = []
        for i in range(1, 25):
            system = 'TP'+str(i)+': '+'System '+str(randint(1, 150))
            self.twenty_four_systems.append(system)

    def testTwentyFourSystems(self):
        for i, system in enumerate(self.twenty_four_systems):
            self.assertEqual(get_system_test_position_int(system), i+1)


def main():
    unittest.main(exit=False)

if __name__ == '__main__':
    main()
#!/usr/bin/python3

''' This module uses lxml to create xml tables with conditional formatting
for out of spec currents/voltages and color modes as well. '''

from core.data_import.mode import *
from core.data_import.board import *
from core.re_and_global import *
from lxml import etree
import webbrowser


def create_xml_tables(test, limits=None):
    ''' This function fills the mode objects with stats from test using mode method '''
    from lxml import etree
    xml_root = etree.Element("test", name=test.name, header_width=str(len(test.systems)))

    time_analysis = etree.SubElement(xml_root, "time")
    last_time_value = etree.SubElement(time_analysis, "timestamp")
    last_time_value.text = str(test.mdf.tail(1).index[0])

    temp_analysis = etree.SubElement(xml_root, "profile")
    for tc in test.thermocouples:
        thermocouple = etree.SubElement(temp_analysis, "thermocouple")
        name = etree.SubElement(thermocouple, "name")
        temp_minimum = etree.SubElement(thermocouple, "temp-min")
        temp_maximum = etree.SubElement(thermocouple, "temp-max")
        name.text = str(tc)
        temp_minimum.text = str(round(test.mdf[tc].min(), 2))
        temp_maximum.text = str(round(test.mdf[tc].max(), 2))

    for temp in test.temps:
        xml_temp = etree.SubElement(xml_root, "temperature", temp=str(temp)+'C')

        for mode in test.modes:
            print('\n\n\n*********', mode, '*********')
            mode.get_system_by_system_mode_stats(xml_temp, temp, limits)

    write_user_inputs(xml_root, test)

    xml_file = open(test.name + '.xml', 'w')
    xml_file.write(r'<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="data.xsl"?>')
    xml_file.close()

    with open(test.name +'.xml', 'a') as xml_file:
        xml_data = etree.tostring(xml_root, pretty_print=True, encoding='unicode')
        xml_file.write(xml_data)
        xml_file.close()

    webbrowser.open('file://' + os.path.realpath(test.name) + '.xml', new=0)


def write_user_inputs(xml_root, test):
    user_inputs = etree.SubElement(xml_root, "user-inputs")
    test_name = etree.SubElement(user_inputs, "test-name")
    folder = etree.SubElement(user_inputs, "folder")
    systems = etree.SubElement(user_inputs, "systems")
    limits_file = etree.SubElement(user_inputs, "limits-file")
    temperature_tolerance = etree.SubElement(user_inputs, "temperature-tolerance")
    voltage_tolerance = etree.SubElement(user_inputs, "voltage-tolerance")
    test_name.text = test.name
    folder.text = test.folder
    systems.text = ', '.join(test.systems)
    limits_file.text = test.limits.filepath
    temperature_tolerance.text = str(test.temperature_tolerance)
    voltage_tolerance.text = str(test.voltage_tolerance)
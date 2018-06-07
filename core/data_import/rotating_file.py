#!/usr/bin/python3

"""
This module contains the RotatingFile class which is used to log
out of spec raw data files. It handles the creation of a new file
when one become too large for instances where a test exhibits a
lot of out of spec data.
"""

import os
import sys

class RotatingFile(object):
    def __init__(self, directory='', filename='out_of_spec', max_files=99,
                 max_file_size=20000000):
        self.ii = 1
        self.directory, self.filename      = directory, filename
        self.max_file_size, self.max_files = max_file_size, max_files
        self.finished, self.fh             = False, None
        self.open()

    def rotate(self):
        """Rotate the file, if necessary"""
        if (os.stat(self.filename_template).st_size > self.max_file_size):
            self.close()
            self.ii += 1
            if (self.ii <= self.max_files):
                self.open()
            else:
                self.close()
                self.finished = True

    def open(self):
        self.fh = open(self.filename_template, 'a')

    def write(self, header, df):
        self.fh.write(header)
        df.to_csv(self.fh, header=df.columns, index=True, 
                  sep='\t', mode='a')
        self.fh.flush()
        self.rotate()

    def close(self):
        self.fh.close()

    @property
    def filename_template(self):
        return self.directory + self.filename + "_%0.2d.txt" % self.ii
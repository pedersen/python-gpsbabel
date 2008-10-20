"""
This module is is the main module for GPSBabel. It is intended to be a complete Python interface, allowing easy mechanisms to the developer to control GPSBabel from within a Python application.
"""
"""
Python-GPSBabel - Python wrapper for GPSBabel project
Copyright (C) 2008, Michael J. Pedersen <m.pedersen@icelus.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import subprocess

class GPSBabel(object):
    def __init__(self):
        gps = subprocess.Popen(["gpsbabel", "-V"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        version = gps.stdout.readlines()
        if version != ['\n', 'GPSBabel Version 1.3.5\n', '\n']:
            raise Exception('Unsupported version of GPSBabel installed. Aborting.')
        self.ftypes = {}
        self.filters = {}
        self.charsets = {}
        self.readOpts()
        self.infiles = {}
        self.outfiles = {}
        self.applyfilters = {}
        self.ini = ""
    
    def readOpts(self):
        ftype = ''
        gps = subprocess.Popen(["gpsbabel", "-h"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mode = 0 # 0 == do nothing, 1 == file type, 2 === filter
        for line in gps.stdout.readlines():
            line = line.rstrip()
            if line.strip() == 'File Types (-i and -o options):':
                mode = 1
                continue
            if line.strip() == 'Supported data filters:':
                mode = 2
                continue
            if mode == 0 or line.strip() == '':
                continue
            if mode == 1:
                if line.startswith('\t  '): # reading type option
                    line = line.strip()
                    self.ftypes[ftype].append(line[:line.find(' ')].strip())
                else: # reading type name
                    line = line.strip()
                    ftype = line[:line.find(' ')].strip()
                    self.ftypes[ftype] = []
            elif mode == 2:
                if line.startswith('\t '): # reading type option
                    line = line.strip()
                    self.filters[ftype].append(line[:line.find(' ')].strip())
                else: # reading type name
                    line = line.strip()
                    ftype = line[:line.find(' ')].strip()
                    self.filters[ftype] = []
        charset = ''
        gps = subprocess.Popen(["gpsbabel", "-l"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mode = 0 # 0 == do nothing, 1 == char set, 2 === char set alias
        for line in gps.stdout.readlines():
            line = line.rstrip()
            if line.startswith('*'):
                charset = line[line.find(' ')+1:]
                self.charsets[charset] = []
            if line.startswith('\t'):
                self.charsets[charset].extend(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), line.strip().split(','))))

if __name__ == "__main__":
    gps = GPSBabel()
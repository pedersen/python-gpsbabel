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

"""
@todo: Add full chain support, complete adding support for all options.
"""
import unittest
import os
import os.path

import gpsbabel

class GPSBabelTest(unittest.TestCase):
    def setUp(self):
        self.gps = gpsbabel.GPSBabel()
    
    def tearDown(self):
        del self.gps
        
    def testInit(self):
        self.failUnless(self.gps != None)
    
    def testClearChainOpts(self):
        self.failUnless(self.gps.ini == "")
        self.failUnless(self.gps.shortnames == False)
        self.failUnless(self.gps.procRoutes == False)
        self.failUnless(self.gps.procTrack  == False)
        self.failUnless(self.gps.procWpts   == False)
        self.failUnless(self.gps.procGps    == False)
        self.failUnless(self.gps.smartIcons == True)
        self.failUnless(self.gps.chain == [])
        
    def testReadOpts(self):
        self.failUnless(self.gps.ftypes["garmin"] != None)
        self.failUnless(self.gps.filters["transform"] != None)
        self.failUnless(self.gps.charsets["ISO-8859-1"] != None)
    
    def testAddActionInvalid(self):
        try:
            self.gps.addAction('invalid', 'gpx', {}, None)
            self.fail('No UnknownActionException Generated')
        except gpsbabel.UnknownActionException:
            pass
        
    def testAddActionFileInvalidFilename(self):
        try:
            self.gps.addAction('infile', 'gpx', {'foobarbaz': 'badoption'}, None)
            self.fail('No MissingFilenameException Generated')
        except gpsbabel.MissingFilenameException:
            pass
        
    def testAddActionFileInvalidFormat(self):
        try:
            self.gps.addAction('infile', 'foobarbaz', {}, 'filename')
            self.fail('No MissingFileFmtException Generated')
        except gpsbabel.MissingFilefmtException:
            pass
        
    def testAddActionFileInvalidOption(self):
        try:
            self.gps.addAction('infile', 'gpx', {'foobarbaz': 'badoption'}, 'filename')
            self.fail('No InvalidOptionException Generated')
        except gpsbabel.InvalidOptionException:
            pass
        
    def testAddActionFilterInvalidFilter(self):
        try:
            self.gps.addAction('filter', 'foobarbaz')
            self.fail('No MissingFilterException Generated')
        except gpsbabel.MissingFilterException:
            pass
        
    def testAddActionFilterInvalidOption(self):
        try:
            self.gps.addAction('filter', 'transform', {'foobarbaz' : 'invalid'})
            self.fail('No InvalidOptionException Generated')
        except gpsbabel.InvalidOptionException:
            pass
        
    def testAddActionCharsetInvalid(self):
        try:
            self.gps.addAction('charset', 'foobarbaz')
            self.fail('No UnknownCharsetException Generated')
        except gpsbabel.UnknownCharsetException:
            pass
        
    def testAddActionFileValid(self):
        self.gps.addAction('infile', 'gpx', {'snlen': 6}, 'filename')
        self.failUnless(len(self.gps.chain) == 1, "len(self.gps.chain) == %d" % len(self.gps.chain))
        
    def testAddActionFilterValid(self):
        self.gps.addAction('filter', 'simplify', {'count' : 6})
        self.failUnless(len(self.gps.chain) == 1, "len(self.gps.chain) == %d" % len(self.gps.chain))
        
    def testAddActionCharsetValidPrimary(self):
        self.gps.addAction('charset', 'ISO-8859-1')
        self.failUnless(len(self.gps.chain) == 1, "len(self.gps.chain) == %d" % len(self.gps.chain))
        
    def testAddActionCharsetValidAlias(self):
        self.gps.addAction('charset', 'Latin-1')
        self.failUnless(len(self.gps.chain) == 1, "len(self.gps.chain) == %d" % len(self.gps.chain))
        
    def testBuildCmd(self):
        self.gps.addAction('charset', 'ISO-8859-1')
        self.gps.addAction('infile', 'gpx', {}, '-')
        self.gps.addAction('filter', 'simplify', {'count' : 6})
        self.gps.addAction('outfile', 'gpx', {}, '-')
        self.failUnless(self.gps.buildCmd() == ['gpsbabel','-p','""','-c','ISO-8859-1','-i','gpx','-f','-','-x','simplify,count=6','-o','gpx','-F','-'])
                
    def testExecCmd(self):
        self.gps.addAction('charset', 'ISO-8859-1')
        self.gps.addAction('infile', 'gpx', {}, '-')
        self.gps.addAction('filter', 'simplify', {'count' : 6})
        self.gps.addAction('outfile', 'gpx', {}, '-')
        self.failUnless(self.gps.execCmd() == [])

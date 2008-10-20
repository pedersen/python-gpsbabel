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

class initTest(unittest.TestCase):
    def setUp(self):
        self.gps = gpsbabel.GPSBabel()
    
    def tearDown(self):
        del self.gps
        
    def testInit(self):
        self.failUnless(self.gps != None)
    
    def testReadOpts(self):
        self.failUnless(self.gps.ftypes["garmin"] != None)
        self.failUnless(self.gps.filters["transform"] != None)
        self.failUnless(self.gps.charsets["ISO-8859-1"] != None)
    
"""
    gpsbabel [options] -i INTYPE -f INFILE [filter] -o OUTTYPE -F OUTFILE
    gpsbabel [options] -i INTYPE -o OUTTYPE INFILE [filter] OUTFILE

Options:
    -p               Preferences file (gpsbabel.ini)
    -s               Synthesize shortnames
    -r               Process route information
    -t               Process track information
    -w               Process waypoint information [default]
    -x filtername    Invoke filter (placed between inputs and output) 
    -T               Process realtime tracking information
    -c               Character set for next operation
    -N               No smart icons on output
"""
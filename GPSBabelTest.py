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

import unittest
import os
import os.path

from decimal import Decimal

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
        self.failUnless(self.gps.smartIcons == True)
        self.failUnless(self.gps.chain == [])
        
    def testReadOpts(self):
        self.failUnless(gpsbabel.ftypes["garmin"] != None)
        self.failUnless(gpsbabel.filters["transform"] != None)
        self.failUnless(gpsbabel.charsets["ISO-8859-1"] != None)
    
    def testAddActionInvalid(self):
        try:
            self.gps.addAction('invalid', 'gpx', None, {})
            self.fail('No UnknownActionException Generated')
        except gpsbabel.UnknownActionException:
            pass
        
    def testAddActionFileInvalidFilename(self):
        try:
            self.gps.addAction('infile', 'gpx', None, {'foobarbaz': 'badoption'})
            self.fail('No MissingFilenameException Generated')
        except gpsbabel.MissingFilenameException:
            pass
        
    def testAddActionFileInvalidFormat(self):
        try:
            self.gps.addAction('infile', 'foobarbaz', 'filename', {})
            self.fail('No MissingFileFmtException Generated')
        except gpsbabel.MissingFilefmtException:
            pass
        
    def testAddActionFileInvalidOption(self):
        try:
            self.gps.addAction('infile', 'gpx', 'filename', {'foobarbaz': 'badoption'})
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
            self.gps.addAction('filter', 'transform', None, {'foobarbaz' : 'invalid'})
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
        self.gps.addAction('infile', 'gpx', 'filename', {'snlen': 6})
        self.failUnless(len(self.gps.chain) == 1, "len(self.gps.chain) == %d" % len(self.gps.chain))
        
    def testAddActionFilterValid(self):
        self.gps.addAction('filter', 'simplify', None, {'count' : 6})
        self.failUnless(len(self.gps.chain) == 1, "len(self.gps.chain) == %d" % len(self.gps.chain))
        
    def testAddActionCharsetValidPrimary(self):
        self.gps.addAction('charset', 'ISO-8859-1')
        self.failUnless(len(self.gps.chain) == 1, "len(self.gps.chain) == %d" % len(self.gps.chain))
        
    def testAddActionCharsetValidAlias(self):
        self.gps.addAction('charset', 'Latin-1')
        self.failUnless(len(self.gps.chain) == 1, "len(self.gps.chain) == %d" % len(self.gps.chain))
        
    def testBuildCmd(self):
        self.gps.addAction('charset', 'ISO-8859-1')
        self.gps.addAction('infile', 'gpx', '-', {})
        self.gps.addAction('filter', 'simplify', None, {'count' : 6})
        self.gps.addAction('outfile', 'gpx', '-', {})
        self.failUnless(self.gps.buildCmd() == ['gpsbabel','-p','','-c','ISO-8859-1','-i','gpx','-f','-','-x','simplify,count=6','-o','gpx','-F','-'])
                
    def testExecCmd(self):
        self.gps.addAction('charset', 'ISO-8859-1')
        self.gps.setInGpx('<?xml version="1.0" encoding="UTF-8"?><gpx version="1.0" creator="GPSBabel - http://www.gpsbabel.org" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd"><time>2008-10-22T18:20:22Z</time><bounds minlat="40.735149952" minlon="-75.099566588" maxlat="40.744316652" maxlon="-75.088833310"/><wpt lat="40.735149952" lon="-75.088833310"><ele>-0.114380</ele><name>GC187W</name><cmt>GC187W</cmt><desc>GC187W</desc><sym>Waypoint</sym></wpt></gpx>')
        self.gps.addAction('filter', 'simplify', None, {'count' : 6})
        self.gps.addAction('outfile', 'gpx', '-', {})
        ret, res = self.gps.execCmd(parseOutput = False)
        self.failUnless(ret == 0)
        
    def testExecCmdException(self):
        try:
            self.gps.execCmd([self.gps.gpsbabel, '-foobarbaz'], parseOutput=False)
            self.fail('No exception raised')
        except RuntimeError:
            pass
        
    def testGuessFormat(self):
        self.failUnless(self.gps.guessFormat("FILENAME.GPX") == "gpx")
        self.failUnless(self.gps.guessFormat("FILENAME.KML") == "kml")
        self.failUnless(self.gps.guessFormat("FILENAME.TXT") == "nmea")
        self.failUnless(self.gps.guessFormat("FILENAME.PDF") == None)
    
    def testGetFormats(self):
        self.failUnless(self.gps.getFormats(self.gps.FMT_INPUT,  self.gps.FMT_FILE)   == ["gpx", "nmea", "sbp"])
        self.failUnless(self.gps.getFormats(self.gps.FMT_OUTPUT, self.gps.FMT_FILE)   == ["gpx", "kml"])
        self.failUnless(self.gps.getFormats(self.gps.FMT_INPUT,  self.gps.FMT_DEVICE) == ["garmin", "navilink"])
        self.failUnless(self.gps.getFormats(self.gps.FMT_OUTPUT, self.gps.FMT_DEVICE) == ["garmin", "navilink"])
        self.failUnless(self.gps.getFormats(-1,  self.gps.FMT_DEVICE) == ["garmin", "navilink"])
        self.failUnless(self.gps.getFormats(self.gps.FMT_INPUT,  -1) == [])
        self.failUnless(self.gps.getFormats(self.gps.FMT_OUTPUT, -1) == [])
        
    def testAddInputFile(self):
        self.gps.addInputFile('-')
        self.failUnless(len(self.gps.chain) == 2)
        self.failUnless(self.gps.chain[0][0] == {'action':'charset', 'fname':None, 'fmtfilter':'UTF-8'})
        self.failUnless(self.gps.chain[0][1] == {})
        self.failUnless(self.gps.chain[1][0] == {'action':'infile', 'fname':'-', 'fmtfilter':'gpx'})
        self.failUnless(self.gps.chain[1][1] == {})
        
    def testAddInputFiles(self):
        files = {'-' : None, '-1' : [], '-2' : ['kml'], '-3' : ['kml', 'utf8']}
        self.gps.addInputFiles(files)
        self.failUnless(len(self.gps.chain) == 8)
        self.failUnless(self.gps.chain[0][0] == {'action':'charset', 'fname':None, 'fmtfilter':'UTF-8'})
        self.failUnless(self.gps.chain[0][1] == {})
        self.failUnless(self.gps.chain[1][0] == {'action':'infile', 'fname':'-', 'fmtfilter':'gpx'})
        self.failUnless(self.gps.chain[1][1] == {})
        self.failUnless(self.gps.chain[2][0] == {'action':'charset', 'fname':None, 'fmtfilter':'UTF-8'})
        self.failUnless(self.gps.chain[2][1] == {})
        self.failUnless(self.gps.chain[3][0] == {'action':'infile', 'fname':'-1', 'fmtfilter':'gpx'})
        self.failUnless(self.gps.chain[3][1] == {})
        self.failUnless(self.gps.chain[4][0] == {'action':'charset', 'fname':None, 'fmtfilter':'UTF-8'})
        self.failUnless(self.gps.chain[4][1] == {})
        self.failUnless(self.gps.chain[5][0] == {'action':'infile', 'fname':'-2', 'fmtfilter':'kml'})
        self.failUnless(self.gps.chain[5][1] == {})
        self.failUnless(self.gps.chain[6][0] == {'action':'charset', 'fname':None, 'fmtfilter':'utf8'})
        self.failUnless(self.gps.chain[6][1] == {})
        self.failUnless(self.gps.chain[7][0] == {'action':'infile', 'fname':'-3', 'fmtfilter':'kml'})
        self.failUnless(self.gps.chain[7][1] == {})
        
    def testAddOutputFiles(self):
        files = {'-' : None, '-1' : [], '-2' : ['kml'], '-3' : ['kml', 'utf8']}
        self.gps.addOutputFiles(files)
        self.failUnless(len(self.gps.chain) == 8)
        self.failUnless(self.gps.chain[0][0] == {'action':'charset', 'fname':None, 'fmtfilter':'UTF-8'})
        self.failUnless(self.gps.chain[0][1] == {})
        self.failUnless(self.gps.chain[1][0] == {'action':'outfile', 'fname':'-', 'fmtfilter':'gpx'})
        self.failUnless(self.gps.chain[1][1] == {})
        self.failUnless(self.gps.chain[2][0] == {'action':'charset', 'fname':None, 'fmtfilter':'UTF-8'})
        self.failUnless(self.gps.chain[2][1] == {})
        self.failUnless(self.gps.chain[3][0] == {'action':'outfile', 'fname':'-1', 'fmtfilter':'gpx'})
        self.failUnless(self.gps.chain[3][1] == {})
        self.failUnless(self.gps.chain[4][0] == {'action':'charset', 'fname':None, 'fmtfilter':'UTF-8'})
        self.failUnless(self.gps.chain[4][1] == {})
        self.failUnless(self.gps.chain[5][0] == {'action':'outfile', 'fname':'-2', 'fmtfilter':'kml'})
        self.failUnless(self.gps.chain[5][1] == {})
        self.failUnless(self.gps.chain[6][0] == {'action':'charset', 'fname':None, 'fmtfilter':'utf8'})
        self.failUnless(self.gps.chain[6][1] == {})
        self.failUnless(self.gps.chain[7][0] == {'action':'outfile', 'fname':'-3', 'fmtfilter':'kml'})
        self.failUnless(self.gps.chain[7][1] == {})
        
    def testAddOutputFile(self):
        self.gps.addOutputFile('-')
        self.failUnless(len(self.gps.chain) == 2)
        self.failUnless(self.gps.chain[0][0] == {'action':'charset', 'fname':None, 'fmtfilter':'UTF-8'})
        self.failUnless(self.gps.chain[0][1] == {})
        self.failUnless(self.gps.chain[1][0] == {'action':'outfile', 'fname':'-', 'fmtfilter':'gpx'})
        self.failUnless(self.gps.chain[1][1] == {})
        
    def testAddCharset(self):
        self.gps.addCharset('UTF-8')
        self.failUnless(len(self.gps.chain) == 1)
        self.failUnless(self.gps.chain[0][0] == {'action':'charset', 'fname':None, 'fmtfilter':'UTF-8'})
        
    def testAddFilter(self):
        self.gps.addFilter('simplify', {'count':6})
        self.failUnless(len(self.gps.chain) == 2)
        self.failUnless(self.gps.chain[0][0] == {'action':'charset', 'fname':None, 'fmtfilter':'UTF-8'})
        self.failUnless(self.gps.chain[0][1] == {})
        self.failUnless(self.gps.chain[1][0] == {'action':'filter', 'fname':None, 'fmtfilter':'simplify'})
        self.failUnless(self.gps.chain[1][1] == {'count':6})
    
    def testWrite(self):
        gpx = gpsbabel.GPXData()
        self.gps.setInGpx(gpx)
        gpx = self.gps.write('-', 'gpx', parseOutput = True)
        self.failUnless(len(gpx.wpts) == 0)
        self.failUnless(len(gpx.rtes) == 0)
        self.failUnless(len(gpx.trks) == 0)
    
    def testRead(self):
        gpx = gpsbabel.GPXData()
        self.gps.stdindata = gpx.toXml()
        gpx = self.gps.read('-', 'gpx', parseOutput = True)
        self.failUnless(len(gpx.wpts) == 0)
        self.failUnless(len(gpx.rtes) == 0)
        self.failUnless(len(gpx.trks) == 0)
        
class GPXWaypointTest(unittest.TestCase):
    def setUp(self):
        self.wpt = gpsbabel.GPXWaypoint()
    
    def testToXmlMinimal(self):
        self.failUnless(self.wpt.toXml('wpt') == '<wpt lat="None" lon="None"></wpt>')
    
    def testToXml(self):
        self.wpt.name = "Test Wpt"
        self.failUnless(self.wpt.toXml('wpt') == '<wpt lat="None" lon="None"><name>Test Wpt</name></wpt>')
        
class GPXRouteTest(unittest.TestCase):
    def setUp(self):
        self.rte = gpsbabel.GPXRoute()
    
    def testToXmlMinimal(self):
        self.failUnless(self.rte.toXml('rte') == '<rte></rte>')
    
    def testToXml(self):
        self.rte.name = "Test Route"
        self.rte.rtepts.append(gpsbabel.GPXWaypoint())
        self.failUnless(self.rte.toXml('rte') == '<rte><name>Test Route</name><rtept lat="None" lon="None"></rtept></rte>')

class GPXTrackSegTest(unittest.TestCase):
    def setUp(self):
        self.trkseg = gpsbabel.GPXTrackSeg()
    
    def testToXmlMinimal(self):
        self.failUnless(self.trkseg.toXml() == '<trkseg></trkseg>')
    
    def testToXml(self):
        self.trkseg.trkpts.append(gpsbabel.GPXWaypoint())
        self.failUnless(self.trkseg.toXml() == '<trkseg><trkpt lat="None" lon="None"></trkpt></trkseg>')

class GPXTrackTest(unittest.TestCase):
    def setUp(self):
        self.trk = gpsbabel.GPXTrack()
    
    def testToXmlMinimal(self):
        self.failUnless(self.trk.toXml('trk') == '<trk></trk>')
    
    def testToXml(self):
        self.trk.name = "Test Track"
        self.trk.trksegs.append(gpsbabel.GPXTrackSeg())
        self.failUnless(self.trk.toXml('trk') == '<trk><name>Test Track</name><trkseg></trkseg></trk>')
       
class GPXDataTest(unittest.TestCase):
    def setUp(self):
        self.gpx = gpsbabel.GPXData()
        
    def testToXmlMinimal(self):
        self.failUnless(self.gpx.toXml() == '<gpx version="1.1" creator="Python GPSBabel"></gpx>')

    def testToXml(self):
        self.gpx.rtes.append(gpsbabel.GPXRoute())
        self.gpx.wpts.append(gpsbabel.GPXWaypoint())
        self.gpx.trks.append(gpsbabel.GPXTrack())
        self.failUnless(self.gpx.toXml() == '<gpx version="1.1" creator="Python GPSBabel"><wpt lat="None" lon="None"></wpt><rte></rte><trk></trk></gpx>')
    
class GPXParserTest(unittest.TestCase):
    def testParseWaypoint(self):
        gd = gpsbabel.gpxParse(
"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.0" creator="GPSBabel - http://www.gpsbabel.org" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
<time>2008-10-22T18:20:22Z</time>
<bounds minlat="40.735149952" minlon="-75.099566588" maxlat="40.744316652" maxlon="-75.088833310"/>
<wpt lat="40.735149952" lon="-75.088833310">
<ele>-0.114380</ele>
<name>GC187W</name>
<cmt>GC187W</cmt>
<desc>GC187W</desc>
<sym>Waypoint</sym>
</wpt>
</gpx>
""")
        self.failUnless(len(gd.wpts) == 1)
        self.failUnless(len(gd.rtes) == 0)
        self.failUnless(len(gd.trks) == 0)
        wpt = gd.wpts[0]
        self.failUnless(wpt.lat  == "40.735149952")
        self.failUnless(wpt.lon  == "-75.088833310")
        self.failUnless(wpt.ele  == "-0.114380")
        self.failUnless(wpt.name == "GC187W")
        self.failUnless(wpt.cmt  == "GC187W")
        self.failUnless(wpt.desc == "GC187W")
        self.failUnless(wpt.sym  == "Waypoint")
    
    def testParseRoute(self):
        gd = gpsbabel.gpxParse(
"""<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0" version="1.0" creator="GPSBabel - http://www.gpsbabel.org" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
  <time>2008-10-22T18:20:11Z</time>
  <bounds minlat="40.735149952" minlon="-75.094233267" maxlat="40.736349989" maxlon="-75.088833310"/>
  <rte>
    <name>GC187W-GC187W</name>
    <rtept lat="40.735149952" lon="-75.088833310">
      <ele>0.000000</ele>
      <name>GC187W</name>
      <fix>none</fix>
    </rtept>
    <rtept lat="40.736349989" lon="-75.094233267">
      <ele>0.000000</ele>
      <name>GC198A</name>
      <fix>none</fix>
    </rtept>
    <rtept lat="40.735149952" lon="-75.088833310">
      <ele>0.000000</ele>
      <name>GC187W</name>
      <fix>none</fix>
    </rtept>
  </rte>
</gpx>
""")
        self.failUnless(len(gd.wpts) == 0)
        self.failUnless(len(gd.rtes) == 1)
        self.failUnless(len(gd.rtes[0].rtepts) == 3)
        self.failUnless(len(gd.trks) == 0)
        wpt = gd.rtes[0].rtepts[0]
        self.failUnless(wpt.lat  == "40.735149952")
        self.failUnless(wpt.lon  == "-75.088833310")
        self.failUnless(wpt.ele  == "0.000000")
        self.failUnless(wpt.name == "GC187W")
        self.failUnless(wpt.fix  == "none")
        wpt = gd.rtes[0].rtepts[1]
        self.failUnless(wpt.lat  == "40.736349989")
        self.failUnless(wpt.lon  == "-75.094233267")
        self.failUnless(wpt.ele  == "0.000000")
        self.failUnless(wpt.name == "GC198A")
        self.failUnless(wpt.fix  == "none")
        wpt = gd.rtes[0].rtepts[2]
        self.failUnless(wpt.lat  == "40.735149952")
        self.failUnless(wpt.lon  == "-75.088833310")
        self.failUnless(wpt.ele  == "0.000000")
        self.failUnless(wpt.name == "GC187W")
        self.failUnless(wpt.fix  == "none")

    def testParseTrack(self):
        gd = gpsbabel.gpxParse(
"""<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0" version="1.0" creator="GPSBabel - http://www.gpsbabel.org" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
  <time>2008-10-22T18:21:23Z</time>
  <bounds minlat="40.515346527" minlon="-75.142643452" maxlat="40.826461315" maxlon="-74.611737728"/>
  <trk>
    <name>ACTIVE LOG #2</name>
    <number>1</number>
    <trkseg>
      <trkpt lat="40.727884769" lon="-75.115907192">
        <ele>310.162476</ele>
        <time>2008-08-17T18:39:00Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
""")
        self.failUnless(len(gd.wpts) == 0)
        self.failUnless(len(gd.rtes) == 0)
        self.failUnless(len(gd.trks) == 1)
        self.failUnless(len(gd.trks[0].trksegs) == 1)
        self.failUnless(len(gd.trks[0].trksegs[0].trkpts) == 1)
        trk = gd.trks[0]
        self.failUnless(trk.name == "ACTIVE LOG #2")
        self.failUnless(trk.number == "1")
        wpt = trk.trksegs[0].trkpts[0]
        self.failUnless(wpt.lat == "40.727884769")
        self.failUnless(wpt.lon == "-75.115907192")
        self.failUnless(wpt.ele == "310.162476")
        self.failUnless(wpt.time == "2008-08-17T18:39:00Z")
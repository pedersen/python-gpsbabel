"""
This module is is the main module for GPSBabel. It is intended to be a complete Python interface, allowing easy mechanisms to the developer to control GPSBabel from within a Python application.

helper methods: getCurrentLoc
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
import xml.sax
import xml.sax.handler

class GPSBabel(object):
    def __init__(self, loc="gpsbabel"):
        self.gpsbabel = loc
        self.clearChainOpts()
        self.validateVersion()
        self.readOpts()
    
    def execCmd(self, cmd=None, parseOutput=True, debug=False):
        if cmd is None: cmd = self.buildCmd(debug)
        gps = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = gps.communicate(self.stdindata)
        returncode = gps.poll()
        output = stdout.split("\n")
        output.extend(stderr.split("\n"))
        if self.autoClear: self.clearChainOpts()
        if parseOutput: output = gpxParse("\n".join(output))
        return(returncode, output)
    
    def getCurrentGpsLocation(self, port, gpsType):
        self.addAction('infile', gpsType, {'get_posn' : None}, port)
        self.captureStdOut()
        ret, gpx = self.execCmd()
        return gpx
    
    def writeToGps(self, port, gpsType, wpt=False, route=False, track=False):
        self.procWpts   = wpt
        self.procRoutes = route
        self.procTrack  = track
        self.addAction('outfile', gpsType, {}, port)
        self.captureStdOut()
        ret, gpx = self.execCmd(parseOutput = False)
        return gpx
    
    def captureStdOut(self):
        self.addAction('outfile', 'gpx', {}, '-')
        
    def setInGpx(self, gpx):
        if isinstance(gpx, str):
            self.stdindata = gpx
            self.addAction('infile', 'gpx', {}, '-')
        elif isinstance(gpx, GPXData):
            self.stdindata = gpx.toXml()
            self.addAction('infile', 'gpx', {}, '-')
        else:
            raise Exception("Unable to set stdin for gpsbabel. Aborting!")
    
    actions = ['charset', 'infile', 'filter', 'outfile']
    def addAction(self, action, fmtfilter, opts={}, fname=None):
        action = action.lower()
        if action not in self.actions:
            raise UnknownActionException("Error: Unknown action %s" % action)
        if action in ['infile', 'outfile'] and fname == None:
            raise MissingFilenameException('Error: Action %s requires a filename, and we have none' % action)
        if action in ['infile', 'outfile']:
            if not self.ftypes.has_key(fmtfilter):
                raise MissingFilefmtException('Error: File format %s is unknown' % fmtfilter)
            for key in opts.keys():
                if not key in self.ftypes[fmtfilter]:
                    raise InvalidOptionException('Error: File format %s has no such option %s' % (fmtfilter, key))
        if action == 'filter':
            if not self.filters.has_key(fmtfilter):
                raise MissingFilterException('Error: Filter %s is unknown' % fmtfilter)
            for key in opts.keys():
                if not key in self.filters[fmtfilter]:
                    raise InvalidOptionException('Error: Filter %s has no such option %s' % (fmtfilter, key))
        if action == 'charset':
            cfound = False
            if not self.charsets.has_key(fmtfilter):
                for key in self.charsets.keys():
                    if fmtfilter in self.charsets[key]: cfound = True
            else: cfound = True
            if not cfound:
                raise UnknownCharsetException('Error: Unknown character set %s' % fmtfilter)
        self.chain.append([{'action' : action, 'fmtfilter' : fmtfilter, 'fname' : fname}, opts])
        
    def clearChainOpts(self):
        self.ini        = ""
        self.shortnames = False
        self.procRoutes = False
        self.procTrack  = False
        self.procWpts   = False
        self.procGps    = False
        self.smartIcons = True
        self.stdindata  = ""
        self.chain      = []
        if not hasattr(self, "autoClear"): self.autoClear = True
    
    def validateVersion(self):
        ret, gps = self.execCmd([self.gpsbabel, "-V"], parseOutput = False)
        version = ""
        for line in gps:
            if line.strip() != "": version = "%s%s" % (version, line.strip())
        if version not in ['GPSBabel Version 1.3.5', 'GPSBabel Version 1.3.3']:
            raise Exception('Unsupported version of GPSBabel installed. Aborting.')
        
    def readOpts(self):
        self.ftypes = {}
        self.filters = {}
        self.charsets = {}
        ftype = ''
        ret, gps = self.execCmd([self.gpsbabel, "-h"], parseOutput = False)
        mode = 0 # 0 == do nothing, 1 == file type, 2 === filter
        for line in gps:
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
        ret, gps = self.execCmd([self.gpsbabel, "-l"], parseOutput = False)
        mode = 0 # 0 == do nothing, 1 == char set, 2 === char set alias
        for line in gps:
            line = line.rstrip()
            if line.startswith('*'):
                charset = line[line.find(' ')+1:]
                self.charsets[charset] = []
            if line.startswith('\t'):
                self.charsets[charset].extend(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), line.strip().split(','))))

    def buildCmd(self, debug=False):
        cmd = ['gpsbabel', '-p']
        cmd.append('' if len(self.ini) == 0 else self.ini)
        if debug: cmd.extend(['-D', '10'])
        if self.shortnames:     cmd.append('-s')
        if self.procRoutes:     cmd.append('-r')
        if self.procTrack:      cmd.append('-t')
        if self.procWpts:       cmd.append('-w')
        if self.procGps:        cmd.append('-T')
        if not self.smartIcons: cmd.append('-N')
        for i in self.chain:
            fmt    = i[0]
            opts_d = i[1]
            opts   = ",".join(map(lambda x: "%s%s" % (x, "=%s" % opts_d[x] if opts_d[x] else ""), opts_d.keys()))
            if len(opts) > 0: opts = ",%s" % opts
            if fmt['action'] == 'infile':
                cmd.extend(['-i', '%s%s' % (fmt['fmtfilter'], opts)])
                cmd.extend(['-f', fmt['fname']])
            elif fmt['action'] == 'outfile':
                cmd.extend(['-o', '%s%s' % (fmt['fmtfilter'], opts)])
                cmd.extend(['-F', fmt['fname']])
            elif fmt['action'] == 'filter':
                cmd.extend(['-x', '%s%s' % (fmt['fmtfilter'], opts)])
            elif fmt['action'] == 'charset':
                cmd.extend(['-c', '%s%s' % (fmt['fmtfilter'], opts)])
        return cmd
    
class GPXData(object):
    __slots__ = ['wpts', 'rtes', 'trks']
    
    def __init__(self):
        self.wpts = []
        self.rtes = []
        self.trks = []
    
    def toXml(self):
        return '<gpx version="1.1" creator="Python GPSBabel">' + \
               "".join(map(lambda x: x.toXml("wpt"), self.wpts)) + \
               "".join(map(lambda x: x.toXml("rte"), self.rtes)) + \
               "".join(map(lambda x: x.toXml("trk"), self.trks)) + \
               '</gpx>'
    
    def finalize(self):
        pass

class GPXWaypoint(object):
    __slots__ = ['lat', 'lon', 'ele', 'time', 'magvar', 'geoidheight', 'name', 'cmt', 'desc',
                 'src', 'link', 'sym', 'type', 'fix', 'sat', 'hdop', 'vdop', 'pdop',
                 'ageofdgpsdata', 'dgpsid']
    
    def __init__(self):
        for i in self.__slots__:
            setattr(self, i, None)
    
    def toXml(self, tag):
        return '<%s lat="%s" lon="%s">' % (tag, str(self.lat), str(self.lon)) + \
               "".join(map(lambda x: '<%s>%s</%s>' % (x, getattr(self, x), x), \
                   filter(lambda x: x not in ['lat', 'lon'] and getattr(self, x) != None, self.__slots__))) + \
               '</%s>' % (tag)
    
    def finalize(self):
        pass

class GPXRoute(object):
    __slots__ = ['name', 'cmt', 'desc', 'src', 'link', 'number', 'type', 'rtepts']
    
    def __init__(self):
        for i in self.__slots__:
            setattr(self, i, None)
        self.rtepts = []
    
    def toXml(self, tag):
        return '<%s>' % (tag) + \
               "".join(map(lambda x: '<%s>%s</%s>' % (x, getattr(self, x), x), \
                   filter(lambda x: x not in ['rtepts'] and getattr(self, x) != None, self.__slots__))) + \
               "".join(map(lambda x: x.toXml("rtept"), self.rtepts)) + \
               '</%s>' % (tag)
    
    def finalize(self):
        pass

class GPXTrackSeg(object):
    __slots__ = ['trkpts']
    
    def __init__(self):
        self.trkpts = []
    
    def toXml(self):
        return "<trkseg>" + \
               "".join(map(lambda x: "%s" % x.toXml("trkpt"), self.trkpts)) + \
               "</trkseg>"
    
    def finalize(self):
        pass

class GPXTrack(object):
    __slots__ = ['name', 'cmt', 'desc', 'src', 'link', 'number', 'type', 'trksegs']
    
    def __init__(self):
        for i in self.__slots__:
            setattr(self, i, None)
        self.trksegs = []
    
    def toXml(self, tag):
        return '<%s>' % (tag) + \
               "".join(map(lambda x: '<%s>%s</%s>' % (x, getattr(self, x), x), \
                   filter(lambda x: x not in ['trksegs'] and getattr(self, x) != None, self.__slots__))) + \
               "".join(map(lambda x: x.toXml(), self.trksegs)) + \
               '</%s>' % (tag)
    
    def finalize(self):
        pass

class UnknownActionException(Exception):
    pass
class MissingFilenameException(Exception):
    pass
class MissingFilterException(Exception):
    pass
class MissingFilefmtException(Exception):
    pass
class InvalidOptionException(Exception):
    pass
class UnknownCharsetException(Exception):
    pass

def gpxParse(instr):
    gpxp = GPXParser()
    xml.sax.parseString(instr, gpxp)
    return gpxp.gpx
    
class GPXParser(xml.sax.handler.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.reset()
    
    def reset(self):
        self.chdata = ""
        self.read = 0
        self.gpx = GPXData()
        self.objstack = [self.gpx]
        
    def startElement(self, name, attrs):
        """
        State Changes:
          nothing - waypoint - nothing
          nothing - route - waypoint - route - nothing
          nothing - track - trackseg - waypoint - trackseg - track - nothing
        States: 0=nothing, 1=wpt, 2=rte, 3=rte/wpt, 4=trk, 5=trkseg, 6=trkseg/wpt
        """
        self.chdata = ""
        if self.read == 0:
            if name == "wpt":
                self.read = 1
                cur = GPXWaypoint()
                self.objstack.append(cur)
                for i in attrs.keys():
                    setattr(cur, i, attrs[i])
            elif name == "rte":
                self.read = 2
                cur = GPXRoute()
                self.objstack.append(cur)
                for i in attrs.keys():
                    setattr(cur, i, attrs[i])
            elif name == "trk":
                self.read = 4
                cur = GPXTrack()
                self.objstack.append(cur)
                for i in attrs.keys():
                    setattr(cur, i, attrs[i])
        elif self.read == 1: # Waypoints
            for i in attrs.keys():
                setattr(self.objstack[-1], i, attrs[i])
        elif self.read == 2: # Routes
            if name == "rtept":
                self.read = 3
                cur = GPXWaypoint()
                self.objstack.append(cur)
            for i in attrs.keys():
                setattr(self.objstack[-1], i, attrs[i])
        elif self.read == 3: # Route Waypoints
            for i in attrs.keys():
                setattr(self.objstack[-1], i, attrs[i])
        elif self.read == 4: # Tracks
            if name == "trkseg":
                self.read = 5
                cur = GPXTrackSeg()
                self.objstack.append(cur)
            for i in attrs.keys():
                setattr(self.objstack[-1], i, attrs[i])
        elif self.read == 5: # Track Seg
            if name == "trkpt":
                self.read = 6
                cur = GPXWaypoint()
                self.objstack.append(cur)
            for i in attrs.keys():
                setattr(self.objstack[-1], i, attrs[i])
        elif self.read == 6: # Track Segment Waypoints
            for i in attrs.keys():
                setattr(self.objstack[-1], i, attrs[i])
    
    def characters(self, ch):
        if self.read:
            self.chdata = "%s%s" % (self.chdata, ch)
    
    def endElement(self, name):
        name = name.lower()
        if self.read == 1: # Waypoints
            if name == "wpt":
                obj = self.objstack.pop()
                obj.finalize()
                self.gpx.wpts.append(obj)
                self.read = 0
            else:
                if self.chdata.strip() != "": setattr(self.objstack[-1], name, self.chdata)
                self.chdata = ""
        elif self.read == 2: # Routes
            if name == "rte":
                obj = self.objstack.pop()
                obj.finalize()
                self.gpx.rtes.append(obj)
                self.read = 0
            else:
                if self.chdata.strip() != "": setattr(self.objstack[-1], name, self.chdata)
                self.chdata = ""
        elif self.read == 3: # Route Waypoints
            if name == "rtept":
                obj = self.objstack.pop()
                obj.finalize()
                self.objstack[-1].rtepts.append(obj)
                self.read = 2
            else:
                if self.chdata.strip() != "": setattr(self.objstack[-1], name, self.chdata)
                self.chdata = ""
        elif self.read == 4: # Tracks
            if name == "trk":
                obj = self.objstack.pop()
                obj.finalize()
                self.gpx.trks.append(obj)
                self.read = 0
            else:
                if self.chdata.strip() != "": setattr(self.objstack[-1], name, self.chdata)
                self.chdata = ""
        elif self.read == 5: # Track Segments
            if name == "trkseg":
                obj = self.objstack.pop()
                obj.finalize()
                self.objstack[-1].trksegs.append(obj)
                self.read = 4
            else:
                if self.chdata.strip() != "": setattr(self.objstack[-1], name, self.chdata)
                self.chdata = ""
        elif self.read == 6: # Track Segment Waypoints
            if name == "trkpt":
                obj = self.objstack.pop()
                obj.finalize()
                self.objstack[-1].trkpts.append(obj)
                self.read = 5
            else:
                if self.chdata.strip() != "": setattr(self.objstack[-1], name, self.chdata)
                self.chdata = ""


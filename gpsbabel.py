"""
This module is is the main module for GPSBabel. It is intended to be a complete Python interface, allowing easy mechanisms to the developer to control GPSBabel from within a Python application.

I've got to add classes for the data
types (track, route, waypoint, live tracking), and code that will read
the gpx file and write a gpx file containing same classes, and then a
couple more convenience methods, and the work is all done.

helper methods: gpxParse, getCurrentLoc
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
    
    def execCmd(self, cmd=None, parseOutput=True):
        if cmd is None: cmd = self.buildCmd()
        gps = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        gps.stdin.write(self.stdindata)
        gps.stdin.close()
        output = gps.stdout.readlines()
        if self.autoClear: self.clearChainOpts()
        return(gps.returncode, output)
    
    def captureStdOut(self):
        self.addAction('outfile', 'gpx', {}, '-')
        
    def setInGpx(self, gpx):
        if isinstance(gpx, str):
            self.stdindata = gpx
        elif isinstance(gpx, GPXData):
            self.stdindata = gpx.toXml()
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
        ret, gps = self.execCmd([self.gpsbabel, "-V"])
        version = ""
        for line in gps:
            if line.strip() != "": version = "%s%s" % (version, line)
        if version not in ['GPSBabel Version 1.3.5\n']:
            raise Exception('Unsupported version of GPSBabel installed. Aborting.')
        
    def readOpts(self):
        self.ftypes = {}
        self.filters = {}
        self.charsets = {}
        ftype = ''
        ret, gps = self.execCmd([self.gpsbabel, "-h"])
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
        ret, gps = self.execCmd([self.gpsbabel, "-l"])
        mode = 0 # 0 == do nothing, 1 == char set, 2 === char set alias
        for line in gps:
            line = line.rstrip()
            if line.startswith('*'):
                charset = line[line.find(' ')+1:]
                self.charsets[charset] = []
            if line.startswith('\t'):
                self.charsets[charset].extend(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), line.strip().split(','))))

    def buildCmd(self):
        cmd = ['gpsbabel', '-p']
        cmd.append('""' if len(self.ini) == 0 else self.ini)
        if self.shortnames:     cmd.append('-s')
        if self.procRoutes:     cmd.append('-r')
        if self.procTrack:      cmd.append('-t')
        if self.procWpts:       cmd.append('-w')
        if self.procGps:        cmd.append('-T')
        if not self.smartIcons: cmd.append('-N')
        for i in self.chain:
            fmt    = i[0]
            opts_d = i[1]
            opts   = ",".join(map(lambda x: "%s=%s" % (x, opts_d[x]), opts_d.keys()))
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
        self.clearChainOpts()
        return cmd
    
class GPXData(object):
    __slots__ = ['wpts', 'rtes', 'trk']
    
    def __init__(self):
        self.wpts = []
        self.rtes = []
        self.trk  = []
    
    def toXml(self):
        return '<gpx version="1.1" creator="Python GPSBabel">' + \
               "".join(map(lambda x: x.toXml("wpt"), self.wpts)) + \
               "".join(map(lambda x: x.toXml("rte"), self.rtes)) + \
               "".join(map(lambda x: x.toXml("trk"), self.trk)) + \
               '</gpx>'

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
               "".join(map(lambda x: "<trkseg>%s</trkseg>" % x.toXml("trkpt"), self.trksegs)) + \
               '</%s>' % (tag)

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

class GPXParser(xml.sax.handler.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.reset()
    
    def reset(self):
        self.chdata = ""
        self.read = False
        
    def startElement(self, name, attrs):
        pass
    
    def characters(self, ch):
        if self.read:
            self.chdata = "%s%s" % (self.chdata, ch)
    
    def endElement(self, name):
        pass
        
if __name__ == "__main__":
    gps = GPSBabel()

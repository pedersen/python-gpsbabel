"""
This module is is the main module for GPSBabel. It is intended to be a complete Python interface, allowing easy mechanisms to the developer to control GPSBabel from within a Python application.

I've got to add classes for the data
types (track, route, waypoint, live tracking), and code that will read
the gpx file and write a gpx file containing same classes, and then a
couple more convenience methods, and the work is all done.

helper methods: setInGpx, captureStdOut, gpxParse, getCurrentLoc
classes: GPSData, Waypoint, Route, Track, LiveTracking
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
    def __init__(self, loc="gpsbabel"):
        self.gpsbabel = loc
        self.clearChainOpts()
        self.validateVersion()
        self.readOpts()
    
    def execCmd(self, cmd=None):
        if cmd is None: cmd = self.buildCmd()
        gps = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        gps.stdin.writelines(self.stdindata)
        gps.stdin.close()
        output = gps.stdout.readlines()
        if self.autoClear: self.clearChainOpts()
        return(output)
    
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
        self.stdindata  = []
        self.chain      = []
        if not hasattr(self, "autoClear"): self.autoClear = True
    
    def validateVersion(self):
        gps = self.execCmd([self.gpsbabel, "-V"])
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
        gps = subprocess.Popen([self.gpsbabel, "-h"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        gps = subprocess.Popen([self.gpsbabel, "-l"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mode = 0 # 0 == do nothing, 1 == char set, 2 === char set alias
        for line in gps.stdout.readlines():
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

if __name__ == "__main__":
    gps = GPSBabel()

"""
This module is is the main module for GPSBabel. It is intended to be a
complete Python interface, allowing easy mechanisms to the developer to
control GPSBabel from within a Python application.

It is highly recommended to read the documentation on GPSBabel at
http://www.gpsbabel.org/ as the usage of this module is heavily modeled on
the general usage of GPSBabel itself.

The classes in this module are grouped as follows:
    * GPSBabel: The wrapper around the gpsbabel command line
    * GPXData, GPXWaypoint, GPXRoute, GPXTrackSeg, GPXTreck: These classes
      represent the various components of a GPX file that can/will be
      captured/used by other tools.
    * *Exception: Custom exception classes that can be raised for specific
      error conditions when trying to run GPSBabel.
    * GPXParser: The class that parses GPX files.

There is also the utility method "gpxParse" which is used to actually parse
a gpx file into the GPX classes above, and which uses the GPXParser class.

Examples of usage:
* Store waypoints, routes, and tracks in file 'mydata.gpx' on a Garmin GPS
  on port /dev/ttyUSB0, and don't XML parse the output
    gps = GPSBabel()
    gps.addAction('infile', 'gpx', {}, 'mydata.gpx')
    gps.write('/dev/ttyUSB0', 'garmin', True, True, True, False)

* Store all waypoints in GPXData.wpts into 'mydata.kml', and not parse
  the output
    gpxd = GPXData()
    gpxd.wpts.append(GPXWaypoint())
    gpxd.wpts[-1].lat = "45.0"
    gpxd.wpts[-1].lon = "-70.0"
    gpxd.wpts[-1].name = "WPT1"
    gps = GPSBabel()
    gps.setInGpx(gpxd)
    gps.write('mydata.kml', 'kml', True, False, False, False)

* Read a kml file 'mydata.kml' into GPXData objects
    gps = GPSBabel()
    gps.addAction('infile', 'kml', {}, 'mydata.kml')
    gps.captureStdOut()
    gpxd = gps.execCmd()

* Store gpxd waypoints into a Garmin GPS on a Windows USB port, and don't
  parse the output
    gps = GPSBabel()
    gps.setInGpx(gpxd)
    gps.write('usb:', 'garmin', True, parseOutput = False)
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
    """
    gpsbabel ( http://www.gpsbabel.org/ ) operates on the concept of a
    chain of actions. You can specify character set changes, input files,
    output files, and filters, all of which can be combined in any number
    of ways.

    The GPSBabel class fully supports doing this. In fact, the only options
    that are not supported are the -D option (debugging), the -b option
    (batch files), and the -T option (continous tracking from the GPS).
    Everything else can be done with GPSBabel. This gives you amazing
    power, but that power comes at a price. We try to hide it as much as
    possible, but it's not totally easy to do so.

    Methods are grouped into three sections. Commonly used, infrequently
    used, and not likely to be used. The sections are an estimate of how
    often you are likely to use them in your code.

    Member variables:
        * actions: The list of types of actions supported by gpsbabel.
          Curently, this list is infile, outfile, charset, and filter

    Instance variables:
        * ini: The location of the GPSBabel ini file. Default: Empty
        * shortnames: Boolean. Equal to -s flag. Default: False
        * procRoutes: Boolean. Equal to -r flag. Default: False
        * procTrack:  Boolean. Equal to -t flag. Default: False
        * procWpts:   Boolean. Equal to -w flag. Default: False
        * smartIcons: Boolean. Equal to -N flag. Default: True
        * stdindata:  String. Contains the data to send on stdin to
                      gpsbabel. Default: Empty
        * chain:      Array. The list of actions to perform for this run of
                      gpsbabel. Default: Empty
        * autoClear:  Boolean. Determines whether to reset all options
                      after running gpsbabel to defaults. Default: True
        * ftypes:     A dictionary of supported file types. Each key's
                      value is a list of supported options
        * filters:    A dictionary of supported filters. Each key's
                      value is a list of supported options
        * charsets:   A dictionary of supported character sets. Each key's
                      value is a list of supported aliases for that
                      character set.
        * banner:     The full GPSBabel version string
        * version:    The portion of the version string which just is the
                      version (e.g.: 1.3.5), or None if it could not found.
    """

    # Most commonly used methods here

    def __init__(self, loc="gpsbabel"):
        """
        Constructor.

        In:
            loc: String containing location of gpsbabel command. Can be
                 left blank if gpsbabel is in the user's PATH.

        Sets instance defaults, validates the version of gpsbabel on the
        system is in the list of supported versions, and reads the list of
        formats, filters, and character sets supported by this version of
        gpsbabel.
        """
        self.gpsbabel = loc
        self.clearChainOpts()
        self.validateVersion()
        self.readOpts()
    
    def execCmd(self, cmd=None, parseOutput=True, debug=False):
        """
        Used to run the command that has been built.

        In:
            cmd: A list. If specified, the list is all the components of
                the command line to be run. For instance, to get a version
                statement, you would pass in ['gpsbabel', '-V']. This will
                allow you to run any arbitrary command at all, not just
                gpsbabel
            parseOutput: If True, attempt to parse the output as a GPX
                file.
            debug: If True, and cmd is None, set the debug level to 10
                while running gpsbabel

        Out:
            (returncode, output): returncode is the result code from
            running the command (should always be 0 in case of success).
            output is either an array of lines which are the raw output (in
            cases where parseOutput is False), or a set of GPXData/etc
            objects (where parseOutput is True)

        This method calls buildCmd when cmd is None, then runs the command
        specified by the list that is now cmd, gathers the output, parses
        it (when parseOutput is true), resets all defaults, and returns the
        results of the run.
        """
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
        """
        Reads the current location from an attached GPS.

        In:
            port: The device name for the port that gpsbabel will be able
                to use. /dev/ttyUSB0 com1 usb: are all valid (depending on
                operating system)
            gpsType: The type of GPS that is attached as known by gpsbabel.
                Currently, the option "get_posn" must be supported by that
                input format. As of now, this limits to nmea and garmin
                formats.

        Out:
            a GPXWaypoint object that contains the current location as
            reported by the GPS.

        The method is simple: Set the attached GPS as the input. Capture
        the output. Let execCmd parse the resulting output, and return the
        resulting GPXWaypoint that is given to use by execCmd
        """
        self.addAction('infile', gpsType, {'get_posn' : None}, port)
        self.captureStdOut()
        ret, gpx = self.execCmd()
        return gpx
    
    def write(self, fname, fmt, wpt=False, route=False, track=False, parseOutput=False):
        """
        Performs a conversion where the goal is output. Often used for
        writing to an attached GPS.
        ***WARNING***
        Note that this method assumes that you have already used setInGpx,
        or otherwise assigned the stdindata/set the input source. It will
        fail if you have not.
        ***WARNING***

        In:
            fname: The name of the file to write to. When this is a GPS,
                use a portname. /dev/ttyUSB0 com1 usb: are all valid
                (depending on operating system)
            fmt: The output format to use. Anything listed in ftypes is
                supported. Note: No options can be passed using this
                method.
            wpt: Turn on/off waypoint processing.
            route: Turn on/off route processing.
            track: Turn on/off track processing.
            parseOutput: Turn on/off parsing of data into GPXData/etc
                objects
        
        Out:
            The output portion of execCmd, ignoring the return code

        The method is beyond simple: Set the processing options. Add the
        outfile processing, and run the resulting command.
        """
        self.procWpts   = wpt
        self.procRoutes = route
        self.procTrack  = track
        self.addAction('outfile', fmt, {}, fname)
        ret, gpx = self.execCmd(parseOutput)
        return gpx
    
    def read(self, fname, fmt, wpt=False, route=False, track=False, parseOutput=True):
        """
        Performs a conversion where the goal is input. Often used for
        reading from an attached GPS.

        In:
            fname: The name of the file to write to. When this is a GPS,
                use a portname. /dev/ttyUSB0 com1 usb: are all valid
                (depending on operating system)
            fmt: The output format to use. Anything listed in ftypes is
                supported. Note: No options can be passed using this
                method.
            wpt: Turn on/off waypoint processing.
            route: Turn on/off route processing.
            track: Turn on/off track processing.
            parseOutput: Turn on/off parsing of data into GPXData/etc
                objects
        
        Out:
            The output portion of execCmd, ignoring the return code

        The method is beyond simple: Set the processing options. Add the
        infile processing, set the output capture, and run the resulting
        command.
        """
        self.procWpts   = wpt
        self.procRoutes = route
        self.procTrack  = track
        self.addAction('infile', fmt, {}, fname)
        self.captureStdOut()
        ret, gpx = self.execCmd(parseOutput)
        return gpx
    
    def setInGpx(self, gpx):
        """
        Convenience method used to set stdindata to gpx data.

        In:
            gpx: Either a string containing a valid GPX file or a
            GPXData/etc object.

        This method assumes that any string coming in will be a valid
        string of XML which conforms to the GPX specification. If it does
        not, then the eventual run of gpsbabel will fail.

        The method is simple: Set the stdindata instance variable to be
        either the string that is passed in, or the GPXData/etc object will
        be converted to XML and stdindata will be set to that XML data.

        Afterwards, addAction will be called to set the stdin to work
        correctly.

        Note that no options can be set on the format using this method.
        """
        if isinstance(gpx, str):
            self.stdindata = gpx
            self.addAction('infile', 'gpx', {}, '-')
        elif isinstance(gpx, GPXData):
            self.stdindata = gpx.toXml()
            self.addAction('infile', 'gpx', {}, '-')
        else:
            raise Exception("Unable to set stdin for gpsbabel. Aborting!")
    
    def captureStdOut(self):
        """
        Add the action to the chain of capturing stdout.
        """
        self.addAction('outfile', 'gpx', {}, '-')
        
    # Important methods, though they will not be commonly used, here

    actions = ['charset', 'infile', 'filter', 'outfile']
    """
    Valid actions which GPSBabel can use.
    """

    def addAction(self, action, fmtfilter, opts={}, fname=None):
        """
        Add an action to the action chain.

        In:
            action: The name of the action to add
            fmtfilter: The name of the format, filter, or character set (or
                alias) to add
            opts: Any options to add. Each key's values will be the value
                of the option. Use None for a key's value to designate no
                value being passed to the option. For example
                { 'get_posn' : None, 'snlen' : '6' }
                would designate to pass get_posn with no values added, and
                snlen with a value of 6. This would appear as
                "get_posn,snlen=6" on the command line.
            fname: The name of the file to be used for this action. Use '-'
                for stdin/stdout
        
        This method is actually fairly complex, mainly because this is
        where most error checking happens. The options are checked to make
        sure that they are compatible with the format or filter. The action
        is checked to make sure it's a legal action. The
        format/filter/character set is checked to make sure it's legal.
        
        After all checks pass, a new entry is added to the chain list. The
        entry is actually two dictionaries. The first describes the action,
        and includes the type, the format/filter/character set, and the
        filename. The second dictionary is the options. So, the entry to
        grab the output as gpx with an snlen of 10 looks like this:
            chain[-1] = [
                { 'action' : 'outfile', 'fmtfilter': 'gpx', 'fname' : '-'},
                { 'snlen' : '10' }
                ]
        """
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
        """
        Reset all default values, and clear the action chain
        """
        self.ini        = ""
        self.shortnames = False
        self.procRoutes = False
        self.procTrack  = False
        self.procWpts   = False
        self.smartIcons = True
        self.stdindata  = ""
        self.chain      = []
        if not hasattr(self, "autoClear"): self.autoClear = True
    
    # The following methods are meant for internal use. You are welcome to use them yourself, but they are going to be extremely uncommon

    def validateVersion(self):
        """
        Find the version of GPSBabel in the system path and make sure it's
        supported. Raise an exception if not.
        """
        ret, gps = self.execCmd([self.gpsbabel, "-V"], parseOutput = False)
        version = ""
        for line in gps:
            if line.strip() != "": version = "%s%s" % (version, line.strip())
        if version not in ['GPSBabel Version 1.3.5', 'GPSBabel Version 1.3.3']:
            raise Exception('Unsupported version of GPSBabel installed. Aborting.')
        
        self.banner = version
        try:
            self.version = version.split(" ")[2]
        except:
            self.version = None
    check_exe = validateVersion
    """
    Provide an alias to validateVersion
    """
        
    def readOpts(self):
        """
        Read the supported formats/filters/character sets from the
        installed gpsbabel.

        Run gpsbabel with the -h parameter, and parse the three sections:
        0: general help, which this method ignores
        1: file types. Make sure to read options when reading the file
            types
        2: filters. Make sure to read options when reading the filters

        Run gpsbabel with the -l parmater, and parse the output. Character
        set names are on lines starting with "*", and aliases are on
        subsequent lines and the lines start with the tab character ("\t")
        """
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
        for line in gps:
            line = line.rstrip()
            if line.startswith('*'):
                charset = line[line.find(' ')+1:]
                self.charsets[charset] = []
            if line.startswith('\t'):
                self.charsets[charset].extend(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), line.strip().split(','))))

    def buildCmd(self, debug=False):
        """
        Build a list of command line and options for gpsbabel.

        In:
            debug: If true, add ["-D", "10"] to the command line

        Out:
            A list of command line parameters. Example:
                ['gpsbabel', '-p', '', '-D', '10', '-i', 'gpx', '-f', \
                    '-', '-o', 'garmin', '-F', '/dev/ttyUSB0']

        The method is simple: Make the base list, add various options as
        specified by the flags. Loop over the actions, and add them in
        appropriately. Return the list.
        """
        cmd = [self.gpsbabel, '-p']
        cmd.append('' if len(self.ini) == 0 else self.ini)
        if debug: cmd.extend(['-D', '10'])
        if self.shortnames:     cmd.append('-s')
        if self.procRoutes:     cmd.append('-r')
        if self.procTrack:      cmd.append('-t')
        if self.procWpts:       cmd.append('-w')
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
    """
    The root container for gpx data objects.

    All of these objects function similarly. Define the legal instance
    members, define a toXml method to convert data to legal gpx format, and
    a finalize method to allow any postprocessing to occur when loading xml
    data into them (for instance, this could be used to convert floats from
    string to decimal).

    wpts is a list of GPXWaypoint
    rtes is a list of GPXRoute
    trks is a list of GPXTracks
    """
    __slots__ = ['wpts', 'rtes', 'trks']
    
    def __init__(self):
        """
        Constructor
        """
        self.wpts = []
        self.rtes = []
        self.trks = []
    
    def toXml(self):
        """
        Return XML representation.

        Out:
            This object in XML
        """
        return '<gpx version="1.1" creator="Python GPSBabel">' + \
               "".join(map(lambda x: x.toXml("wpt"), self.wpts)) + \
               "".join(map(lambda x: x.toXml("rte"), self.rtes)) + \
               "".join(map(lambda x: x.toXml("trk"), self.trks)) + \
               '</gpx>'
    
    def finalize(self):
        """
        Any post load of XML steps are placed here.
        """
        pass

class GPXWaypoint(object):
    """
    Container for wptType objects
    """
    __slots__ = ['lat', 'lon', 'ele', 'time', 'magvar', 'geoidheight', 'name', 'cmt', 'desc',
                 'src', 'link', 'sym', 'type', 'fix', 'sat', 'hdop', 'vdop', 'pdop',
                 'ageofdgpsdata', 'dgpsid']
    
    def __init__(self):
        """
        Constructor
        """
        for i in self.__slots__:
            setattr(self, i, None)
    
    def toXml(self, tag):
        """
        Return XML representation.

        In:
            tag: The XML tag to use around this object's XML representation

        Out:
            This object in XML
        """
        return '<%s lat="%s" lon="%s">' % (tag, str(self.lat), str(self.lon)) + \
               "".join(map(lambda x: '<%s>%s</%s>' % (x, getattr(self, x), x), \
                   filter(lambda x: x not in ['lat', 'lon'] and getattr(self, x) != None, self.__slots__))) + \
               '</%s>' % (tag)
    
    def finalize(self):
        """
        Any post load of XML steps are placed here.
        """
        pass

class GPXRoute(object):
    """
    Container for rteType objects.

    Note: rtepts is a list of GPXWaypoint objects
    """
    __slots__ = ['name', 'cmt', 'desc', 'src', 'link', 'number', 'type', 'rtepts']
    
    def __init__(self):
        """
        Constructor
        """
        for i in self.__slots__:
            setattr(self, i, None)
        self.rtepts = []
    
    def toXml(self, tag):
        """
        Return XML representation.

        In:
            tag: The XML tag to use around this object's XML representation

        Out:
            This object in XML
        """
        return '<%s>' % (tag) + \
               "".join(map(lambda x: '<%s>%s</%s>' % (x, getattr(self, x), x), \
                   filter(lambda x: x not in ['rtepts'] and getattr(self, x) != None, self.__slots__))) + \
               "".join(map(lambda x: x.toXml("rtept"), self.rtepts)) + \
               '</%s>' % (tag)
    
    def finalize(self):
        """
        Any post load of XML steps are placed here.
        """
        pass

class GPXTrackSeg(object):
    """
    Track segment objects.

    trkpts is a list of GPXWaypoints
    """
    __slots__ = ['trkpts']
    
    def __init__(self):
        """
        Constructor
        """
        self.trkpts = []
    
    def toXml(self):
        """
        Return XML representation.

        Out:
            This object in XML
        """
        return "<trkseg>" + \
               "".join(map(lambda x: "%s" % x.toXml("trkpt"), self.trkpts)) + \
               "</trkseg>"
    
    def finalize(self):
        """
        Any post load of XML steps are placed here.
        """
        pass

class GPXTrack(object):
    """
    Track objects

    trksegs is a list of GPXTrackSeg objects
    """
    __slots__ = ['name', 'cmt', 'desc', 'src', 'link', 'number', 'type', 'trksegs']
    
    def __init__(self):
        """
        Constructor
        """
        for i in self.__slots__:
            setattr(self, i, None)
        self.trksegs = []
    
    def toXml(self, tag):
        """
        Return XML representation.

        In:
            tag: The XML tag to use around this object's XML representation

        Out:
            This object in XML
        """
        return '<%s>' % (tag) + \
               "".join(map(lambda x: '<%s>%s</%s>' % (x, getattr(self, x), x), \
                   filter(lambda x: x not in ['trksegs'] and getattr(self, x) != None, self.__slots__))) + \
               "".join(map(lambda x: x.toXml(), self.trksegs)) + \
               '</%s>' % (tag)
    
    def finalize(self):
        """
        Any post load of XML steps are placed here.
        """
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
    """
    Utility function to parse a GPX string

    Returns the GPXData object that contains everything from the string
    """
    gpxp = GPXParser()
    xml.sax.parseString(instr, gpxp)
    gpxp.gpx.finalize()
    return gpxp.gpx
    
class GPXParser(xml.sax.handler.ContentHandler):
    """
    This is a SAX XML parser. As such, it has to track state changes so it
    knows where things are and what to do next. The states are pretty
    simplistic, so hopefully the diagram below makes sense. If not, let me
    know, and I'll improve it.

    Basically, we're always reading one of 6 things: nothing, waypoint,
    route, route waypoint, track, tracksegment, or track segment waypoint.
    Track which state we're in, and act accordingly.

    State Changes:
        nothing - waypoint - nothing
        nothing - route - waypoint - route - nothing
        nothing - track - trackseg - waypoint - trackseg - track - nothing
    States: 0=nothing, 1=wpt, 2=rte, 3=rte/wpt, 4=trk, 5=trkseg, 6=trkseg/wpt
    """
    def __init__(self):
        """
        Constructor. Clear out the character data buffer, set initial read
        state to nothing, create initial gpx object, and set the object
        stack to that GPXData object.
        """
        xml.sax.ContentHandler.__init__(self)
        self.chdata = ""
        self.read = 0
        self.gpx = GPXData()
        self.objstack = [self.gpx]
        
    def startElement(self, name, attrs):
        """
        Handle the start of a new element.

        This method assumes that all character data will be completely
        placed at the end of the element. As such, it erases any previously
        read character data.

        The methodology is as follows:
        Check the current state. From there, check possible states to
        transition to. If the new element name indicates a transition,
        transition to the new state, and copy all attributes into the new
        object.
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
        """
        Append character data to be read.

        If we're in a readable state, save this character data. Otherwise,
        discard it.
        """
        if self.read:
            self.chdata = "%s%s" % (self.chdata, ch)
    
    def endElement(self, name):
        """
        Conclude a given element.

        Check the current state. If the ending tag indicates the end of the
        current state, finalize the current object, and transition to the
        new state.

        Otherwise, attach the current character data (if any
        non-whitespace) to the same attribute as the element name on the
        current object.
        """
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

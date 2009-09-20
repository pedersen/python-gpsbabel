"""
This module is is the main module for GPSBabel. It is intended to be a
complete Python interface, allowing easy mechanisms to the developer to
control GPSBabel from within a Python application.

It is highly recommended to read the documentation on GPSBabel at
http://www.gpsbabel.org/ as the usage of this module is heavily modeled on
the general usage of GPSBabel itself.

The module properties are as follows:
    * ftypes:     A dictionary of supported file types. Each key's value is
                  a list of supported options
    * filters:    A dictionary of supported filters. Each key's value is a
                  list of supported options
    * charsets:   A dictionary of supported character sets. Each key's
                  value is a list of supported aliases for that character
                  set.
    * banner:     The full GPSBabel version string
    * version:    The portion of the version string which just is the
                  version (e.g.: 1.3.5), or None if it could not found.
    * gps:        An instance of the GPSBabel object, pre-made and ready
                  for use.

The classes in this module are grouped as follows:
    * GPSBabel: The wrapper around the gpsbabel command line
    * GPXData, GPXWaypoint, GPXRoute, GPXTrackSeg, GPXTreck: These classes
      represent the various components of a GPX file that can/will be
      captured/used by other tools. View the help from GPXData to see the
      expected hierarchy of objects and values.
    * *Exception: Custom exception classes that can be raised for specific
      error conditions when trying to run GPSBabel.
    * GPXParser: The class that parses GPX files.

There is also the utility method "gpxParse" which is used to actually parse
a gpx string into the GPX classes above, and which uses the GPXParser class.

Examples of usage:
* Store waypoints, routes, and tracks in file 'mydata.gpx' on a Garmin GPS
  on port /dev/ttyUSB0, and don't XML parse the output
    gps = GPSBabel()
    gps.addInputFile('mydata.gpx')
    gps.addOutputFile('/dev/ttyUSB0', 'garmin')
    gps.procRoutes = True
    gps.procTrack = True
    gps.procWpts = True
    gps.execCmd(parseOutput = False)

* Store all waypoints in GPXData.wpts into 'mydata.kml', and not parse
  the output
    gpxd = GPXData()
    gpxd.wpts.append(GPXWaypoint())
    gpxd.wpts[-1].lat = "45.0"
    gpxd.wpts[-1].lon = "-70.0"
    gpxd.wpts[-1].name = "WPT1"
    gps = GPSBabel()
    gps.setInGpx(gpxd)
    gps.addOutputFile('mydata.kml', 'kml')
    gps.procRoutes = False
    gps.procTrack = False
    gps.procWpts = True
    gps.execCmd(parseOutput = False)

* Read a kml file 'mydata.kml' into GPXData objects
    gps = GPSBabel()
    gps.addInputFile('mydata.kml', 'kml')
    gps.captureStdOut()
    gpxd = gps.execCmd()

* Store gpxd waypoints into a Garmin GPS on a Windows USB port, and don't
  parse the output
    gps = GPSBabel()
    gps.setInGpx(gpxd)
    gps.write('usb:', 'garmin', True, parseOutput = False)

* Read a kml file 'mydata.kml' into GPXData objects, but do not wait for
  GPSBabel to complete its run. This is likely to be used in a GUI, to
  allow for the GUI to update while GPSBabel runs in the background.
    gps = GPSBabel()
    gps.addInputFile('mydata.kml', 'kml')
    gps.captureStdOut()
    gps.execCmd(wait=False)
    while gps.checkCmd() == None: pass
    (retcode, gpxd) = gps.endCmd()

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
import datetime
import os
import os.path
import select
import subprocess
import tempfile
import time
import xml.sax
import xml.sax.handler

from decimal import Decimal


# Following code shamelessly copied from http://code.activestate.com/recipes/440554/ as of Thu, Dec 11, 2008.
import os
import subprocess
import errno
import time
import sys

PIPE = subprocess.PIPE

if subprocess.mswindows:
    from win32file import ReadFile, WriteFile
    from win32pipe import PeekNamedPipe
    import msvcrt
else:
    import select
    import fcntl

class Popen(subprocess.Popen):
    def recv(self, maxsize=None):
        return self._recv('stdout', maxsize)

    def recv_err(self, maxsize=None):
        return self._recv('stderr', maxsize)

    def send_recv(self, input='', maxsize=None):
        return self.send(input), self.recv(maxsize), self.recv_err(maxsize)

    def get_conn_maxsize(self, which, maxsize):
        if maxsize is None:
            maxsize = 1024
        elif maxsize < 1:
            maxsize = 1
        return getattr(self, which), maxsize

    def _close(self, which):
        if getattr(self, which) is not None:
            getattr(self, which).close()
            setattr(self, which, None)

    if subprocess.mswindows:
        def send(self, input):
            if not self.stdin:
                return None

            try:
                x = msvcrt.get_osfhandle(self.stdin.fileno())
                (errCode, written) = WriteFile(x, input)
            except ValueError:
                return self._close('stdin')
            except (subprocess.pywintypes.error, Exception), why:
                if why[0] in (109, errno.ESHUTDOWN):
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self.get_conn_maxsize(which, maxsize)
            if conn is None:
                return None

            try:
                x = msvcrt.get_osfhandle(conn.fileno())
                (read, nAvail, nMessage) = PeekNamedPipe(x, 0)
                if maxsize < nAvail:
                    nAvail = maxsize
                if nAvail > 0:
                    (errCode, read) = ReadFile(x, nAvail, None)
            except ValueError:
                return self._close(which)
            except (subprocess.pywintypes.error, Exception), why:
                if why[0] in (109, errno.ESHUTDOWN):
                    return self._close(which)
                raise

            if self.universal_newlines:
                read = self._translate_newlines(read)
            return read

    else:
        def send(self, input):
            if not self.stdin:
                return None

            if not select.select([], [self.stdin], [], 0)[1]:
                return 0

            try:
                written = os.write(self.stdin.fileno(), input)
            except OSError, why:
                if why[0] == errno.EPIPE: #broken pipe
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self.get_conn_maxsize(which, maxsize)
            if conn is None:
                return None

            flags = fcntl.fcntl(conn, fcntl.F_GETFL)
            if not conn.closed:
                fcntl.fcntl(conn, fcntl.F_SETFL, flags| os.O_NONBLOCK)

            try:
                if not select.select([conn], [], [], 0)[0]:
                    return ''

                r = conn.read(maxsize)
                if not r:
                    return self._close(which)

                if self.universal_newlines:
                    r = self._translate_newlines(r)
                return r
            finally:
                if not conn.closed:
                    fcntl.fcntl(conn, fcntl.F_SETFL, flags)

message = "Other end disconnected!"
# End code copy/paste

def which(cmd):
    syspath = ['.']
    if sys.platform == 'win32':
        syspath.extend(os.environ['PATH'].split(';'))
        for d in syspath:
            t = os.sep.join([d, cmd])
            for ext in ['exe', 'bat', 'com']:
                f = "%s.%s" % (t, ext)
                if os.path.exists(f) and os.access(f, os.X_OK) and not os.path.isdir(f):
                    return f
    else:
        syspath.extend(os.environ['PATH'].split(':'))
        for d in syspath:
            f = os.sep.join([d, cmd])
            if os.path.exists(f) and os.access(f, os.X_OK) and not os.path.isdir(f):
                return f
    return None

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
    """

    # Most commonly used methods here

    def __init__(self, loc="gpsbabel"):
        """
        Constructor.

        In:
            loc: String containing location of gpsbabel command. Can be
                 left blank if gpsbabel is in the user's PATH.

        Sets instance defaults.
        """
        self.__gps = None
        self.gpsbabel = loc
        self.clearChainOpts()

    def execCmd(self, cmd=None, parseOutput=True, wait=True, debug=False):
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
            wait: If True, wait until gpsbabel is done before returning. If
                False, return immediately. It is then the caller's
                responsibility to use checkCmd and endCmd, respectively,
                to perform any cleanup.
            debug: If True, and cmd is None, set the debug level to 10
                while running gpsbabel

        Out:
            (returncode, output): returncode is the result code from
            running the command (should always be 0 in case of success).
            output is either an array of lines which are the raw output (in
            cases where parseOutput is False), or a set of GPXData/etc
            objects (where parseOutput is True)

        Exceptions:
            If gpsbabel prints any data on stderr, a RuntimeError will be 
            raised with the contents of stderr
        """

        #This method calls buildCmd when cmd is None, then runs the command
        #specified by the list that is now cmd. If wait is true, it manages
        #the calling of checkCmd and encCmd for the caller.
        if cmd is None: cmd = self.buildCmd(debug)
        self.__parseOutput = parseOutput
        self.__gps = Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.__gps.universal_newlines = True
        self.__stdout = []
        self.__stderr = []
        if isinstance(self.stdindata, str):
            self.__gps.send(self.stdindata)
        else:
            out = ''
            for i in self.stdindata:
                out = '%s%s' % (out, i)
            self.__gps.send(out)
        self.__gps._close('stdin')
        if wait:
            self.__returncode = None
            while self.__returncode is None: self.checkCmd()
            return self.endCmd()
    convert=execCmd
    """
    Provide an alias to execCmd
    """

    def checkCmd(self):
        """
        Check the status of the running gpsbabel. Return None unless
        gpsbabel has exited, in which case return the exit code.
        """
        if self.__gps is None:
            return None
        self.__returncode = self.__gps.poll()
        out = self.__gps.recv(65536)
        if out is not None:
            self.__stdout.extend(filter(lambda x: len(x.strip()) > 0, out.split("\n")))
        err = self.__gps.recv_err(65536)
        if err is not None:
            self.__stderr.extend(filter(lambda x: len(x.strip()) > 0, err.split("\n")))
        return self.__returncode
    checkConvert = checkCmd

    def endCmd(self):
        """
        Get the exit code for the running gpsbabel, and the output, and
        return both.
        """
        if self.__gps is None:
            return (None, [])
        if self.checkCmd() is None:
            return (None, [])
        if self.stdoutname is not None:
            output = open(self.stdoutname).readlines()
            os.unlink(self.stdoutname)
            self.stdoutname = None
        else:
            output = self.__stdout
        if len(self.__stderr) > 0:
            raise RuntimeError("gpsbabel failure: %s" % "\n".join(self.__stderr))
        if self.autoClear: self.clearChainOpts()
        if self.__parseOutput: output = gpxParse("\n".join(output))
        self.__gps = None
        return(self.__returncode, output)
    endConvert = endCmd

    def addInputFile(self, fname, fmt="gpx", charset="UTF-8"):
        """
        Adds an input file to the processing chain.

        In:
            fname:   The name of the file to read
            fmt:     The format of the file to read
            charset: The character set to use when reading the file
        """
        self.addCharset(charset)
        self.addAction('infile', fmt, fname)

    def addInputFiles(self, files):
        """
        Add a dictionary of files to the input.

        In:
            files: A dictionary. Each key is a filename, and each value is
            a list of up to two entries. If no entries, the default file
            format will be used. If one, then it is treated as the file
            format. If two, the second is treated as the character set for
            the file.
        """
        for fname in sorted(files.keys()):
            fmt = files[fname][0] if files[fname] is not None and len(files[fname]) >= 1 else "gpx"
            charset = files[fname][1] if files[fname] is not None and len(files[fname]) >= 2 else "UTF-8"
            self.addInputFile(fname, fmt, charset)

    def addOutputFiles(self, files):
        """
        Add a dictionary of files to the input.

        In:
            files: A dictionary. Each key is a filename, and each value is
            a list of up to two entries. If no entries, the default file
            format will be used. If one, then it is treated as the file
            format. If two, the second is treated as the character set for
            the file.
        """
        for fname in sorted(files.keys()):
            fmt = files[fname][0] if files[fname] is not None and len(files[fname]) >= 1 else "gpx"
            charset = files[fname][1] if files[fname] is not None and len(files[fname]) >= 2 else "UTF-8"
            self.addOutputFile(fname, fmt, charset)

    def addOutputFile(self, fname, fmt="gpx", charset="UTF-8"):
        """
        Adds an output file to the processing chain

        In:
            fname:   The name of the file to write
            fmt:     The format of the file to write
            charset: The character set to use when writing the file
        """
        self.addCharset(charset)
        self.addAction('outfile', fmt, fname)

    def addFilter(self, fname, opts, charset="UTF-8"):
        """
        Adds an filter to the processing chain

        In:
            fname:   The name of the filter to use
            opts:    The options for the filter
            charset: The character set to use when running the filter
        """
        self.addCharset(charset)
        self.addAction('filter', fname, None, opts)

    def addCharset(self, charset):
        """
        Add a character set translation to the processing chain.

        In:
            charset: The name of the character set to use next.
        """
        self.addAction('charset', charset)

    def getPositionAwareTypes(self):
        """
        Out:
            A tupe that lists types of GPSes that Python-GPSBabel knows
            how to request the current location from. The list is formatted
            to be GUI display friendly.
        """
        return ('Garmin', 'NMEA')
    
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
        """

        #The method is simple: Set the attached GPS as the input. Capture
        #the output. Let execCmd parse the resulting output, and return the
        #resulting GPXWaypoint that is given to use by execCmd
        self.addAction('infile', gpsType.lower(), port, {'get_posn' : None})
        self.captureStdOut()
        ret, gpx = self.execCmd()
        gpx = gpx.wpts[0] if len(gpx.wpts) > 0 else None
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
        """
        #The method is beyond simple: Set the processing options. Add the
        #outfile processing, and run the resulting command.
        self.procWpts   = wpt
        self.procRoutes = route
        self.procTrack  = track
        self.addAction('outfile', fmt, fname, {})
        ret, gpx = self.execCmd(parseOutput = parseOutput)
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
        """
        #The method is beyond simple: Set the processing options. Add the
        #infile processing, set the output capture, and run the resulting
        #command.
        self.procWpts   = wpt
        self.procRoutes = route
        self.procTrack  = track
        self.addAction('infile', fmt, fname, {})
        self.captureStdOut()
        ret, gpx = self.execCmd(parseOutput = parseOutput)
        return gpx

    def setInGpx(self, gpx):
        """
        Convenience method used to set stdindata to gpx data.

        In:
            gpx: Either a string containing a valid GPX file or a
            GPXData/etc object, or an interable object that will output GPX
            when iterated over. See the GPXData/etc objects for an example
            of this.
        """
        #This method assumes that any string coming in will be a valid
        #string of XML which conforms to the GPX specification. If it does
        #not, then the eventual run of gpsbabel will fail.
        #
        #The method is simple: Set the stdindata instance variable to be
        #either the string that is passed in, or the GPXData/etc object will
        #be converted to XML and stdindata will be set to that XML data.
        #
        #Afterwards, addAction will be called to set the stdin to work
        #correctly.
        #
        #Note that no options can be set on the format using this method.
        if isinstance(gpx, str):
            self.stdindata = gpx
            self.addAction('infile', 'gpx', '-', {})
        elif isinstance(gpx, GPXData):
            self.stdindata = gpx
            self.addAction('infile', 'gpx', '-', {})
        else:
            try:
                it = iter(gpx)
                self.stdindata = gpx
                self.addAction('infile', 'gpx', '-', {})
            except TypeError:
                raise Exception("Unable to set stdin for gpsbabel. Aborting!")

    def captureStdOut(self):
        """
        Add the action to the chain of capturing stdout.
        """
        (fd, name) = tempfile.mkstemp()
        os.close(fd)
        self.stdoutname = name
        self.addAction('outfile', 'gpx', name, {'gpxver':'1.0'})

    # Important methods, though they will not be commonly used, here

    def guessFormat(self, fname):
        """
        Very basic, very incomplete, format guessing

        In:
            fname: The name of a file

        Out:
            The type of the file format that GPSBabel can use for this file
        """
        gpsnames = {".gpx":"gpx", ".kml":"kml", ".txt":"nmea"}
        ext = os.path.splitext(fname)[-1].lower()
        return gpsnames[ext] if ext in gpsnames.keys() else None

    FMT_INPUT, FMT_OUTPUT, FMT_FILE, FMT_DEVICE = range(4)
    """
    Constants used for the getFormats method.
    FMT_INPUT  : Direction, read from GPSBabel
    FMT_OUTPUT : Direction, write to GPSBabel
    FMT_FILE   : Output, write to a file
    FMT_DEVICE : Output, write to a GPS device

    """

    def getFormats(self, direction, source):
        """
        Get list of formats supported for a given direction and media type

        In:
            direction : The direction of input. Valid values are
                        FMT_INPUT and FMT_OUTPUT
            source    : The type of input/output. Valid values are FMT_FILE
                        and FMT_DEVICE
        """
        if source == self.FMT_FILE:
            if direction == self.FMT_OUTPUT: return ["gpx", "kml"]
            elif direction == self.FMT_INPUT: return ["gpx", "nmea", "sbp"]
        elif source == self.FMT_DEVICE: return ["garmin", "navilink"]

        return []

    actions = ['charset', 'infile', 'filter', 'outfile']
    """
    Valid actions which GPSBabel can use.
    """

    def addAction(self, action, fmtfilter, fname=None, opts={}):
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
        """
        #This method is actually fairly complex, mainly because this is
        #where most error checking happens. The options are checked to make
        #sure that they are compatible with the format or filter. The action
        #is checked to make sure it's a legal action. The
        #format/filter/character set is checked to make sure it's legal.
        # 
        #After all checks pass, a new entry is added to the chain list. The
        #entry is actually two dictionaries. The first describes the action,
        #and includes the type, the format/filter/character set, and the
        #filename. The second dictionary is the options. So, the entry to
        #grab the output as gpx with an snlen of 10 looks like this:
        #    chain[-1] = [
        #        { 'action' : 'outfile', 'fmtfilter': 'gpx', 'fname' : '-'},
        #        { 'snlen' : '10' }
        #        ]
        action = action.lower()
        if action not in self.actions:
            raise UnknownActionException("Error: Unknown action %s" % action)
        if action in ['infile', 'outfile'] and fname == None:
            raise MissingFilenameException('Error: Action %s requires a filename, and we have none' % action)
        if action in ['infile', 'outfile']:
            if not ftypes.has_key(fmtfilter):
                raise MissingFilefmtException('Error: File format %s is unknown' % fmtfilter)
            for key in opts.keys():
                if not key in ftypes[fmtfilter]:
                    raise InvalidOptionException('Error: File format %s has no such option %s' % (fmtfilter, key))
        if action == 'filter':
            if not filters.has_key(fmtfilter):
                raise MissingFilterException('Error: Filter %s is unknown' % fmtfilter)
            for key in opts.keys():
                if not key in filters[fmtfilter]:
                    raise InvalidOptionException('Error: Filter %s has no such option %s' % (fmtfilter, key))
        if action == 'charset':
            cfound = False
            if not charsets.has_key(fmtfilter):
                for key in charsets.keys():
                    if fmtfilter in charsets[key]: cfound = True
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
        self.stdoutname = None
        self.chain      = []
        if not hasattr(self, "autoClear"): self.autoClear = True
    clear = clearChainOpts
    """
    Provide an alias to clearChainOpts
    """

    # The following methods are meant for internal use. You are welcome to use them yourself, but they are going to be extremely uncommon

    def buildCmd(self, debug=False):
        """
        Build a list of command line and options for gpsbabel.

        In:
            debug: If true, add ["-D", "10"] to the command line

        Out:
            A list of command line parameters. Example:
                ['gpsbabel', '-p', '', '-D', '10', '-i', 'gpx', '-f', \
                    '-', '-o', 'garmin', '-F', '/dev/ttyUSB0']
        """
        #The method is simple: Make the base list, add various options as
        #specified by the flags. Loop over the actions, and add them in
        #appropriately. Return the list.
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

    The object hierarchy for the GPXData closely mirrors the XML
    representation of those objects. As such, when looking at the GPXData
    object, this is the expected representation of a .gpx/.loc file after
    it has been parsed:

    GPXData
        wpts: list of GPXWaypoint
            GPXWaypoint.__slots__ lists legal attributes
        rtes: list of GPXRoute
            GPXRoute.__slots__ lists legal attributes
                rtepts: list of GPXWaypoint
        trks: list of GPXTrack
            GPXTrack.__slots__ lists legal attributes
                trksegs: list of GPXTrackSeg
                    GPXTrackSeg.__slots__ lists legal attributes
                        trkpts: list of GPXWaypoint

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

    def __iter__(self):
        return self.next()

    def next(self):
        yield '<gpx version="1.1" creator="Python GPSBabel">'
        for wpt in self.wpts:
            wpt.xmltag = 'wpt'
            for i in wpt:
                yield i
        for rte in self.rtes:
            rte.xmltag = 'rte'
            for i in rte:
                yield i
        for trk in self.trks:
            trk.xmltag = 'trk'
            for i in trk:
                yield i
        yield '</gpx>'

    def toXml(self):
        """
        Return XML representation.

        Out:
            This object in XML
        """
        output = ""
        for i in self:
            output = "%s%s" % (output, i)
        return output

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
                 'ageofdgpsdata', 'dgpsid', 'xmltag', 'speed']

    def __init__(self):
        """
        Constructor
        """
        for i in self.__slots__:
            setattr(self, i, None)

    def __iter__(self):
        return self.next()

    def next(self):
        yield '<%s lat="%s" lon="%s">' % (self.xmltag, str(self.lat), str(self.lon))
        for attr in filter(lambda x: x not in ['lat', 'lon', 'xmltag'] and getattr(self, x) != None, self.__slots__):
            yield '<%s>%s</%s>' % (attr, getattr(self, attr), attr)
        yield '</%s>' % (self.xmltag)

    def toXml(self, tag):
        """
        Return XML representation.

        In:
            tag: The XML tag to use around this object's XML representation

        Out:
            This object in XML
        """
        self.xmltag = tag
        output = ""
        for i in self:
            output = "%s%s" % (output, i)
        return output

    def finalize(self):
        """
        Any post load of XML steps are placed here.
        """
        for i in ['lat', 'lon', 'ele', 'magvar', 'geoidheight', 'hdop', 'vdop', 'pdop', 'ageofdgpsdata', 'speed']:
            if getattr(self, i) is not None:
                setattr(self, i, Decimal(getattr(self, i)))
        for i in ['sat', 'dgpsid']:
            if getattr(self, i) is not None:
                setattr(self, i, int(getattr(self, i)))
        for i in ['time']:
            if getattr(self, i) is not None:
                setattr(self, i, datetime.datetime(*time.strptime(getattr(self, i), '%Y-%m-%dT%H:%M:%SZ')[:6]))

class GPXRoute(object):
    """
    Container for rteType objects.

    Note: rtepts is a list of GPXWaypoint objects
    """
    __slots__ = ['name', 'cmt', 'desc', 'src', 'link', 'number', 'type', 'rtepts', 'xmltag']

    def __init__(self):
        """
        Constructor
        """
        for i in self.__slots__:
            setattr(self, i, None)
        self.rtepts = []

    def __iter__(self):
        return self.next()

    def next(self):
        yield '<%s>' % (self.xmltag)
        for attr in filter(lambda x: x not in ['rtepts', 'xmltag'] and getattr(self, x) != None, self.__slots__):
            yield '<%s>%s</%s>' % (attr, getattr(self, attr), attr)
        for rte in self.rtepts:
            rte.xmltag = 'rtept'
            for i in rte:
                yield i
        yield '</%s>' % (self.xmltag)

    def toXml(self, tag):
        """
        Return XML representation.

        In:
            tag: The XML tag to use around this object's XML representation

        Out:
            This object in XML
        """
        self.xmltag = tag
        output = ""
        for i in self:
            output = "%s%s" % (output, i)
        return output

    def finalize(self):
        """
        Any post load of XML steps are placed here.
        """
        self.number = int(self.number) if self.number is not None else None


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

    def __iter__(self):
        return self.next()

    def next(self):
        yield "<trkseg>"
        for trkpt in self.trkpts:
            trkpt.xmltag = "trkpt"
            for i in trkpt:
                yield i
        yield "</trkseg>"

    def toXml(self):
        """
        Return XML representation.

        Out:
            This object in XML
        """
        output = ""
        for i in self:
            output = "%s%s" % (output, i)
        return output

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
    __slots__ = ['name', 'cmt', 'desc', 'src', 'link', 'number', 'type', 'trksegs', 'xmltag']

    def __init__(self):
        """
        Constructor
        """
        for i in self.__slots__:
            setattr(self, i, None)
        self.trksegs = []

    def __iter__(self):
        return self.next()

    def next(self):
        yield '<%s>' % (self.xmltag)
        for attr in filter(lambda x: x not in ['trksegs', 'xmltag'] and getattr(self, x) != None, self.__slots__):
            yield '<%s>%s</%s>' % (attr, getattr(self, attr), attr)
        for trkseg in self.trksegs:
            for i in trkseg:
                yield i
        yield '</%s>' % (self.xmltag)

    def toXml(self, tag):
        """
        Return XML representation.

        In:
            tag: The XML tag to use around this object's XML representation

        Out:
            This object in XML
        """
        self.xmltag = tag
        output = ""
        for i in self:
            output = "%s%s" % (output, i)
        return output

    def finalize(self):
        """
        Any post load of XML steps are placed here.
        """
        self.number = int(self.number) if self.number is not None else None

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
    This is a SAX XML parser for GPX files.
    """
    #As such, it has to track state changes so it
    #knows where things are and what to do next. The states are pretty
    #simplistic, so hopefully the diagram below makes sense. If not, let me
    #know, and I'll improve it.
    #
    #Basically, we're always reading one of 6 things: nothing, waypoint,
    #route, route waypoint, track, tracksegment, or track segment waypoint.
    #Track which state we're in, and act accordingly.
    #
    #State Changes:
    #    nothing - waypoint - nothing
    #    nothing - route - waypoint - route - nothing
    #    nothing - track - trackseg - waypoint - trackseg - track - nothing
    #States: 0=nothing, 1=wpt, 2=rte, 3=rte/wpt, 4=trk, 5=trkseg, 6=trkseg/wpt
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
        """
        #This method assumes that all character data will be completely
        #placed at the end of the element. As such, it erases any previously
        #read character data.
        #
        #The methodology is as follows:
        #Check the current state. From there, check possible states to
        #transition to. If the new element name indicates a transition,
        #transition to the new state, and copy all attributes into the new
        #object.
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
        """
        #If we're in a readable state, save this character data. Otherwise,
        #discard it.
        if self.read:
            self.chdata = "%s%s" % (self.chdata, ch)

    def endElement(self, name):
        """
        Conclude a given element.
        """
        #Check the current state. If the ending tag indicates the end of the
        #current state, finalize the current object, and transition to the
        #new state.
        #
        #Otherwise, attach the current character data (if any
        #non-whitespace) to the same attribute as the element name on the
        #current object.
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

def validateVersion(gps):
    """
    Find the version of GPSBabel in the system path and make sure it's
    supported. Raise an exception if not.
    """
    ret, gpsver = gps.execCmd([gps.gpsbabel, "-V"], parseOutput = False)
    versionstr = ""
    for line in gpsver:
        if line.strip() != "": versionstr = "%s%s" % (versionstr, line.strip())
    major, minor, patch = versionstr.split()[-1].split('.')
    assert major>='1'
    assert minor>='3'
    assert patch>='3'

    banner = versionstr
    try:
        version = versionstr.split(" ")[2]
    except:
        raise Exception('Unsupported version of GPSBabel installed. Aborting.')
check_exe = validateVersion
"""
Provide an alias to validateVersion
"""

def readOpts(gpso):
    """
    Read the supported formats/filters/character sets from the
    installed gpsbabel.
    """
    #Run gpsbabel with the -h parameter, and parse the three sections:
    #0: general help, which this method ignores
    #1: file types. Make sure to read options when reading the file
    #    types
    #2: filters. Make sure to read options when reading the filters
    #Run gpsbabel with the -l parmater, and parse the output. Character
    #set names are on lines starting with "*", and aliases are on
    #subsequent lines and the lines start with the tab character ("\t")
    ftype = ''
    ret, gps = gpso.execCmd([gpso.gpsbabel, "-h"], parseOutput = False)
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
                ftypes[ftype].append(line[:line.find(' ')].strip())
            else: # reading type name
                line = line.strip()
                ftype = line[:line.find(' ')].strip()
                ftypes[ftype] = []
        elif mode == 2:
            if line.startswith('\t '): # reading type option
                line = line.strip()
                filters[ftype].append(line[:line.find(' ')].strip())
            else: # reading type name
                line = line.strip()
                ftype = line[:line.find(' ')].strip()
                filters[ftype] = []
    charset = ''
    ret, gps = gpso.execCmd([gpso.gpsbabel, "-l"], parseOutput = False)
    for line in gps:
        line = line.rstrip()
        if line.startswith('*'):
            charset = line[line.find(' ')+1:]
            charsets[charset] = []
        if line.startswith('\t'):
            charsets[charset].extend(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), line.strip().split(','))))


version = None
banner = None
ftypes = {}
filters = {}
charsets = {}
print ",".join(sys.argv)
gps = GPSBabel(which('gpsbabel'))
if len(sys.argv) > 0 and sys.argv[0].lower().endswith('setup.py'):
    pass
else:
    validateVersion(gps)
    readOpts(gps)

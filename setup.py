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

from distutils.core import setup
import os, os.path, sys

if sys.platform.startswith('win'):
    try:
        import win32file
    except ImportError:
        print "Without win32file, python-gpsbabel will fail on Windows. Aborting."
        print "Get it at http://sourceforge.net/projects/pywin32/"
        sys.exit(1)
    try:
        import win32pipe
    except ImportError:
        print "Without win32pipe, python-gpsbabel will fail on Windows. Aborting."
        print "Get it at http://sourceforge.net/projects/pywin32/"
        sys.exit(1)

datafiles = []
setup(name='gpsbabel',
        version="0.8.2",
        description='Python wrapper for GPSBabel project',
        author='Michael Pedersen',
        author_email='m.pedersen@icelus.org ',
        url='http://www.cache901.org/developers-corner/python-gpsbabel',
        py_modules=['gpsbabel', ]
    )


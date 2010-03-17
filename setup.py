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

from setuptools import setup
import os, os.path, sys

if sys.platform.startswith('win'):
    install_reqs = ['pywin32']
else:
    install_reqs = []

setup(name='gpsbabel',
        version="1.0.0",
        description='Python wrapper for GPSBabel project',
        author='Michael Pedersen',
        author_email='m.pedersen@icelus.org ',
        install_requires = install_reqs,
        url='http://code.google.com/p/python-gpsbabel/',
        py_modules=['gpsbabel', ]
    )


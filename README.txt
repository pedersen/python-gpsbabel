Python-GPSBabel: A Python wrapper around the GPSBabel command.
Distributed under terms of the GNU GPL v2 or greater.

This package requires Python 2.5 and a supported version of GPSBabel
installed on your system. Supported versions are 1.3.3, 1.3.5, and 1.3.6.

GPSBabel should be installed in such a way that typing "gpsbabel -V" on the
command line/Terminal/Command Prompt will produce valid output. This is an
absolute requirement, and any programs which import the gpsbabel module will
fail to start without this being done.

This is purely a library package. It has no command line tools or usage. It
is meant for developers to help them extend GPSBabel using Python.

==============
Installation
==============
Installation is accomplished from the command line.

user@desktop:~/gpsbabel$ python setup.py install

The above command needs to be performed as root.

==============
For Developers
==============

This module was developed with a strong preference for using GPX files. As
such, there are objects for each of the major data types in a GPX files, as
well as built conversion methods to translate to and from GPX data.

Please examine the documentation embedded in the module for full details on
how to use this module. This can be accomplished by doing the following at
a command prompt:

user@desktop:~$ python
Python 2.5.2 (r252:60911, Sep 29 2008, 21:15:13) 
[GCC 4.3.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import gpsbabel
>>> help(gpsbabel)

You will then receive several screenfuls of documentation and examples you
may use.

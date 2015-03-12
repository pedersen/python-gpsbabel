python-gpsbabel is a simple wrapper around the GPS Babel executable. Works on Windows, Linux, and Mac.

This wrapper is believed to be pretty much feature complete and bug-free, though the version number is kept low since others might have more features to add.

At this time, python-gpsbabel can do the following:

  * Create arbitrary chains, including changing character sets, applying filters, and readin and writing files in any format supported by GPSBabel.
  * It can capture the output of any GPSBabel command.
  * If that output is in the GPX format, it can convert it to something usable by a calling program.
  * It can take the same sort of objects it creates, and send them as input to GPSBabel.
  * It is easily capable of support additional versions of GPSBabel when they come out.
  * It can read from and write to supported GPS units.

As a result, it is an extremely useful solution to getting Cache901 to talk to GPS units.
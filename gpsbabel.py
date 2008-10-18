"""
This module is is the main module for GPSBabel. It is intended to be a complete Python interface, allowing easy mechanisms to the developer to control GPSBabel from within a Python application.
"""
"""
GPSBabel Version 1.3.5.  http://www.gpsbabel.org

Usage:
    gpsbabel [options] -i INTYPE -f INFILE [filter] -o OUTTYPE -F OUTFILE
    gpsbabel [options] -i INTYPE -o OUTTYPE INFILE [filter] OUTFILE

    Converts GPS route and waypoint data from one format type to another.
    The input type and filename are specified with the -i INTYPE
    and -f INFILE options. The output type and filename are specified
    with the -o OUTTYPE and -F OUTFILE options.
    If '-' is used for INFILE or OUTFILE, stdin or stdout will be used.

    In the second form of the command, INFILE and OUTFILE are the
    first and second positional (non-option) arguments.

    INTYPE and OUTTYPE must be one of the supported file types and
    may include options valid for that file type.  For example:
      'gpx', 'gpx,snlen=10' and 'ozi,snlen=10,snwhite=1'
    (without the quotes) are all valid file type specifications.

Options:
    -p               Preferences file (gpsbabel.ini)
    -s               Synthesize shortnames
    -r               Process route information
    -t               Process track information
    -T               Process realtime tracking information
    -w               Process waypoint information [default]
    -b               Process command file (batch mode)
    -c               Character set for next operation
    -N               No smart icons on output
    -x filtername    Invoke filter (placed between inputs and output) 
    -D level         Set debug level [0]
    -l               Print GPSBabel builtin character sets and exit
    -h, -?           Print detailed help and exit
    -V               Print GPSBabel version and exit

File Types (-i and -o options):
	alantrl               Alan Map500 tracklogs (.trl)
	alanwpr               Alan Map500 waypoints and routes (.wpr)
	baroiq                Brauniger IQ Series Barograph Download
	cambridge             Cambridge/Winpilot glider software
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	cst                   CarteSurTable data file
	cetus                 Cetus for Palm/OS
	  dbname                Database name 
	  appendicon            (0/1) Append icon_descr to description 
	coastexp              CoastalExplorer XML
	csv                   Comma separated values
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	compegps              CompeGPS data files (.wpt/.trk/.rte)
	  deficon               Default icon name 
	  index                 Index of route/track to write (if more the one in  
	  radius                Give points (waypoints/route points) a default rad 
	  snlen                 Length of generated shortnames (default 16) 
	copilot               CoPilot Flight Planner for Palm/OS
	coto                  cotoGPS for Palm/OS
	  zerocat               Name of the 'unassigned' category 
	axim_gpb              Dell Axim Navigation System (.gpb) file format
	an1                   DeLorme .an1 (drawing) file
	  type                  Type of .an1 file 
	  road                  Road type changes 
	  nogc                  (0/1) Do not add geocache data to description 
	  nourl                 (0/1) Do not add URLs to description 
	  deficon               Symbol to use for point data 
	  color                 Color for lines or mapnotes 
	  zoom                  Zoom level to reduce points 
	  wpt_type              Waypoint type 
	  radius                Radius for circles 
	gpl                   DeLorme GPL
	saplus                DeLorme Street Atlas Plus
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	saroute               DeLorme Street Atlas Route
	  turns_important       (0/1) Keep turns if simplify filter is used 
	  turns_only            (0/1) Only read turns; skip all other points 
	  split                 (0/1) Split into multiple routes at turns 
	  controls              Read control points as waypoint/route/none 
	  times                 (0/1) Synthesize track times 
	xmap                  DeLorme XMap HH Native .WPT
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	xmap2006              DeLorme XMap/SAHH 2006 Native .TXT
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	xmapwpt               DeLorme XMat HH Street Atlas USA .WPT (PPC)
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	destinator_itn        Destinator Itineraries (.dat)
	destinator_poi        Destinator Points of Interest (.dat)
	destinator_trl        Destinator TrackLogs (.dat)
	easygps               EasyGPS binary format
	exif                  Embedded Exif-GPS data (.jpg)
	  filename              (0/1) Set waypoint name to source filename. 
	igc                   FAI/IGC Flight Recorder Data Format
	  timeadj               (integer sec or 'auto') Barograph to GPS time diff 
	gpssim                Franson GPSGate Simulation
	  wayptspd              Default speed for waypoints (knots/hr) 
	  split                 (0/1) Split input into separate files 
	fugawi                Fugawi
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	g7towin               G7ToWin data files (.g7t)
	garmin301             Garmin 301 Custom position and heartrate
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	glogbook              Garmin Logbook XML
	gdb                   Garmin MapSource - gdb
	  cat                   Default category on output (1..16) 
	  bitscategory          Bitmap of categories 
	  ver                   Version of gdb file to generate (1..3) 
	  via                   (0/1) Drop route points that do not have an equivalent w 
	  roadbook              (0/1) Include major turn points (with description) from  
	mapsource             Garmin MapSource - mps
	  snlen                 Length of generated shortnames 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  mpsverout             Version of mapsource file to generate (3,4,5) 
	  mpsmergeout           (0/1) Merge output with existing file 
	  mpsusedepth           (0/1) Use depth values on output (default is ignore) 
	  mpsuseprox            (0/1) Use proximity values on output (default is ignore) 
	garmin_txt            Garmin MapSource - txt (tab delimited)
	  date                  Read/Write date format (i.e. yyyy/mm/dd) 
	  datum                 GPS datum (def. WGS 84) 
	  dist                  Distance unit [m=metric, s=statute] 
	  grid                  Write position using this grid. 
	  prec                  Precision of coordinates 
	  temp                  Temperature unit [c=Celsius, f=Fahrenheit] 
	  time                  Read/Write time format (i.e. HH:mm:ss xx) 
	  utc                   Write timestamps with offset x to UTC time 
	pcx                   Garmin PCX5
	  deficon               Default icon name 
	  cartoexploreur        (0/1) Write tracks compatible with Carto Exploreur 
	garmin_poi            Garmin POI database
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	garmin_gpi            Garmin Points of Interest (.gpi)
	  alerts                (0/1) Enable alerts on speed or proximity distance 
	  bitmap                Use specified bitmap on output 
	  category              Default category on output 
	  hide                  (0/1) Don't show gpi bitmap on device 
	  descr                 (0/1) Write description to address field 
	  notes                 (0/1) Write notes to address field 
	  position              (0/1) Write position to address field 
	  proximity             Default proximity 
	  sleep                 After output job done sleep n second(s) 
	  speed                 Default speed 
	  unique                (0/1) Create unique waypoint names (default = yes) 
	  units                 Units used for names with @speed ('s'tatute or 'm' 
	garmin                Garmin serial/USB protocol
	  snlen                 Length of generated shortnames 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  deficon               Default icon name 
	  get_posn              (0/1) Return current position as a waypoint 
	  power_off             (0/1) Command unit to power itself down 
	  resettime             (0/1) Sync GPS time to computer time 
	  category              Category number to use for written waypoints 
	  bitscategory          Bitmap of categories 
	gtrnctr               Garmin Training Centerxml
	geo                   Geocaching.com .loc
	  deficon               Default icon name 
	  nuke_placer           (0/1) Omit Placer name 
	gcdb                  GeocachingDB for Palm/OS
	ggv_log               Geogrid Viewer tracklogs (.log)
	geonet                GEOnet Names Server (GNS)
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	geoniche              GeoNiche .pdb
	  dbname                Database name (filename) 
	  category              Category name (Cache) 
	dg-100                GlobalSat DG-100/BT-335 Download
	  erase                 (0/1) Erase device data after download 
	kml                   Google Earth (Keyhole) Markup Language
	  deficon               Default icon name 
	  lines                 (0/1) Export linestrings for tracks and routes 
	  points                (0/1) Export placemarks for tracks and routes 
	  line_width            Width of lines, in pixels 
	  line_color            Line color, specified in hex AABBGGRR 
	  floating              (0/1) Altitudes are absolute and not clamped to ground 
	  extrude               (0/1) Draw extrusion line from trackpoint to ground 
	  trackdata             (0/1) Include extended data for trackpoints (default = 1 
	  trackdirection        (0/1) Indicate direction of travel in track icons (defau 
	  units                 Units used when writing comments ('s'tatute or 'm' 
	  labels                (0/1) Display labels on track and routepoints  (default  
	  max_position_point    Retain at most this number of position points  (0  
	google                Google Maps XML
	gpilots               GpilotS
	  dbname                Database name 
	gtm                   GPS TrackMaker
	arc                   GPSBabel arc filter file
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	gpsdrive              GpsDrive Format
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	gpsdrivetrack         GpsDrive Format for Tracks
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	gpsman                GPSman
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	gpspilot              GPSPilot Tracker for Palm/OS
	  dbname                Database name 
	gpsutil               gpsutil
	gpx                   GPX XML
	  snlen                 Length of generated shortnames 
	  suppresswhite         (0/1) No whitespace in generated shortnames 
	  logpoint              (0/1) Create waypoints from geocache log entries 
	  urlbase               Base URL for link tag in output 
	  gpxver                Target GPX version for output 
	hiketech              HikeTech
	holux                 Holux (gm-100) .wpo Format
	hsandv                HSA Endeavour Navigator export File
	html                  HTML Output
	  stylesheet            Path to HTML style sheet 
	  encrypt               (0/1) Encrypt hints using ROT13 
	  logs                  (0/1) Include groundspeak logs if present 
	  degformat             Degrees output as 'ddd', 'dmm'(default) or 'dms' 
	  altunits              Units for altitude (f)eet or (m)etres 
	ignrando              IGN Rando track files
	  index                 Index of track to write (if more the one in source 
	ktf2                  Kartex 5 Track File
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	kwf2                  Kartex 5 Waypoint File
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	kompass_tk            Kompass (DAV) Track (.tk)
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	kompass_wp            Kompass (DAV) Waypoints (.wp)
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	psitrex               KuDaTa PsiTrex text
	lowranceusr           Lowrance USR
	  ignoreicons           (0/1) Ignore event marker icons on read 
	  writeasicons          (0/1) Treat waypoints as icons on write 
	  merge                 (0/1) (USR output) Merge into one segmented track 
	  break                 (0/1) (USR input) Break segments into separate tracks 
	maggeo                Magellan Explorist Geocaching
	mapsend               Magellan Mapsend
	  trkver                MapSend version TRK file to generate (3,4) 
	magnav                Magellan NAV Companion for Palm/OS
	magellanx             Magellan SD files (as for eXplorist)
	  deficon               Default icon name 
	  maxcmts               Max number of comments to write (maxcmts=200) 
	magellan              Magellan SD files (as for Meridian)
	  deficon               Default icon name 
	  maxcmts               Max number of comments to write (maxcmts=200) 
	magellan              Magellan serial protocol
	  deficon               Default icon name 
	  maxcmts               Max number of comments to write (maxcmts=200) 
	  baud                  Numeric value of bitrate (baud=4800) 
	  noack                 (0/1) Suppress use of handshaking in name of speed 
	  nukewpt               (0/1) Delete all waypoints 
	ik3d                  MagicMaps IK3D project file (.ikt)
	tef                   Map&Guide 'TourExchangeFormat' XML
	  routevia              (0/1) Include only via stations in route 
	mag_pdb               Map&Guide to Palm/OS exported files (.pdb)
	mapconverter          Mapopolis.com Mapconverter CSV
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	mxf                   MapTech Exchange Format
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	msroute               Microsoft AutoRoute 2002 (pin/route reader)
	msroute               Microsoft Streets and Trips (pin/route reader)
	s_and_t               Microsoft Streets and Trips 2002-2007
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	bcr                   Motorrad Routenplaner (Map&Guide) .bcr files
	  index                 Index of route to write (if more the one in source 
	  name                  New name for the route 
	  radius                Radius of our big earth (default 6371000 meters) 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	psp                   MS PocketStreets 2002 Pushpin
	mtk-bin               MTK Logger (iBlue 747,...) Binary File Format
	  csv                   MTK compatible CSV output file 
	mtk                   MTK Logger (iBlue 747,Qstarz BT-1000,...) download
	  erase                 (0/1) Erase device data after download 
	  csv                   MTK compatible CSV output file 
	tpg                   National Geographic Topo .tpg (waypoints)
	  datum                 Datum (default=NAD27) 
	tpo2                  National Geographic Topo 2.x .tpo
	tpo3                  National Geographic Topo 3.x/4.x .tpo
	navicache             Navicache.com XML
	  noretired             (0/1) Suppress retired geocaches 
	nmn4                  Navigon Mobile Navigator .rte files
	  index                 Index of route to write (if more the one in source 
	navilink              NaviGPS GT-11/BGT-11 Download
	  nuketrk               (0/1) Delete all track points 
	  nukerte               (0/1) Delete all routes 
	  nukewpt               (0/1) Delete all waypoints 
	  power_off             (0/1) Command unit to power itself down 
	dna                   Navitrak DNA marker format
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	netstumbler           NetStumbler Summary File (text)
	  nseicon               Non-stealth encrypted icon name 
	  nsneicon              Non-stealth non-encrypted icon name 
	  seicon                Stealth encrypted icon name 
	  sneicon               Stealth non-encrypted icon name 
	  snmac                 (0/1) Shortname is MAC address 
	nima                  NIMA/GNIS Geographic Names File
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	nmea                  NMEA 0183 sentences
	  snlen                 Max length of waypoint name to write 
	  gprmc                 (0/1) Read/write GPRMC sentences 
	  gpgga                 (0/1) Read/write GPGGA sentences 
	  gpvtg                 (0/1) Read/write GPVTG sentences 
	  gpgsa                 (0/1) Read/write GPGSA sentences 
	  date                  Complete date-free tracks with given date (YYYYMMD 
	  get_posn              (0/1) Return current position as a waypoint 
	  pause                 Decimal seconds to pause between groups of strings 
	  append_positioning    (0/1) Append realtime positioning data to the output fil 
	  baud                  Speed in bits per second of serial port (baud=4800 
	  gisteq                (0/1) Write tracks for Gisteq Phototracker 
	lmx                   Nokia Landmark Exchange
	osm                   OpenStreetMap data files
	  tag                   Write additional way tag key/value pairs 
	  tagnd                 Write additional node tag key/value pairs 
	ozi                   OziExplorer
	  pack                  (0/1) Write all tracks into one file 
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  wptfgcolor            Waypoint foreground color 
	  wptbgcolor            Waypoint background color 
	  proximity             Proximity distance 
	palmdoc               PalmDoc Output
	  nosep                 (0/1) No separator lines between waypoints 
	  dbname                Database name 
	  encrypt               (0/1) Encrypt hints with ROT13 
	  logs                  (0/1) Include groundspeak logs if present 
	  bookmarks_short       (0/1) Include short name in bookmarks 
	pathaway              PathAway Database for Palm/OS
	  date                  Read/Write date format (i.e. DDMMYYYY) 
	  dbname                Database name 
	  deficon               Default icon name 
	  snlen                 Length of generated shortnames 
	quovadis              Quovadis
	  dbname                Database name 
	raymarine             Raymarine Waypoint File (.rwf)
	  location              Default location 
	cup                   See You flight analysis data
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	sportsim              Sportsim track files (part of zipped .ssz files)
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	stmsdf                Suunto Trek Manager (STM) .sdf files
	  index                 Index of route (if more the one in source) 
	stmwpp                Suunto Trek Manager (STM) WaypointPlus files
	  index                 Index of route/track to write (if more the one in  
	xol                   Swiss Map # (.xol) format
	openoffice            Tab delimited fields useful for OpenOffice, Plotic
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	text                  Textual Output
	  nosep                 (0/1) Suppress separator lines between waypoints 
	  encrypt               (0/1) Encrypt hints using ROT13 
	  logs                  (0/1) Include groundspeak logs if present 
	  degformat             Degrees output as 'ddd', 'dmm'(default) or 'dms' 
	  altunits              Units for altitude (f)eet or (m)etres 
	  splitoutput           (0/1) Write each waypoint in a separate file 
	tomtom_itn            TomTom Itineraries (.itn)
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	tomtom_asc            TomTom POI file (.asc)
	  snlen                 Max synthesized shortname length 
	  snwhite               (0/1) Allow whitespace synth. shortnames 
	  snupper               (0/1) UPPERCASE synth. shortnames 
	  snunique              (0/1) Make synth. shortnames unique 
	  urlbase               Basename prepended to URL on output 
	  prefer_shortnames     (0/1) Use shortname instead of description 
	  datum                 GPS datum (def. WGS 84) 
	tomtom                TomTom POI file (.ov2)
	tmpro                 TopoMapPro Places File
	dmtlog                TrackLogs digital mapping (.trl)
	  index                 Index of track (if more the one in source) 
	tiger                 U.S. Census Bureau Tiger Mapping Service
	  nolabels              (0/1) Suppress labels on generated pins 
	  genurl                Generate file with lat/lon for centering map 
	  margin                Margin for map.  Degrees or percentage 
	  snlen                 Max shortname length when used with -s 
	  oldthresh             Days after which points are considered old 
	  oldmarker             Marker type for old points 
	  newmarker             Marker type for new points 
	  suppresswhite         (0/1) Suppress whitespace in generated shortnames 
	  unfoundmarker         Marker type for unfound points 
	  xpixels               Width in pixels of map 
	  ypixels               Height in pixels of map 
	  iconismarker          (0/1) The icon description is already the marker 
	unicsv                Universal csv with field structure in first line
	  datum                 GPS datum (def. WGS 84) 
	  grid                  Write position using this grid. 
	  utc                   Write timestamps with offset x to UTC time 
	vcard                 Vcard Output (for iPod)
	  encrypt               (0/1) Encrypt hints using ROT13 
	vidaone               VidaOne GPS for Pocket PC (.gpb)
	vitosmt               Vito Navigator II tracks
	vitovtt               Vito SmartMap tracks (.vtt)
	wfff                  WiFiFoFum 2.0 for PocketPC XML
	  aicicon               Infrastructure closed icon name 
	  aioicon               Infrastructure open icon name 
	  ahcicon               Ad-hoc closed icon name 
	  ahoicon               Ad-hoc open icon name 
	  snmac                 (0/1) Shortname is MAC address 
	wbt-bin               Wintec WBT-100/200 Binary File Format
	wbt                   Wintec WBT-100/200 GPS Download
	  erase                 (0/1) Erase device data after download 
	wbt-tk1               Wintec WBT-201/G-Rays 2 Binary File Format
	yahoo                 Yahoo Geocode API data
	  addrsep               String to separate concatenated address fields (de 

Supported data filters:
	arc                   Include Only Points Within Distance of Arc        
	  file                  File containing vertices of arc (required)
	  distance              Maximum distance from arc (required)
	  exclude               Exclude points close to the arc 
	  points                Use distance from vertices not lines 
	discard               Remove unreliable points with high hdop or vdop   
	  hdop                  Suppress waypoints with higher hdop 
	  vdop                  Suppress waypoints with higher vdop 
	  hdopandvdop           Link hdop and vdop supression with AND 
	  sat                   Minimium sats to keep waypoints 
	duplicate             Remove Duplicates                                 
	  shortname             Suppress duplicate waypoints based on name 
	  location              Suppress duplicate waypoint based on coords 
	  all                   Suppress all instances of duplicates 
	  correct               Use coords from duplicate points 
	interpolate           Interpolate between trackpoints                   
	  time                  Time interval in seconds 
	  distance              Distance interval in miles or kilometers 
	  route                 Interpolate routes instead 
	nuketypes             Remove all waypoints, tracks, or routes           
	  waypoints             Remove all waypoints from data stream 
	  tracks                Remove all tracks from data stream 
	  routes                Remove all routes from data stream 
	polygon               Include Only Points Inside Polygon                
	  file                  File containing vertices of polygon (required)
	  exclude               Exclude points inside the polygon 
	position              Remove Points Within Distance                     
	  distance              Maximum positional distance (required)
	  all                   Suppress all points close to other points 
	radius                Include Only Points Within Radius                 
	  lat                   Latitude for center point (D.DDDDD) (required)
	  lon                   Longitude for center point (D.DDDDD) (required)
	  distance              Maximum distance from center (required)
	  exclude               Exclude points close to center 
	  nosort                Inhibit sort by distance to center 
	  maxcount              Output no more than this number of points 
	  asroute               Put resulting waypoints in route of this name 
	simplify              Simplify routes                                   
	  count                 Maximum number of points in route 
	  error                 Maximum error 
	  crosstrack            Use cross-track error (default) 
	  length                Use arclength error 
	sort                  Rearrange waypoints by resorting                  
	  gcid                  Sort by numeric geocache ID 
	  shortname             Sort by waypoint short name 
	  description           Sort by waypoint description 
	  time                  Sort by time 
	stack                 Save and restore waypoint lists                   
	  push                  Push waypoint list onto stack 
	  pop                   Pop waypoint list from stack 
	  swap                  Swap waypoint list with <depth> item on stack 
	  copy                  (push) Copy waypoint list 
	  append                (pop) Append list 
	  discard               (pop) Discard top of stack 
	  replace               (pop) Replace list (default) 
	  depth                 (swap) Item to use (default=1) 
	reverse               Reverse stops within routes                       
	track                 Manipulate track lists                            
	  move                  Correct trackpoint timestamps by a delta 
	  pack                  Pack all tracks into one 
	  split                 Split by date or time interval (see README) 
	  sdistance             Split by distance 
	  merge                 Merge multiple tracks for the same way 
	  name                  Use only track(s) where title matches given name 
	  start                 Use only track points after this timestamp 
	  stop                  Use only track points before this timestamp 
	  title                 Basic title for new track(s) 
	  fix                   Synthesize GPS fixes (PPS, DGPS, 3D, 2D, NONE) 
	  course                Synthesize course 
	  speed                 Synthesize speed 
	transform             Transform waypoints into a route, tracks into rout
	  wpt                   Transform track(s) or route(s) into waypoint(s) [R 
	  rte                   Transform waypoint(s) or track(s) into route(s) [W 
	  trk                   Transform waypoint(s) or route(s) into tracks(s) [ 
	  del                   Delete source data after transformation 
"""
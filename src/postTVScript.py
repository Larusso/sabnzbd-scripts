#!/usr/bin/env python
#sabnzbd post script for tv show episodes
#the tv show epsiode needs to be sorted in its own sub folder, and renamed to Show-S0XE0X.ext
#this makes some things a little bit easier.
#checks if the episode is allready downloaded. If true, then check if the current
#release has a better quality (REPACK or WEB)
#example:
#
#The Firm S01E05 720p WEB DL DD5 1 H 264 CtrlHD
#
#
#The first parameter (result-dir)  = /mnt/usbdisk1/video/tv shows/The Firm/Season 1
#The second parameter (nzb-name)   = The Firm S01E05 720p WEB DL DD5 1 H 264 CtrlHD.nzb
#The third parameter (nice name)   = The Firm S01E05 720p WEB DL DD5 1 H 264 CtrlHD
#The fourth parameter (newzbin-id) =
#The fifth parameter (category)    = tv
#The sixth parameter (group)       = alt.binaries.hdtv
#The seventh parameter (status)    = 0
#


import sys
import tvEpisodeCheck
import log

if len( sys.argv ) < 7:
	print "Error is this script called from sabnzdb?"
	sys.exit( )
else:
	log.print_log( [ 'param1 (result-dir)', sys.argv[ 1 ] ] )
	log.print_log( [ 'param2 (nzb-name)', sys.argv[ 2 ] ] )
	log.print_log( [ 'param3 (nice name)', sys.argv[ 3 ] ] )
	log.print_log( [ 'param4 (newzbin-id)', sys.argv[ 4 ] ] )
	log.print_log( [ 'param5 (category)', sys.argv[ 5 ] ] )
	log.print_log( [ 'param6 (group)', sys.argv[ 6 ] ] )
	log.print_log( [ 'param7 (status)', sys.argv[ 7 ] ] )

	tvScrap = tvEpisodeCheck.TVEpisodeCheck( )
	exitCode = tvScrap.executeEpisodeCheck( sys.argv[ 1 ], sys.argv[ 3 ] )
	sys.exit( exitCode )

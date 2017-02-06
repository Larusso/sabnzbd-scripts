#!/usr/bin/python

###############################################################################
# PLEASE DO NOT REMOVE
#
# Author: Anchal 'Nacho' Nigam (and lots of help from #python on irc.freenode.net)
# E-Mail: emailyoumust@gmail.com
# Date:   February 1, 2010
###############################################################################

###############################################################################
# CONFIG START
# for explanation go to:
# https://sites.google.com/site/imthenachoman/programming/os-x-sabnzbd-handbrake-and-itunes-post-processing-script
###############################################################################

IS_LION = True

DATE_TIME_FORMAT = "[ %Y-%m-%d @ %H:%M:%S ]  "
SEPARATOR = " : "
PRINT_CONFIG = True

HANDBRAKE_PATH = "/usr/bin/HandBrakeCLI"
HANDBRAKE_PARAMATERS_BEFORE_PRESET = False
HANDBRAKE_PARAMATERS_AFTER_PRESET = False
HANDBRAKE_PRESET = "iPhone 4"
HANDBRAKE_COMMAND_OUTPUT = False
HANDBRAKE_ALL_AUDIO = True

FILE_TYPES = [ "*.avi", "*.mkv" ]
OUTPUT_EXTENSION = "mp4"
OUTPUT_PREFIX = ""
OUTPUT_POSTFIX = " - iPhone"
OUTPUT_DIRECTORY = False

POST_PROCESSING = True
POST_PROCESSING_COMMAND = 'ls -la "{directory}" "{filename}"'
POST_PROCESSING_OUTPUT = True

IMPORT_TO_ITUNES = True
TV_FORMAT = "^(?P<show>.*) - (?P<season_number>\d+)x(?P<episode_number>\d+) - (?P<episode_ID>.*)$"
DELETE_AFTER_IMPORT = True

DELETE_ORIGINAL = False

OUTPUT_APPEND = False

###############################################################################
# CONFIG END
###############################################################################

###############################################################################
# MAIN PROGRAM
###############################################################################

import sys

if( not IS_LION ):
    # Prior to Snow Leoprd this script does not work well with the current default python path SabNZBD sets
    # Set it to the same python path as OS X defaults

    osx_python_path = [
        sys.path[0],
        "/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python26.zip",
        "/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6",
        "/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/plat-darwin",
        "/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/plat-mac",
        "/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/plat-mac/lib-scriptpackages",
        "/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python",
        "/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-tk",
        "/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-old",
        "/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/lib-dynload",
        "/Library/Python/2.6/site-packages",
        "/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/PyObjC",
        "/System/Library/Frameworks/Python.framework/Versions/2.6/Extras/lib/python/wx-2.8-mac-unicode"
    ]
    sys.path = osx_python_path

import glob, os, re, subprocess, shlex
from time import strftime

def print_log( l ):
    print strftime( DATE_TIME_FORMAT ) + SEPARATOR.join( map( str, l ) )

def get_audio_track_list( input_file ):
    handbrake_command = [ HANDBRAKE_PATH, "-i", input_file, "-t", "0" ]
    stdout = subprocess.PIPE
    stderr = subprocess.STDOUT
    p = subprocess.Popen( handbrake_command, stdout = stdout, stderr = stderr )
    ( stdout, stderr ) = p.communicate()
    
    if( p.wait() == 0 ):
        out = re.sub( r'(.|\n)*audio tracks:\n', '', stdout )
        out = re.sub( r'\n\s+\+\s+subtitle tracks(.|\n)*', '', out )
        out = re.split( '\n', out )
        return ",".join( map( str, range( 1, len( out ) + 1 ) ) ) if len( out ) > 1 else "1"
    return "1"

def post_process( filename, directory ):
    post_process_command = shlex.split( POST_PROCESSING_COMMAND.format( **locals() ) )
    stdout = None if POST_PROCESSING_OUTPUT else subprocess.PIPE
    stderr = None if POST_PROCESSING_OUTPUT else subprocess.STDOUT
    p = subprocess.Popen( post_process_command, stdout = stdout, stderr = stderr )
    ( stdout, stderr ) = p.communicate()
    return ( p.wait(), stdout )

def check_if_in_itunes( filename ):
    applescript = ""
    applescript += 'tell application "iTunes"' + "\n"
    applescript += "\t" + 'get (count of (tracks of playlist "Library" whose description is "{filename}"))'.format( **locals() ) + "\n"
    applescript += 'end tell' + "\n"
    
    stdout = subprocess.PIPE
    stderr = subprocess.STDOUT
    p = subprocess.Popen( [ "osascript", "-e", applescript ], stdout = stdout, stderr = stderr )
    ( stdout, stderr ) = p.communicate()
    
    return ( p.wait(), stdout.rstrip() )

def import_in_itunes( filename, output_file ):
    applescript = ""
    applescript += 'tell application "iTunes"' + "\n"
    applescript += "\t" + 'set posix_path to "{output_file}"'.format( **locals() ) + "\n"
    applescript += "\t" + 'set mac_path to posix_path as POSIX file' + "\n"
    applescript += "\t" + 'set video to ( add mac_path )' + "\n"
    print_log( [ "\t\t" + "Name".ljust( 15 ), filename ] )
    applescript += "\t" + 'set name of video to "{filename}"'.format( **locals() ) + "\n"
    applescript += "\t" + 'set description of video to "{filename}"'.format( **locals() ) + "\n"
    
    if( category == "tv" ):
        print_log( [ "\t\t" + "Type".ljust( 15 ), "TV Show" ] )
        applescript += "\t" + 'set video kind of video to TV Show' + "\n"
        tv_details = re.match( TV_FORMAT, filename )
        if( tv_details != None ):
            tv_details = tv_details.groupdict()
            for key in tv_details:
                print_log( [ "\t\t" + key.replace( '_', ' ' ).ljust( 15 ), tv_details[key] ] )
                applescript += "\t" + 'set {0} of video to "{1}"'.format( key.replace( '_', ' ' ), tv_details[key] ) + "\n"
            
            # fix for iOS 4.2
            applescript += "\t" + 'set artist of video to "{0}"'.format( tv_details['show'] ) + "\n"
            applescript += "\t" + 'set track number of video to "{0}"'.format( tv_details['episode_number'] ) + "\n"
            applescript += "\t" + 'set name of video to "{0}"'.format( tv_details['episode_ID'] ) + "\n"
        else:
            print_log( [ "\t\t" + "ERROR".ljust( 15 ), "TV_FORMAT does not match output file name" ] )
    else:
        print_log( [ "\t\t" + "Type".ljust( 15 ), "Movie" ] )
	
    applescript += 'end tell' + "\n"
    return subprocess.Popen( [ "osascript", "-e", applescript ] ).wait()    

if( len( sys.argv ) == 3 ):
    final_directory = sys.argv[1]
    category = sys.argv[2]
    nzb_id = ""
elif( len( sys.argv ) == 8 ):
    final_directory = sys.argv[1]
    category = sys.argv[5]
    nzb_id = sys.argv[4]
else:
    print >> sys.stderr, "ERROR: Invalid number of arguments"
    print >> sys.stderr, sys.argv
    exit( 1 )

if( not OUTPUT_DIRECTORY ):
    OUTPUT_DIRECTORY = final_directory

print_log( [ "NZB ID".ljust( 30 ), nzb_id ] )
print_log( [ "Category".ljust( 30 ), category ] )
print_log( [ "Final directory".ljust( 30 ), final_directory ] )
print_log( [ "Output directory".ljust( 30 ), OUTPUT_DIRECTORY ] )

if( PRINT_CONFIG ):
    print_log( [ "OS X Lion?".ljust( 30 ), IS_LION ] )
    print_log( [ "Date/Time Format".ljust( 30 ), DATE_TIME_FORMAT ] )
    print_log( [ "Separator".ljust( 30 ), SEPARATOR ] )
    print_log( [ "Print Config".ljust( 30 ), PRINT_CONFIG ] )
    print_log( [ "File types".ljust( 30 ), FILE_TYPES ] )
    if( category == "tv" ):
        print_log( [ "TV format".ljust( 30 ), TV_FORMAT ] )
    print_log( [ "Output File prefix".ljust( 30 ), OUTPUT_PREFIX ] )
    print_log( [ "Output File postfix".ljust( 30 ), OUTPUT_POSTFIX ] )
    print_log( [ "Output File extension".ljust( 30 ), OUTPUT_EXTENSION ] )    
    print_log( [ "Delete original".ljust( 30 ), DELETE_ORIGINAL ] )
    print_log( [ "Handbrake path".ljust( 30 ), HANDBRAKE_PATH ] )
    print_log( [ "Handbrake Pre-Preset Paramaters".ljust( 30 ), HANDBRAKE_PARAMATERS_BEFORE_PRESET ] )
    print_log( [ "Handbrake Post-Preset Paramaters".ljust( 30 ), HANDBRAKE_PARAMATERS_AFTER_PRESET ] )
    print_log( [ "Handbrake preset".ljust( 30 ), HANDBRAKE_PRESET ] )
    print_log( [ "Handbrake use all audio tracks".ljust( 30 ), HANDBRAKE_ALL_AUDIO ] )
    print_log( [ "Print handbrake output".ljust( 30 ), HANDBRAKE_COMMAND_OUTPUT ] )
    print_log( [ "Post processing".ljust( 30 ), POST_PROCESSING ] )
    if( POST_PROCESSING ):
        print_log( [ "Post processing command".ljust( 30 ), POST_PROCESSING_COMMAND ] )
        print_log( [ "Print post processing output".ljust( 30 ), POST_PROCESSING_OUTPUT ] )
    print_log( [ "Import to iTunes".ljust( 30 ), IMPORT_TO_ITUNES ] )
    print_log( [ "Delete after import to iTunes".ljust( 30 ), DELETE_AFTER_IMPORT ] )
    print_log( [ "Append output".ljust( 30 ), OUTPUT_APPEND ] )

handbrake_output_list = [[]]

for file_type in FILE_TYPES:
    print_log( [ "Processing file type", file_type ] )
    for input_file in glob.glob( final_directory + "/" + file_type ):
        handbrake_output_list[-1].append( [ 'Input File', input_file ] );
        ( directory, filename_ext ) = os.path.split( input_file )
        filename = os.path.splitext( filename_ext )[0]
        output_file = "{OUTPUT_PREFIX}{filename}{OUTPUT_POSTFIX}.{OUTPUT_EXTENSION}".format( **locals() )
        output_file_path = os.path.join( OUTPUT_DIRECTORY, output_file )
        
        
        # check if file is already in iTunes
        if( IMPORT_TO_ITUNES ):
            ( r, stdout ) = check_if_in_itunes( filename )
            if( r == 0 ):
                if( stdout != "0" ):
                    print_log( [ "\t" + filename, "skipping", "already exists in iTunes library" ] )
                    handbrake_output_list[-1].append( [ " - skipped", "already in iTunes library" ] );
                    continue
            else:
                print_log( [ "\t" + "error", "checking iTunes", "ERROR {0}: {1}".format( r, stdout ) ] )
        
        # check if output file already exists
        if( os.path.exists( output_file_path ) ):
            print_log( [ "\t" + filename, 'skipping', 'already converted' ] )
            handbrake_output_list[-1].append( [ " - skipped", "already converted" ] );
            continue
        
        output_file_processing = "{OUTPUT_PREFIX}{filename}{OUTPUT_POSTFIX}_processing.{OUTPUT_EXTENSION}".format( **locals() )
        output_file_processing_path = os.path.join( OUTPUT_DIRECTORY, output_file_processing )
        
        handbrake_command = [ HANDBRAKE_PATH, "-i", input_file, "-o", output_file_processing_path ]
        if( HANDBRAKE_PARAMATERS_BEFORE_PRESET ):
            handbrake_command.extend( shlex.split( HANDBRAKE_PARAMATERS_BEFORE_PRESET ) )
        
        if( HANDBRAKE_PRESET ):
            handbrake_command.append( "--preset=" + HANDBRAKE_PRESET )
        
        if( HANDBRAKE_ALL_AUDIO ):
            handbrake_command.append( "--audio=" + get_audio_track_list( input_file ) )
        
        if( HANDBRAKE_PARAMATERS_AFTER_PRESET ):
            handbrake_command.extend( shlex.split( HANDBRAKE_PARAMATERS_AFTER_PRESET ) )
        
        stdout = None if HANDBRAKE_COMMAND_OUTPUT else subprocess.PIPE
        stderr = None if HANDBRAKE_COMMAND_OUTPUT else subprocess.STDOUT
        
        print_log( [ "\t" + filename, "encoding", output_file_processing ] )
        
        p = subprocess.Popen( handbrake_command, stdout = stdout, stderr = stderr )
        ( stdout, stderr ) = p.communicate()
        
        if( not HANDBRAKE_COMMAND_OUTPUT ):
            handbrake_output_list[-1].append( [ " - handbrake output", stdout ] );
        
        if( p.wait() != 0 ):
            print_log( [ "\t" + "FAILED", "handbrake did not finish successfully" ] )
            handbrake_output_list[-1].append( [ " - failed", "handbrake did not finish successfully" ] );
            continue
        
        if( not os.path.isfile( os.path.join( OUTPUT_DIRECTORY, output_file_processing ) ) ):
            print_log( [ "\t" + "ERROR", os.path.join( OUTPUT_DIRECTORY, output_file_processing ) + " is not a valid path" ] )
            handbrake_output_list[-1].append( [ " - errored", os.path.join( OUTPUT_DIRECTORY, output_file_processing ) + " is not a valid path" ] );
            continue            

        os.rename( os.path.join( OUTPUT_DIRECTORY, output_file_processing ), os.path.join( OUTPUT_DIRECTORY, output_file ) )
        
        print_log( [ "\t" + "done encoding" ] )
        
        if( DELETE_ORIGINAL ):
            sys.stdout.write( strftime( DATE_TIME_FORMAT ) + "\t" + "deleting original" )
            sys.stdout.flush()
            os.unlink( input_file )
            print SEPARATOR + 'done'
        
        if( POST_PROCESSING ):
            print_log( [ "\t" + "post processing", output_file ] )
            ( r, stdout ) = post_process( output_file_path, OUTPUT_DIRECTORY )
            if( not POST_PROCESSING_OUTPUT ):
                handbrake_output_list[-1].append( [ " - post_processing", stdout ] );
            
            if( r == 0 ):
                print_log( [ "\t" + "done post processing" ] )
            else:
                print_log( [ "\t" + "error post processing", "ERROR {0}: {1}".format( r, stdout ) ] )
        
        if( IMPORT_TO_ITUNES ):
            print_log( [ "\t" + "importing to iTunes"] )
            r = import_in_itunes( filename, output_file_path )
            if( r == 0 ):
                print_log( [ "\t" + "done" ] )
                if( DELETE_AFTER_IMPORT ):
                    sys.stdout.write( strftime( DATE_TIME_FORMAT ) + "\t" + "deleting converted file" )
                    sys.stdout.flush()
                    os.unlink( output_file_path )
                    print SEPARATOR + 'done'
            else:
                print_log( [ "\t" + "ERROR" ] )

if( OUTPUT_APPEND ):
    for i in handbrake_output_list:
        print "output"
        print "\n"
        for j in i:
            print j[0].ljust( 20 ) + ": " + re.sub( r'\n', '\n' + "... ".rjust( 20 ) + ": ", j[1] )

###############################################################################
# PLEASE DO NOT REMOVE
#
# Author: Anchal 'Nacho' Nigam (and lots of help from #python on irc.freenode.net)
# E-Mail: emailyoumust@gmail.com
# Date:   February 1, 2010
###############################################################################
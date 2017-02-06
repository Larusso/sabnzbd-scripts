DATE_TIME_FORMAT = "[ %Y-%m-%d @ %H:%M:%S ]  "
SEPARATOR = " : "
KEY_SPACE = 30

from time import strftime
def print_log( l ):
	key = "%s:" % l.pop(0)
	print strftime( DATE_TIME_FORMAT ) + key.ljust(KEY_SPACE) + SEPARATOR.join( map( str, l ) )

def print_break( char ):
	print char.ljust(KEY_SPACE * 2,char)

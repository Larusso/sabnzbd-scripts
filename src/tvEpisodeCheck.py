import sys
import re
import os
import log
import shutil
import fnmatch

class TVEpisodeCheck( ):
	def findEpisodeFileAtPath(self, path, fileName):
		log.print_log( [ "try to find downloaded file", fileName, path ] )
		log.print_break( "-" )
		dirList = os.listdir( path )
		for fname in dirList:
			log.print_log( [ "file in path", fname ] )
			splitR = os.path.splitext( fname )
			root = splitR[ 0 ]
			ext = splitR[ 1 ]
			log.print_log( [ 'file root', root ] )
			log.print_log( [ 'file extension', ext ] )
			if ext == ".mkv" or ext == ".avi" or ext == ".mpg" or ext == ".mpeg":
				if root == fileName:
					log.print_log( [ "file found", fileName ] )
					log.print_break( "-" )
					return os.path.join( path, fname )
		log.print_break( "-" )
		return None

	def getDownloadDetails(self, nzbName):
		match = re.search( '^(.*?) ([S|s][0-9]{2,})[\.]*([E|e][0-9]{2,})', nzbName )
		log.print_break( "-" )
		log.print_log( [ 'get episode information' ] )
		#log.print_log( [ "match", match.group( 0 ) ] )
		log.print_log( [ "show title", match.group( 1 ) ] )
		log.print_log( [ "season", match.group( 2 ) ] )
		log.print_log( [ "episode", match.group( 3 ) ] )

		isWebRelease = False
		webMatch = re.search( 'WEB DL DD5 1', nzbName )
		if not webMatch is None:
			isWebRelease = True
		log.print_log( [ "is WEB release", isWebRelease ] )
		log.print_break( "-" )

		is5_1Release = False
		dd5_1Match = re.search( 'DD5 1', nzbName )
		if not dd5_1Match is None:
			is5_1Release = True
		log.print_log( [ "is 5.1 release", is5_1Release ] )
		log.print_break( "-" )

		return TVShowEpisodeDetails( match.group( 1 ), match.group( 2 ), match.group( 3 ), isWebRelease, is5_1Release )

	# run the check and move or rename the downloaded file
	# move duplicate files to a trash folder!
	def executeEpisodeCheck(self, resultDir, nzbName):
		exitCode = 0
		# get the episode details from the nzb file name
		episodeDetails = self.getDownloadDetails( nzbName )

		# retrieve the downloaded file path
		downloadedFilePath = self.findEpisodeFileAtPath( resultDir, episodeDetails.getFileName( ) )

		# create the final file path
		finalPath = os.path.abspath( os.path.join( resultDir, os.path.pardir ) )

		# check if the epsisode is already been downloaded
		duplicateEpisodePath = self.findEpisodeFileAtPath( finalPath, episodeDetails.getFileName( ) )
		log.print_log( [ "is episode downloaded?", duplicateEpisodePath ] )

		if not downloadedFilePath is None:
			log.print_log( [ "found downloaded file", downloadedFilePath ] )
			if duplicateEpisodePath:
				# check if the filesize is bigger

				# get the duplicate episode file filesize
				os.chdir( finalPath )
				duplicateFileSize = os.path.getsize( os.path.basename( duplicateEpisodePath ) )
				log.print_log(["duplicateFileSize",duplicateFileSize])

				# get the downloaded episode filesize
				os.chdir( resultDir )
				downloadedEpisodeFileSize = os.path.getsize( os.path.basename( downloadedFilePath ) )
				log.print_log(["downloadedEpisodeFileSize",downloadedEpisodeFileSize])

				overrideFile = False
				if downloadedEpisodeFileSize > duplicateFileSize:
					delta = downloadedEpisodeFileSize - duplicateFileSize
					log.print_log(["filesize delta", delta])
					if delta >= (100 * 1024 * 1024):
						overrideFile = True

					elif episodeDetails.isWebRelease and episodeDetails.is5_1Release:
						overrideFile = True

				if episodeDetails.isWebRelease:
					#override file!
					log.print_log( [ "override file" ] )

					#first rename the original file
					log.print_log( [ "backup old download", os.path.basename( duplicateEpisodePath ),
					                 os.path.basename( duplicateEpisodePath ) + ".bak" ] )
					os.chdir( finalPath )
					os.rename( os.path.basename( duplicateEpisodePath ),
					           os.path.basename( duplicateEpisodePath ) + ".bak" )

					#copy the file to the new location
					shutil.move( downloadedFilePath, finalPath )

				else:
					log.print_log( [ "ignore download" ] )
			else:
				log.print_log( [ "save file as " ] )
				#copy the file to the new location
				shutil.move( downloadedFilePath, finalPath )
		else:
			log.print_log( [ "found no download!" ] )
			exitCode = 1

		#delete the result directory
		log.print_log( [ "delete the result directory", resultDir ] )
		#shutil.rmtree( resultDir, onerror=self.remove_readonly )

		return exitCode


	def remove_readonly(fn, path, excinfo):
		if fn is os.rmdir:
			os.chmod( path, stat.S_IWRITE )
			os.rmdir( path )
		elif fn is os.remove:
			os.chmod( path, stat.S_IWRITE )
			os.remove( path )


class TVShowEpisodeDetails( ):
	def __init__(self, showName, seasonCode, episodeCode, isWebRelease, is5_1Release):
		self.showName = showName
		self.seasonCode = seasonCode
		self.episodeCode = episodeCode
		self.isWebRelease = isWebRelease
		self.is5_1Release = is5_1Release

	def getFileName(self):
		return self.showName + " - " + self.seasonCode + self.episodeCode

	def isWebRelease(self):
		return self.isWebRelease



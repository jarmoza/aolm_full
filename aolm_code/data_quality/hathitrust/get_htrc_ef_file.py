# Code adapted from https://wiki.htrc.illinois.edu/display/COM/Downloading+Extracted+Features#DownloadingExtractedFeatures-ConvertingHathiTrustVolumeIDtoRSyncURL(usingPython)

from my_debug import debug_print
import glob
import os
from pairtree import id2path, id_encode
import subprocess
import time


# Your output path here
ef_output_path = "/Users/PeregrinePickle/Desktop/victor_ef_files/"
nyp_output_path = "/Users/PeregrinePickle/Documents/Digital_Humanities/htrc_playground/data/ninec_tests/nyp_ef_files/"
current_output_path = nyp_output_path
bib_api_json_path = "/Users/PeregrinePickle/Documents/Digital_Humanities/htrc_playground/data/ninec_tests/bib_api_json/"


def id_to_rsync(p_htid):

	# Take an HTRC id and convert it to an Rsync location for syncing Extracted Features
	libid, volid = p_htid.split(".", 1)
	volid_clean = id_encode(volid)
	filename = ".".join([libid, volid_clean, "json.bz2"])

	print "P_Htid: {4}\nLibid: {0}\nVolid: {1}\nVolidClean: {2}\nFilename: {3}".format(libid, volid, volid_clean, filename, p_htid)

	path = "/".join([libid, "pairtree_root", id2path(volid).replace("\\", "/"), volid_clean, filename])

	debug_print(path)

	return path

def replace_illegal_chars(p_string):

	characters = []
	illegal_chars = "+=/"
	for ch in p_string:
		if ch in illegal_chars:
			characters.append("-")
		else:
			characters.append(ch)

	return "".join(characters)

def rsync_ef_file(p_filename):

	# Terminal example
	# rsync -azv data.analytics.hathitrust.org::features/{{URL}} 
	debug_print("Rsyncing {0}".format("data.analytics.hathitrust.org::features/{0}".format(p_filename)))
	print p_filename[p_filename.rfind("/") + 1:]
	subprocess.call(["rsync",
					 # "-azv",
					 "-az",
					 "data.analytics.hathitrust.org::features/{0}".format(p_filename), 
					 "{0}{1}".format(current_output_path, p_filename[p_filename.rfind("/") + 1:])]) 

def rsync_ef_file_clean(p_filename):

	# Terminal example
	# rsync -azv data.analytics.hathitrust.org::features/{{URL}} 
	clean_filename = replace_illegal_chars(p_filename)
	debug_print("Rsyncing {0}".format("data.analytics.hathitrust.org::features/{0}".format(clean_filename)))
	subprocess.call(["rsync",
					 # "-azv",
					 "-az",
					 "data.analytics.hathitrust.org::features/{0}".format(p_filename), 
					 "{0}{1}".format(current_output_path, clean_filename)]) 
					 # "{0}{1}".format(current_output_path, p_filename)]) 


def main():

	# Your HathiTrust volume IDs here
	# test_id = "mdp.39015000623424"
	# test_id = "miun.adx6300.0001.001"
	
	# Victor
	# ht_vol_ids = ['nyp.33433006830958',
	# 			  'njp.32101067486678',
	# 			  'nyp.33433082138706',
	# 			  'nyp.33433076042393',
	# 			  'nyp.33433082138755',
	# 			  'njp.32101017504109',
	# 			  'nyp.33433076041486',
	# 			  'nyp.33433074799408']

	# New York Public
	ht_vol_ids = []
	for filepath in glob.glob(bib_api_json_path + "nyp*.json"):
		ht_vol_ids.append(filepath[filepath.rfind("/") + 1: filepath.rfind(".")])

	# Get filenames for download
	filenames = [id_to_rsync(vol_id) for vol_id in ht_vol_ids]

	# Retrieve EF files
	map(rsync_ef_file, filenames)


if "__main__" == __name__:
	main()
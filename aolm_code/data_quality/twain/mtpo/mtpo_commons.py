# Author: Jonathan Armoza
# Project: Art of Literary Modeling
# Date: October 22, 2019
# Purpose: Stores common data for exploring the TEI XML files of 
#		   Mark Twain Project Online (http://www.marktwainproject.org/)
# Credits: Terence Catapano of MTPO (assisted with file location and usage
# 		   rights determination, 2018-2019)
# Initial access date of files: September 5, 2019

# Imports

# Built-ins
import os	# Determines current working directory


# Globals

def format_path(p_path):
	if os.sep != p_path[len(p_path) - 1]:
		return p_path + os.sep
	return p_path

mtpo_root_folder = format_path(os.getcwd()) + ".." + os.sep

# Options and fields for retrieving works from Mark Twain Project Online
mtpo = {}

# A. TEI files sorted by genre
mtpo["known_files"] = {

	"autobio": ["MTDP10362.xml", "MTDP10363.xml", "MTDP10364.xml"],
	"fiction": ["MTDP10000.xml", "MTDP10001.xml", "MTDP10002.xml", "MTDP10360.xml"],
	"letters": [],
	"reviews": []
}

# B. Titles keyed by TEI file name
mtpo["known_files_dict"] = {
	
	"MTDP10000.xml": "Adventures of Huckleberry Finn : an electronic text",
	"MTDP10001.xml": "The Adventures of Tom Sawyer : an electronic text",
	"MTDP10002.xml": "Roughing It : an electronic text",
	"MTDP10360.xml": "Huck Finn and Tom Sawyer among the Indians, and Other Unfinished Stories : an electronic text",
	"MTDP10362.xml": "Autobiography of Mark Twain, Volume 1 : an electronic text",
	"MTDP10363.xml": "Autobiography of Mark Twain, Volume 2 : an electronic text",
	"MTDP10364.xml": "Autobiography of Mark Twain, Volume 3 : an electronic text"
}

# C. File folders (relative to mtpo_commons path)
mtpo["folders"] = { 
	"root": mtpo_root_folder,
	"scripts": format_path(mtpo_root_folder + "scripts"),
	"works": format_path(mtpo_root_folder + "mtpo"),
	"output": format_path(mtpo_root_folder + "output")
}
mtpo["folders"]["autobiographies"] = format_path(mtpo["folders"]["works"] + "autobiographies" + os.sep + "formatted")
mtpo["folders"]["fiction"] = format_path(mtpo["folders"]["works"] + "fiction")
mtpo["folders"]["letters"] = format_path(mtpo["folders"]["works"] + "letters")

# D. Primary sections by volume
mtpo["sections"] = {
	
	"primary": {

		"bd0010": "Preliminary Manuscripts and Dictations",
		"bd0011": "Autobiography of Mark Twain",
	}
}

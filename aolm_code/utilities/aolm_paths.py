import os
import sys

data_paths = {}

def setup_paths():

	# 1. Check and initialize code paths for the project
	setup_code_paths()

	# 2. Check and initialize data paths for the project
	setup_data_paths()

def setup_code_paths():

	# 0. Code folder is one level above utlities folder
	code_folder = "..{0}{1}".format(os.sep, os.path.dirname(__file__))
	
	# 1. Add code folder to Python path if not already added to it
	if code_folder not in sys.path:
		sys.path.append(code_folder)

def setup_data_paths():

	# 0. Check to see if paths variable has been filled in
	if 0 == len(data_paths):

		# 1. Setup root data folder paths
		
		# A. The root data folder for the project is two levels above utilities folder
		data_paths["root"] = "{0}{1}..{1}..{1}data{1}".format(os.path.dirname(__file__), os.sep)
		
		# B. Root folders for project working data
		data_paths["aolm_root"] = data_paths["root"] + "aolm" + os.sep
		data_paths["aolm_dickinson_root"] = "{0}aolm{1}dickinson{1}".format(data_paths["root"], os.sep)
		data_paths["aolm_general_root"] = "{0}aolm{1}general{1}".format(data_paths["root"], os.sep)
		data_paths["aolm_hathi_root"] = "{0}aolm{1}hathi{1}".format(data_paths["root"], os.sep)
		data_paths["aolm_shakespeare_root"] = "{0}aolm{1}shakespeare{1}".format(data_paths["root"], os.sep)
		data_paths["aolm_twain_root"] = "{0}aolm{1}twain{1}".format(data_paths["root"], os.sep)

		# C. Root folders for source data
		data_paths["dickinson_root"] = data_paths["root"] + "dickinson" + os.sep
		data_paths["general_root"] = data_paths["root"] + "general" + os.sep
		data_paths["hathi_root"] = data_paths["root"] + "hathi" + os.sep
		data_paths["twain_root"] = data_paths["root"] + "twain" + os.sep

		# 2. Setup subfolders from those root paths
		
		# A. Emily Dickinson working data
		data_paths["aolm_dickinson"] = {

			"correspondence": data_paths["aolm_dickinson_root"] + "correspondence" + os.sep,
			"general": data_paths["aolm_dickinson_root"] + "general" + os.sep,
			"dq_assessment": data_paths["aolm_dickinson_root"] + "dq_assessment" + os.sep,
			"eda_chronology": data_paths["aolm_dickinson_root"] + "eda" + os.sep + "chronology" + os.sep
		}

		# B. General working data
		data_paths["aolm_general"] = {

			"voyant_stopwords": data_paths["aolm_general_root"] + "input" + os.sep + "voyant_stopwords.txt"
		}

		# C. HathiTrust working data
		data_paths["aolm_hathi"] = {}

		# D. Shakespeare working data
		data_paths["aolm_shakespeare"] = {

			"richardiii": data_paths["aolm_shakespeare_root"] + "richardiii" + os.sep
		}

		# E. Mark Twain working data
		data_paths["aolm_twain"] = {

			"aphorisms": data_paths["aolm_twain_root"] + "aphorisms" + os.sep,
			"general": data_paths["aolm_twain_root"] + "general" + os.sep,
			"gutenberg_dq": data_paths["aolm_twain_root"] + "gutenberg_dq" + os.sep,
			"mtpo": data_paths["aolm_twain_root"] + "mtpo" + os.sep
		}

		# F. Emily Dickinson source data
		data_paths["dickinson"] = {

			"bingham": data_paths["dickinson_root"] + "bingham" + os.sep,
			"eda": data_paths["dickinson_root"] + "eda"+ os.sep,
			"general": data_paths["dickinson_root"] + "general"+ os.sep,
			"reference": data_paths["dickinson_root"] + "reference" + os.sep
		}

		# G. General source data
		data_paths["general"] = {}

		# H. HathiTrust source data
		data_paths["hathi"] = {}

		# I. Mark Twain source data
		data_paths["twain"] = {

			"autobiography": data_paths["twain_root"] + "autobiography" + os.sep,
			"huckleberry_finn": data_paths["twain_root"] + "huckleberry_finn" + os.sep,
			"internet_archive": data_paths["twain_root"] + "huckleberry_finn" + os.sep + "internet_archive" + os.sep
		}
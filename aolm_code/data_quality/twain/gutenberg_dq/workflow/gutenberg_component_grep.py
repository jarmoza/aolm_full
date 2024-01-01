# Author: Jonathan Armoza
# Creation date: October 11, 2021
# Purpose: Reads in a Project Gutenberg-style text in txt format
# 		   and divides it into units provided by an input json metadata file

# TODO:
# (1) Modularize chapter grep script
# (2) Build json input parameters for each Huckleberry Finn edition
# (3) Run grep script over each text and insert components into the json file for each
# (4) Move utility functions to aolm_utilities.py
# (5) Proper github setup for Art of Literary Modeling repository

# Process for entering a new text:
# (1) Identify all file keys in metadata json file
# ex. below
# "frontmatter_endline": "Scene: The Mississippi Valley Time: Forty to fifty years ago",
# "chapter_prefix": "CHAPTER",
# "body_endline": "*** END OF THE PROJECT GUTENBERG EBOOK HUCKLEBERRY FINN ***",
# "body_component_prefix": "HUCKLEBERRYFINN_BODY_",
# "gutenberg_header_prefix": "GUTENBERG_HEADER_",
# "gutenberg_footer_prefix": "GUTENBERG_FOOTER_"

# Known Huckleberry Finn edition text files
# paths["2021-02-21"] = "2021-02-21_HuckFinn.txt"
# paths["2016-08-17"] = "2016-08-17_HuckFinn.txt"
# paths["2021-02-21"] = "2021-02-21_HuckFinn.txt"

# Imports

# Standard library
from collections import OrderedDict
import json
import os
import sys

# Local
from utilities.aolm_utilities import print_debug_header
from utilities.aolm_utilities import is_valid_file
from utilities import aolm_paths
aolm_paths.setup_paths()


# Globals

# Input/output paths
paths = {
	
	# "input": "{0}gutenberg_dq{1}input{1}".format(aolm_paths.data_paths["aolm_twain_root"], os.sep),
	# "output": "{0}gutenberg_dq{1}input{1}".format(aolm_paths.data_paths["aolm_twain_root"], os.sep)
	"input": "{0}txt{1}demarcated{1}".format(aolm_paths.data_paths["twain"]["internet_archive"], os.sep),
	"output": "{0}txt{1}demarcated{1}".format(aolm_paths.data_paths["twain"]["internet_archive"], os.sep)

}

# Utility functions

def output_stats(p_metadata_filepath):

	# 0. Read in the metadata json
	with open(p_metadata_filepath, "r") as metadata_file:
		metadata_json = json.load(metadata_file)

	# 1. Show base filename on the terminal
	print(os.path.splitext(os.path.basename(p_metadata_filepath))[0].upper())

	# 2. Output file keys to the terminal
	print_debug_header("File keys")
	for key in metadata_json["keys"]:
		print("{0}: {1}".format(key, metadata_json["keys"][key]))

	# 2. Output stats on text file components to the terminal
	print_debug_header("File component stats")
	print("Header length (lines): {0}".format(len(metadata_json["components"]["GUTENBERG_HEADER"])))
	print("Body components (count): {0}".format(len(metadata_json["components"]) - 2))
	print("Footer length (lines): {0}".format(len(metadata_json["components"]["GUTENBERG_FOOTER"])))


# Classes

class GutenbergReader:

	# Constructor and private methods

	def __init__(self, p_text_filepath, p_metadata_filepath):

		# 0. Save parameters
		self.m_text_filepath = p_text_filepath
		self.m_metadata_filepath = p_metadata_filepath

		# 1. Member field initialization

		# Stores chapter first and lines, in chapter-order
		self.m_components = OrderedDict()

		# Stores lines of the text file
		self.m_text_lines = []

		# Stores json components of metadata file
		self.m_metadata_json = {}

		# 2. Read input files
		self.__read_text_file()
		self.__read_metadata_file()

		# 3. Read input components by keys and in order specified from text file
		self.read_components()

		# 4. Save components into metadata json
		self.m_metadata_json["components"] = self.m_components

	def __read_metadata_file(self):

		# 1. Read in metadata file for text file
		with open(self.m_metadata_filepath, "r") as metadata_file:
			self.m_metadata_json = json.load(metadata_file)

		# A. Check to see if text has already been transformed into json, and if it has, clear them for a new reading
		if len(self.m_metadata_json["components"]) > 0:
			self.m_metadata_json["components"] = {}

	def __read_text_file(self):

		# 1. Read in text file
		with open(self.m_text_filepath, "r") as text_file:
			self.m_text_lines = text_file.readlines()

	# Public methods

	def read_components(self):

		# 0. Reading through text file starting at first line
		line_index = 0

		# 1. Go through component keys, reading components specified by them in order
		for input_key in self.m_metadata_json["keys"]["order"]:

			# A. Read this component and the line where reading stopped
			self.m_components[input_key], line_index = \
				GutenbergReader.read_component(
					(self.m_metadata_json["keys"]["input"][input_key]["startline"],
				 	 self.m_metadata_json["keys"]["input"][input_key]["endline"]),
					self.m_text_lines,
					line_index)

			# B. Check to see if this component needs to be divided into subcomponents
			if "subcomponents" in self.m_metadata_json["keys"]["input"][input_key]:

				# I. Save subcomponent prefixes for reading and writing
				input_prefix = self.m_metadata_json["keys"]["input"][input_key]["subcomponent_input_prefix"]
				output_prefix = self.m_metadata_json["keys"]["output"][input_key]

				# II. Determine line indices where input prefix exists
				subcomp_indices = [[index] for index in range(len(self.m_components[input_key])) if input_prefix in self.m_components[input_key][index]]
				for item_index in range(len(subcomp_indices)):
					if item_index + 1 < len(subcomp_indices):
						subcomp_indices[item_index].append(subcomp_indices[item_index + 1][0] - 1)
					else:
						subcomp_indices[item_index].append(len(self.m_components[input_key]) - 1)

				# III. Split apart component into subcomponents
				subcomponents = OrderedDict()
				for item in subcomp_indices:
					subcomponents[output_prefix + self.m_components[input_key][item[0]]] = \
						self.m_components[input_key][item[0] + 1:item[1] + 1]

				# IV. Replace full text component with dictionary subcomponents
				self.m_components[input_key] = subcomponents

	def output(self, p_metadata_filepath):

		# 1. Write out the new json data to the metadata json file
		with open(p_metadata_filepath, "w") as output_file:
			json.dump(self.m_metadata_json, output_file, indent=4)


	# Static methods

	@staticmethod
	def read_component(p_line_keys, p_text_lines, p_line_start_index):
		
		# 0. Line keys
		start_key = p_line_keys[0]
		end_key = p_line_keys[1]

		# 0. Text component
		component_lines = []

		# 0. Search flags
		start_key_found = False
		end_key_found = False

		# 0. Line stop index to return back
		line_stop_index = p_line_start_index

		# 1. Gather text lines for component between start and end keys, inclusive
		for index in range(p_line_start_index, len(p_text_lines)):

			# A. Stop reading if end line key was read
			if end_key_found:
				break

			# B. Increment line stop index for future reading
			line_stop_index += 1

			# C. Strip line of white space
			cleaned_line = p_text_lines[index].strip()

			# D. Search for start key if not yet found
			if not start_key_found:
				if start_key in cleaned_line:
					component_lines.append(cleaned_line)
					start_key_found = True
			else:
				if end_key in cleaned_line:
					end_key_found = True
				component_lines.append(cleaned_line)

		# 2. Return component between start and end line keys, inclusive
		#    or between start line key and end of file if end line key not found
		#	 and return the line where reading ended
		return component_lines, line_stop_index


# Main script		

def main(p_txt_filename):

	# 0. Text file path and metadata json file path inferred form text filename
	text_filepath = paths["input"] + p_txt_filename
	print(text_filepath)
	metadata_filepath = paths["input"] + os.path.splitext(p_txt_filename)[0] + ".json"

	# 0. Check for valid input text file and corresponding metadata json file
	if not is_valid_file(text_filepath, "txt") or \
	   not is_valid_file(metadata_filepath, "json"):
		print("Invalid filename input: {0}".format(p_txt_filename))
		return

	# 1. Read file components into ordered dictionary
	reader = GutenbergReader(text_filepath, metadata_filepath)

	# 2. Output text components into the metadata file
	reader.output(metadata_filepath)

	# 3. Output stats based on script run
	# output_stats(metadata_filepath)
		

if "__main__" == __name__:
	if len(sys.argv) > 1:
		main(sys.argv[1] if len(sys.argv) > 1 else "")

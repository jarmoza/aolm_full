# Author: Jonathan Armoza
# Created: January 11, 2022
# Purpose: Retrieve text files for editions of "The Adventures of Huckleberry Finn"
# from the Internet Archive

# Internet Archive information
# Advanced search query: title:(adventures of huckleberry finn) AND creator:(twain) AND mediatype:(texts)
# Command line interface documentation: https://archive.org/services/docs/api/internetarchive/cli.html

# ia download --itemlist=idlist.txt --format='Text'

# Imports

# Standard library
import json
import os
import subprocess

# Local library
from utilities.aolm_paths import data_paths
from utilities.aolm_paths import setup_paths
from utilities.aolm_utilities import debug_separator
setup_paths()


# Globals

# Paths
input_data_path = "{0}input{1}".format(data_paths["aolm_twain"]["gutenberg_dq"], os.sep)
output_data_path = "{0}output{1}".format(data_paths["aolm_twain"]["gutenberg_dq"], os.sep)
# editions_ids_csv_filename = "internarchive_ids_huckfinn.csv"
editions_json_filename = "internarchive_ids_huckfinn.json"

edition_metadata = None

# Main script

# Functions

def download_editions_byformat(p_format):

	# 1. Download each edition as a plain text file if it exists for that edition
	# Example: ia download theadventuresofh07104gut --format='Text'
	for edition_id in edition_metadata:

		print("Trying to download {0} ...".format(edition_id))

		# A. Attempt to download the file
		try:
			subprocess.check_call([
				"ia",
				"download",
				edition_id,
				"--format=\'{0}\'".format(p_format)
			])
		except:
			print("Could not find txt file for {0}".format(edition_id))
			continue

def read_metadata():

	# 1. Read in edition metadata
	
	# A. Read in json data
	with open(input_data_path + editions_json_filename, "r") as json_file:
		json_data = json.load(json_file)

	# B. Create a dictionary based on edition ID
	docs = json_data["response"]["docs"]
	edition_metadata = { edition["identifier"]:edition for edition in docs }

	return edition_metadata

def main():

	# 1. Read in edition metadata
	edition_metadata = read_metadata()

	# 2. Display all text formats by edition ID
	for edition_id in edition_metadata:

		valid_formats = []
		for format_name in edition_metadata[edition_id]["format"]:
			if "text" in format_name.lower() or "txt" in format_name.lower():
				valid_formats.append(format_name)

		if len(valid_formats):
			print("{0}\nEdition: {1}".format(debug_separator, edition_id))
			print(valid_formats)


	# 3.. Download editions
	# download_editions_byformat("Text")
if "__main__" == __name__:
	main()


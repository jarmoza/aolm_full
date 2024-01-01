# Author: Jonathan Armoza
# Creation date: March 19, 2019
# Purpose: Look at summary aspects of Emily Dickinson Archive's tei files
# 		   and perform data quality profiing on them

# Imports

# Built-ins
import argparse
from collections import Counter
import glob
import os
# import pdb
from shutil import copyfile
import xml.etree.ElementTree

# Third party
from bs4 import BeautifulSoup
import editdistance # https://github.com/aflc/editdistance
import numpy as np

# Globals

# Maps publication name to folder in the split corpus
corpus_folder_map = {

	u'Poems by Emily Dickinson, Todd and Higginson, 1890': "todd_higginson_1890",
	u'Poems by Emily Dickinson: Second Series, Higginson and Todd, 1891': "higginson_todd_2nd_1891",
	u'Poems by Emily Dickinson: Third Series, Todd, 1896': "todd_3rd_1896",
	u'The Single Hound,  Bianchi, 1914': "bianchi_1914",
	u'The Poems of Emily Dickinson, Johnson, 1955': "johnson_1955",
	u'The Poems of Emily Dickinson, Variorum Edition, Franklin, 1998': "franklin_1998"
}

# Command line argument parser
parser = argparse.ArgumentParser(description="Art of Literary Modeling, XML Analysis for Data Quality")

# Paths for outputs of this script
paths = {

	# Path to Dickinson tei files
	"tei_path": os.getcwd() + "{0}..{0}tei{0}".format(os.sep),

	# Path to tag html output files
	"html_path": os.getcwd() + "{0}..{0}stats{0}html{0}".format(os.sep),

	# Root path to split corpus folders
	"split_corpus_path": os.getcwd() + "{0}..{0}curated{0}split{0}".format(os.sep),

	# Path to list of Levenshtein edit distances between poem titles
	"title_distance_path": os.getcwd() + "{0}..{0}stats{0}title_distances{0}".format(os.sep),

	# Path where output files from xml analysis are placed
	"output_path": os.getcwd() + "{0}output{0}".format(os.sep)
}

# Default command line argument values
script_cli_defaults = {
	
	"allattributeinfo": [paths["tei_path"], paths["output_path"]],
	"attributeinfo":	["tei", paths["tei_path"], paths["output_path"]],
	"create": 			[paths["tei_path"], paths["html_path"]],
	"similartitles": 	[paths["tei_path"], paths["title_distance_path"]],
	"splitpublication": [paths["tei_path"], paths["split_corpus_path"]],
	"tagfieldvalues": 	["tei", "True", paths["tei_path"]],
	"tagcardinality": 	[paths["html_path"], paths["tei_path"], paths["output_path"]],
	"taginfo": 			["tei", paths["tei_path"]]
}

# Default TEI namespace
tei_namespace = "{http://www.tei-c.org/ns/1.0}"


# Utility functions
def set_args(p_args, p_name):

	index = 0
	my_args = []

	# 0. Get args attribute
	attribute = getattr(p_args, p_name)

	# 1. Save given args

	# If given args is in list form
	if isinstance(attribute, list):

		# A. Save the given args
		while index < len(attribute):
			my_args.append(attribute[index])
			index += 1

	# Else, given args is single variable
	else:
		my_args.append(attribute)
		index += 1

	# 2. Fill out the rest of the necessary args with default values
	while index < len(script_cli_defaults[p_name]):
		my_args.append(script_cli_defaults[p_name][index])
		index += 1

	return my_args

def levenshtein(p_sequence1, p_sequence2):
    
    size_x = len(p_sequence1) + 1
    size_y = len(p_sequence2) + 1
    matrix = np.zeros ((size_x, size_y))
    
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            
            if p_sequence1[x - 1] == p_sequence2[y-1]:
                matrix [x,y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1],
                    matrix[x, y - 1] + 1)
            else:
                matrix [x,y] = min(
                    matrix[x - 1,y] + 1,
                    matrix[x - 1,y - 1] + 1,
                    matrix[x,y - 1] + 1)

    return (matrix[size_x - 1, size_y - 1])

# Utility classes

class DefaultArgs(argparse.Action):

	# Private methods
	
	def __call__(self, p_parser, p_namespace, p_values, option_string=None):
		
		setattr(p_namespace, self.dest, p_values)
		setattr(p_namespace, self.dest + DefaultArgs.s_nondefault_str, True)

	# Static methods and variables

	@staticmethod
	def hasattr(p_args, p_name):

		return hasattr(p_args, p_name + DefaultArgs.s_nondefault_str)

	s_nondefault_str = "_nondefault"


# Classes
 
# Performs profiling over TeiTag objects
class StructuralProfiling(object):

	def __init__(self):

		pass

# Contains metadata/stats about a tei tag in a group of tei files
class TeiTag(object):

	# Constructor

	def __init__(self, p_tag_name, p_folder, p_file_list, p_publication_tag="",
		p_publication_names=[], p_force_soup_build=False):

		print("===================================")
		print("TeiTag constructor")
		print("Name: {}".format(p_tag_name))
		# print("Folder: {}".format(p_folder))
		# print("File list: {}".format(p_file_list))

		# 0. Save parameters as member values
		self.m_name = p_tag_name
		self.m_folder = p_folder
		self.m_file_list = p_file_list
		self.m_publication_tagname = p_publication_tag
		self.m_publication_names = p_publication_names

		# 1. Fields to be populated
		self.m_tag_attributes = {}
		self.m_tag_counts = {}
		self.m_file_appearances = 0
		self.m_average_cardinality = 0
		self.m_median_cardinality = 0
		self.m_publication_cardinality = {}
		self.m_total_cardinality = 0

		# 2. Gather soup objects into memory for all tei files in this folder
		# Persistent - stays in memory until program end or explicit garbage collection
		if p_force_soup_build or 0 == len(TeiTag.s_soup_storage.keys()):
			self.build_soup_objects()

		# 3. Save information on attributes used for this tag
		self.__get_tag_attributes()

		# 4. Calculate stats on this tag in the given files
		self.__calculate_cardinality()

	# Private methods

	def __calculate_cardinality(self):

		# 1. Look through each tei file for the tag
		for tei_filename in self.m_file_list:

			# A. Get the pre-built BeautifulSoup object
			soup = self.s_soup_storage[tei_filename]

			# B. Record the number of this tag's occurrences in this file
			self.m_tag_counts[tei_filename] = len(soup.find_all(self.m_name.lower()))

			# C. Tally the number of files this tag appears in
			if self.m_tag_counts[tei_filename] >= 1:
				self.m_file_appearances += 1

		if self.m_file_appearances == 0:
			print("{0} tag has 'zero' appearances".format(self.m_name))

		# 2. Calculate cardinality stats across all files

		# A. Total cardinality is the count of tag occurrences across all files
		self.m_total_cardinality = sum(self.m_tag_counts.values())

		# B. Average cardinality is the average number of occurrences across the files it appears in
		self.m_average_cardinality = float(self.m_total_cardinality) / float(self.m_file_appearances)

		# C. Median cardinality is the median number of occurrences across the files it appears in
		tag_appearance_buckets = {}
		for tei_filename in self.m_tag_counts:

			# i. Make sure the tag appears in this file at least once
			if self.m_tag_counts[tei_filename] >= 1:
				str_count = str(self.m_tag_counts[tei_filename])
				if str_count not in tag_appearance_buckets:
					tag_appearance_buckets[str_count] = 0
				tag_appearance_buckets[str_count] += 1

		highest_appearances = max(tag_appearance_buckets.values())
		medians = []
		for count in tag_appearance_buckets:
			if highest_appearances == tag_appearance_buckets[count]:
				medians.append(count)
		self.m_median_cardinality = "\"" + ",".join(medians) + "\""

		# D. Publication cardinality

		# I. Stores count of appearances of this tag by publication name
		self.m_publication_cardinality = { publication_name: 0 for publication_name in self.m_publication_names }

		# II. Look through tei files for publication name
		for tei_filename in self.m_file_list:

			if self.m_tag_counts[tei_filename] >= 1:

				# A. Get the pre-built BeautifulSoup object
				soup = self.s_soup_storage[tei_filename]

				# b. Get the publication name
				for publication_tag in soup.find_all(self.m_publication_tagname.lower()):

					# i. Count the publication name appearance for this tag
					self.m_publication_cardinality[publication_tag.p.string] += 1

		self.print_stats()

	def __get_tag_attributes(self):

		# 1. Look through each tei file for the tag
		for tei_filename in self.m_file_list:

			# A. Get the pre-built BeautifulSoup object
			soup = self.s_soup_storage[tei_filename]

			# B. Record the number of this tag's occurrences in this file
			tags = soup.find_all(self.m_name.lower())

			# C. Save all attributes and their values for each tag instance
			for tag in tags:
				for attr in tag.attrs:
					
					# I. Check to see if attribute in dictionary and tally it
					if attr not in self.m_tag_attributes:
						self.m_tag_attributes[attr] = { "count": 0, "values": {} }
					self.m_tag_attributes[attr]["count"] += 1

					# II. Check to see if value in attribute dictionary and tally it
					if tag.attrs[attr] not in self.m_tag_attributes[attr]["values"]:
						self.m_tag_attributes[attr]["values"][tag.attrs[attr]] = 0
					self.m_tag_attributes[attr]["values"][tag.attrs[attr]] += 1

	# Properties

	@property
	def average_cardinality(self):
		return self.m_average_cardinality
	@property
	def median_cardinality(self):
		return self.m_median_cardinality
	@property
	def publication_cardinality(self):
		return self.m_publication_cardinality
	@property
	def total_cardinality(self):
		return self.m_total_cardinality

	@property
	def name(self):
		return self.m_name
	@property
	def attributes(self):
		return self.m_tag_attributes
	
	# Public methods

	def build_soup_objects(self):

		# 0. Clear any BeautifulSoupObjects from memory
		TeiTag.clear_soup_objects()

		# 1. Contstruct soup objects from this tag's tei folder
		for tei_filename in self.m_file_list:

			# Double-check for file existence as file could have been curated out
			if os.path.exists(self.m_folder + tei_filename):

				with open(self.m_folder + tei_filename, "r") as tei_file:

					# A. Create and store a BeautifulSoup object from the file
					TeiTag.s_soup_storage[tei_filename] = BeautifulSoup(tei_file, "lxml")

	def output_attribute_info(self, p_output_path):

		with open(p_output_path + self.m_name + ".csv", "w") as output_file:

			# A. Write csv header
			header_line = "attribute,attribute_count,value|value_count\n"
			output_file.write(header_line)

			# B. Construct and write attribute/value info row
			for attr in self.m_tag_attributes:
				output_line = "{0},{1},".format(attr, self.m_tag_attributes[attr]["count"])
				values = ""
				for value in self.m_tag_attributes[attr]["values"]:
					values += "{0}|{1},".format(value, self.m_tag_attributes[attr]["values"][value])
				output_line += values.rstrip(",") + "\n"
				output_file.write(output_line)

	def print_stats(self):

		# Cardinality stats
		print("Cardinality")
		print("\tTotal: {}".format(self.m_total_cardinality))
		print("\tAverage: {}".format(self.m_average_cardinality))
		print("\tMedian: {}".format(self.m_median_cardinality))
		print("\tPublication: {}".format(self.m_publication_cardinality))

	# Static methods and variable

	@staticmethod
	def clear_soup_objects():

		# 1. Trigger garbage collection for in-memory BeautifulSoup objects
		TeiTag.s_soup_storage = {}	

	@staticmethod
	def get_tag_fieldvalues(p_tag, p_has_internal_p=False, p_input_path=paths["tei_path"]):

		# 1. Go through the tei files and look for the given tag
		tag_values = []
		for xml_filepath in glob.glob(p_input_path + "*"):

			# A. Process the file with BeautifulSoup and look for tags
			with open(xml_filepath, "r") as xml_file:

				# i. Create BeautifulSoup object
				soup = BeautifulSoup(xml_file, "lxml")

				# ii. Find all instances of this tag (exception for internal p tags)
				if p_has_internal_p:
					tag_values.extend([tag.p.string for tag in soup.find_all(p_tag.lower())])
				else:
					tag_values.extend([tag.string for tag in soup.find_all(p_tag.lower())])

		return Counter(tag_values)	

	@staticmethod
	def get_tag_cardinality():

		# 1. Get all tag names
		tag_filenames = [tag_filepath[tag_filepath.rfind(os.sep) + 1:] \
			for tag_filepath in glob.glob(paths["html_path"] + "*")]
		tag_filenames.remove("index.html")
		tag_names = [tag_filename.split(".")[0] for tag_filename in tag_filenames]

		# 2. Get a list of files in which this tag appears
		# tei_filenames = {}
		# for tag in tag_names:
			
		# 	tag_filepath = paths["html_path"] + tag + ".html"

		# 	# A. Create a soup object based on this html file
		# 	with open(paths["html_path"] + tag + ".html", "r") as tag_file:
				
		# 		soup = BeautifulSoup(tag_file, features="lxml")

		# 		# B. Get the href attribute for all anchor tags
		# 		# Example value
		# 		# file:///Users/PeregrinePickle/Documents/Digital_Humanities/dickinson/scripts/../tei/2911.tei
		# 		href_values = [anchor_tag["href"] for anchor_tag in soup.find_all("a")]

		# 		# C. Separate out the tei filename from each full path
		# 		tei_filenames[tag] = [tei_filepath[tei_filepath.rfind(os.sep) + 1:] \
		# 			for tei_filepath in href_values]

		# 2. Get a list of all tei filenames to search for tags in
		tei_filenames = [filepath[filepath.rfind(os.sep) + 1:] for filepath in glob.glob(paths["tei_path"] + "*.tei")]

		# 3. Get publication names
		publication_names = TeiTag.get_tag_fieldvalues("publicationstmt", True).keys()

		# 4. Count tags across all files in the tei folder
		tag_objects = {}
		for tag in tag_names:

			# A. Create a tag object that will determine its cardinality across all tei files
			tag_objects[tag] = TeiTag(tag, paths["tei_path"], tei_filenames, "publicationstmt", publication_names)

		# 4. Output cardinality stats to a csv file
		with open(paths["output_path"] + "tei_cardinality.csv", "w") as output_file:

			# I. Write out header line
			header_line = "tag_name,average,median,total,"
			for publication_name in publication_names:
				header_line += "\"{0}\",".format(publication_name)
			header_line = header_line.rstrip(",") + "\n"
			output_file.write(header_line)

			# II. Write out cardinality data for each tag
			for tag in tag_objects:

				output_line = "{0},{1},{2},{3},".format(
					tag_objects[tag].name,
					tag_objects[tag].average_cardinality,
					tag_objects[tag].median_cardinality,
					tag_objects[tag].total_cardinality)

				for publication_name in publication_names:
					if publication_name in tag_objects[tag].publication_cardinality:
						output_line += "{0},".format(tag_objects[tag].publication_cardinality[publication_name])
					else:
						output_line += "0,"

				output_line = output_line.rstrip(",") + "\n"

				output_file.write(output_line)

	@staticmethod
	def get_tag_info(p_tag, p_input_path):

		# 1. Get a list of all tei filenames to search for tags in
		tei_filenames = [filepath[filepath.rfind(os.sep) + 1:] for filepath in glob.glob(p_input_path + "*.tei")]

		# 2. Instantiate tag
		my_tag = TeiTag(p_tag, p_input_path, tei_filenames)

		# 3. Output collection tag information to the screen
		my_tag.print_stats()

	@staticmethod
	def get_all_tag_attribute_info(p_input_path, p_output_path):

		# 1. Get all tag names
		tag_filenames = [tag_filepath[tag_filepath.rfind(os.sep) + 1:] \
			for tag_filepath in glob.glob(paths["html_path"] + "*")]
		tag_filenames.remove("index.html")
		tag_names = [tag_filename.split(".")[0] for tag_filename in tag_filenames]

		# 2. Get attribute info for each tag
		tag_objects = []
		for tag in tag_names:
			tag_obj = TeiTag.get_tag_attribute_info(tag, p_input_path, p_output_path, False)
			tag_objects.append(tag_obj)

		# 3. Output attribute info for each tag into one csv file
		TeiTag.output_attribute_info_multiple_tags(tag_objects, p_output_path)

	@staticmethod
	def get_tag_attribute_info(p_tag, p_input_path, p_output_path, p_output=True):

		# 0. Get a list of all tei filenames to search for tags in
		tei_filenames = [filepath[filepath.rfind(os.sep) + 1:] for filepath in glob.glob(p_input_path + "*.tei")]

		# 0. Get publication names
		publication_names = TeiTag.get_tag_fieldvalues("publicationstmt", True).keys()

		# 1. Make a tag object
		tag_object = TeiTag(p_tag, p_input_path, tei_filenames, "publicationstmt", publication_names)

		# 2. Write counts of the tag's attributes and their respective values to csv file
		if p_output:
			tag_object.output_attribute_info(p_output_path)
		else:
			return tag_object

	@staticmethod
	def output_attribute_info_multiple_tags(p_tag_objects, p_output_path):

		with open(p_output_path + "tei_tag_attribute_cardinality.csv", "w") as output_file:

			# A. Write csv header
			header_line = "tag_name,attribute,attribute_count,value|value_count\n"
			output_file.write(header_line)

			# B. Construct and write attribute/value info row
			for tag_object in p_tag_objects:

				# I. Write line with just the tag name
				output_file.write("{0}\n".format(tag_object.name))

				# II. Write the next line accounting for all attributes
				for attr in tag_object.attributes:
					
					# a. Blank space for tag name indent, attribute, attribute count
					output_line = "\"\",{0},{1},".format(attr, tag_object.attributes[attr]["count"])

					# b. Attribute values
					values = ""
					for value in tag_object.attributes[attr]["values"]:
						values += "{0}|{1},".format(value, tag_object.attributes[attr]["values"][value])

					# c. Write attribute info
					output_line += values.rstrip(",") + "\n"
					output_file.write(output_line)

	# Stores BeautifulSoup objects for tei files currently being examined
	s_soup_storage = {}

# Primary analysis/output functions
class XmlAnalysis(object):

	# Static methods	

	@staticmethod
	def create_tag_html_files(p_input_path, p_output_path):

		blank_line_count = 0
		tag_set = []
		files_by_tag = {}
		for xml_filepath in glob.glob(p_input_path + "*"):
		    
			# Parse the tei file
			tei_file_root = xml.etree.ElementTree.parse(xml_filepath).getroot()

			# TEI filename
			filename = os.path.basename(xml_filepath)

			# Examine the tags
			for child in tei_file_root.iter():
				
				if child.tag not in files_by_tag: 
					files_by_tag[child.tag] = []
				if filename not in files_by_tag[child.tag]:
					files_by_tag[child.tag].append(filename)

				tag_set.append(child.tag)

				if XmlAnalysis.is_blankline(child):
					blank_line_count += 1


		# De-dupe file lists
		for tag in files_by_tag:
			files_by_tag[tag] = list(set(files_by_tag[tag]))

		# Get tag counts
		tag_counter = Counter([XmlAnalysis.tagname_nonamespace(tag) for tag in tag_set])

		# Output an html file per tag
		for tag in files_by_tag:

			with open(p_output_path + XmlAnalysis.tagname_nonamespace(tag) + ".html", "w") as output_file:

				# Build the file html
				lines = []
				lines.append("<html>\n")
				lines.append("\t<body>\n")
				lines.append("\t\t<p>Occurrences in corpus: {0}</p>\n".format(tag_counter[XmlAnalysis.tagname_nonamespace(tag)]))
				lines.append("\t\t<p>\n")
				for fn in files_by_tag[tag]:
					lines.append("\t\t\t<a href=\"{0}\">{1}</a><br/>\n".format("file://" + paths["tei_path"] + fn, fn))
				lines.append("\t\t</p>\n")
				lines.append("\t</body>\n")
				lines.append("</html>")

				# Output the html
				output_file.write("".join(lines))

		# Create an index html file to link to all tag html files
		with open(p_output_path + "index.html", "w") as output_file:

			# Build the file html
			lines = []
			lines.append("<html>\n")
			lines.append("\t<body>\n")
			lines.append("\t\t<p>Number of tags: {0}</p>\n".format(len(tag_counter.keys())))
			lines.append("\t\t<p>\n")
			for tag in tag_counter:
				lines.append("\t\t\t<a href=\"file://{0}{1}.html\">{2}</a><br/>\n".format(paths["html_path"], tag, tag))
			lines.append("\t\t</p>\n")
			lines.append("\t</body>\n")
			lines.append("</html>")

			# Output the html
			output_file.write("".join(lines))				

	@staticmethod
	def find_similar_titles_in_collection(p_input_path, p_output_path):

		# Initialize distance table with titles
		title_table = []
		fileid_table = []
		for xml_filepath in glob.glob(p_input_path + "*"):
			with open(xml_filepath, "rU") as xml_file:
				soup = BeautifulSoup(xml_file, "xml")
				title = soup.find_all("titleStmt")[0].title.string
				title_table.append(title)
				fileid_table.append(os.path.splitext(os.path.basename(xml_filepath))[0])

		# Fill in the distance table with Levenshtein title distances
		for index in range(len(title_table)):
			distance_table = []
			for compared_title in title_table:
				distance_table.append([fileid_table[index], compared_title, editdistance.eval(title_table[index], compared_title)])
			with open(p_output_path + fileid_table[index] + ".json", "w") as output_file:
				output_file.write(sorted(distance_table, key=lambda x: x[2], reverse=True))

		# 10 closest titles
		# print(sorted(distance_table[distance_table.keys()[0]][0:10], key=lambda x: x[1], reverse=True))

	# Requires:
	# (1) Definition of "corpus_folder_map" dict to match publication names to new subfolder names
	# (2) Listed subfolders in "corpus_folder_map" are already created
	@staticmethod
	def split_by_publication(p_input_path, p_output_path):

		# 1. Go through the tei files and split corpus up by publisher
		for xml_filepath in glob.glob(p_input_path + "*"):

			with open(xml_filepath, "rU") as xml_file:

				# A. Create a soup object for this file
				soup = BeautifulSoup(xml_file, "xml")

				# B. Find all publication tags in the file
				publication = soup.find_all("publicationStmt")[0].p.string

				# C. Copy this file to the appropriate subfolder given the publication name
				if os.path.exists(p_output_path + corpus_folder_map[publication] + "/"):
					copyfile(xml_filepath, 
							 p_output_path + corpus_folder_map[publication] + "/" + os.path.basename(xml_filepath))

	# Utility methods

	@staticmethod
	def is_blankline(p_xml_node):

		return XmlAnalysis.namespace_tagname("l") == p_xml_node.tag and \
			   (not p_xml_node.text or 0 == len(p_xml_node.text.strip()))

	@staticmethod
	def namespace_tagname(p_tag):

		return "{0}".format(tei_namespace) + p_tag

	@staticmethod
	def tagname_nonamespace(p_tag_w_namespace):

		return p_tag_w_namespace[len(tei_namespace):]	

def main(p_args):

	# pdb.set_trace()

	# 1. Look through terminal arguments for requested functionality

	# XmlAnalysis functions

	if DefaultArgs.hasattr(p_args, "create"):
		my_args = set_args(p_args, "create")
		XmlAnalysis.create_tag_html_files(my_args[0], my_args[1])

	elif DefaultArgs.hasattr(p_args, "similartitles"):
		# Ex. XmlAnalysis.find_similar_titles_in_collection(paths["split_corpus_path"] + "franklin_1998/")
		my_args = set_args(p_args, "similartitles")
		XmlAnalysis.find_similar_titles_in_collection(my_args[0], my_args[1])

	elif DefaultArgs.hasattr(p_args, "splitpublication"):
		my_args = set_args(p_args, "splitpublication")
		XmlAnalysis.split_by_publication(my_args[0], my_args[1])

	# TeiTag functions

	elif DefaultArgs.hasattr(p_args, "tagfieldvalues"):
		# Ex. TeiTag.get_tag_fieldvalues("add", False, paths["split_corpus_path"] + "franklin_1998/")
		# 	  print(TeiTag.get_tag_fieldvalues("publicationStmt", True))
		my_args = set_args(p_args, "tagfieldvalues")
		TeiTag.get_tag_fieldvalues(my_args[0], my_args[1], my_args[2])
	
	elif DefaultArgs.hasattr(p_args, "tagcardinality"):
		my_args = set_args(p_args, "tagcardinality")
		TeiTag.get_tag_cardinality(my_args[0], my_args[1], my_args[2])

	elif DefaultArgs.hasattr(p_args, "taginfo"):
		# Ex. TeiTag.get_tag_info("sourceDesc")
		my_args = set_args(p_args, "taginfo")
		TeiTag.get_tag_info(my_args[0], my_args[1])

	elif DefaultArgs.hasattr(p_args, "attributeinfo"):
		my_args = set_args(p_args, "attributeinfo")
		TeiTag.get_tag_attribute_info(my_args[0], my_args[1], my_args[2])

	elif DefaultArgs.hasattr(p_args, "allattributeinfo"):
		my_args = set_args(p_args, "allattributeinfo")
		TeiTag.get_all_tag_attribute_info(my_args[0], my_args[1])

	# Sandbox 

	else:
		return

if "__main__" == __name__:

	# 1. Describe arguments and retrieve their values from input

	# A. XmlAnalysis args
	parser.add_argument(
		"-c",
		"--create",
		action=DefaultArgs,
		default=[paths["tei_path"], paths["html_path"]],
		help="Create a hierarchical set of html files that " + 
		"explores a tei collection")
	parser.add_argument(
		"-st",
		"--similartitles",
		action=DefaultArgs,
		default=[paths["tei_path"], paths["title_distance_path"]],
		help="Find similar titled texts across a collection")
	parser.add_argument(
		"-sp",
		"--splitpublication",
		action=DefaultArgs,
		default=[paths["tei_path"], paths["split_corpus_path"]],
		help="Divide tei files by publication name into separate folders")

	# B. TeiTag args
	parser.add_argument(
		"-tfv",
		"--tagfieldvalues",
		action=DefaultArgs,
		default=["tei", "True", paths["tei_path"]],
		help="Find all values for a tag in an xml file collection")
	parser.add_argument(
		"-tc",
		"--tagcardinality",
		action=DefaultArgs,
		default=[paths["html_path"], paths["tei_path"], paths["output_path"]],
		help="Counts the number of instances of all tags in an xml file collection.\n" + 
		"Requires a run of create_tag_html_files() beforehand.")
	parser.add_argument(
		"-ti",
		"--taginfo",
		action=DefaultArgs,
		default=["tei", paths["tei_path"]],
		help="Shows all stats for a particular tag in an xml file collection.")
	parser.add_argument(
		"-ai",
		"--attributeinfo",
		action=DefaultArgs,
		default=["tei", paths["tei_path"], paths["output_path"]],
		help="Outputs csv file containing attribute and value counts for a tag.")
	parser.add_argument(
		"-aai",
		"--allattributeinfo",
		action=DefaultArgs,
		default=[paths["tei_path"], paths["output_path"]],
		help="Outputs csv files containing attributes and value counts for all tags.",
		nargs="*")

	# 2. Run main script
	main(parser.parse_args())


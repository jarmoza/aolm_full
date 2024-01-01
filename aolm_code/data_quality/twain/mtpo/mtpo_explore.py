# Author: Jonathan Armoza
# Project: Art of Literary Modeling
# Date: October 22, 2019
# Purpose: Some brief explorations of the TEI XML files and other (meta)data from
# 		   Mark Twain Project Online (http://www.marktwainproject.org/)
# Credits: Terence Catapano of MTPO (assisted with file location and usage
# 		   rights determination, 2018-2019)
# Initial access date of files: September 5, 2019

import argparse 			  	# Terminal arguments
from collections import Counter	# Counts all values in a list
from bs4 import BeautifulSoup	# Parse TEI XML file for a Mark Twain work

from mtpo_commons import mtpo   # Data about the Mark Twain Project TEI collection


class MTPO_Volume:

	def __init__(self, p_filepath):

		# 1. Ingest the TEI as a BeautifulSoup object
		with open(p_filepath, "r") as tei_file:
			self.m_soup = BeautifulSoup(tei_file.read(), "lxml")

	def get_attributes_for_tag(self, p_tag, p_attribute):

		# Stores all values of the requested attribute
		attribute_values = []

		# 1. Get all of the requested tags in the soup
		all_tags = self.m_soup.find_all(p_tag)

		# 2. Save all attribute values (if listed in tag)
		for tag in all_tags:
			if tag.has_attr(p_attribute):
				attribute_values.append(tag[p_attribute])

		# 3. Create and return a counting dictionary of the attribute values
		return Counter(attribute_values)

	def get_tags_by_attribute_value(self, p_tag, p_attribute, p_attribute_value):

		# Stores all tag contents
		tag_contents = []

		# 1. Get all of the requested tags in the soup
		all_tags = self.m_soup.find_all(p_tag)

		# 2. Save all tags by requested attribute values (if listed in tag)
		for tag in all_tags:
			if tag.has_attr(p_attribute) and \
			   p_attribute_value == tag[p_attribute]:
				tag_contents.append(tag.contents)

		return tag_contents


def parse_arguments():

	# 1. Create the argument parser
	parser = argparse.ArgumentParser()

	# 2. Define MTPO Scraping Possibilities
	parser.add_argument("filename",
						choices=mtpo["known_files_dict"].keys(),
						help="Filename of MTPO title to explore")
	parser.add_argument("-t", "--tag", help="Name of tags to retrieve")
	parser.add_argument("-a", "--attribute", help="Name of attribute to retrieve from a tag [See -t option].")
	parser.add_argument("-av", "--attribute_value", help="Attribute value to look for in a tag [See -t option].")

	# 3. Parse arguments passed in through the terminal
	arguments = parser.parse_args()

	return arguments

def main():

	# 1. Get arguments from the terminal
	arguments = parse_arguments()

	print("Arguments read: {0}".format(arguments))

	# 2. Look for tag/attribute to retrieve in a given title
	if arguments.filename and arguments.tag:

		# a. Ingest the TEI file
		mtpo_volume = MTPO_Volume(mtpo["folders"]["autobiographies"] + arguments.filename)

		if arguments.attribute and not arguments.attribute_value:

			# b. Retrieve the attribute values for the given tag
			attribute_values = mtpo_volume.get_attributes_for_tag(arguments.tag, arguments.attribute)

			# c. Output the attribute values
			for val in attribute_values:
				print("{0}: {1}".format(val, attribute_values[val]))

		elif arguments.attribute and arguments.attribute_value:

			# b. Retrieve all tags with the given attribute value
			tag_contents = mtpo_volume.get_tags_by_attribute_value(arguments.tag,
				arguments.attribute, arguments.attribute_value)

			print("Number of tags: {0}".format(len(tag_contents)))

			# c. Output the separate tag contents
			index = 0
			for contents in tag_contents:
				index += 1
				print("Loop {0}".format(index))
				with open(mtpo["folders"]["output"] + 
						  "{0}_{1}_{2}_{3}.txt".format(arguments.tag,
						  	arguments.attribute, arguments.attribute_value, index), "w") as output_file:
					output_file.write(str(contents))


if "__main__" == __name__:
	main()

"""
Author: Jonathan Armoza
Creation date: May 25, 2021
Last Updated: May 25, 2021
Purpose: Reads poems from Emily Dickinson's 'Bolts of Melody'
         edited by Millicent Todd Bingham
"""


# Imports

# Built-in
import os
import re
import string
import sys

# Local
from aolm_paths import data_paths
from aolm_utilities import clean_word
from aolm_utilities import output_dividers
from bingham_bolts import bolts_guide
from dickinson_poem import DickinsonPoem
from ed_poem_reader import PoemReader


# Globals

text_locations = {
	
	"bolts": "{0}bingham{1}processed{1}".format(paths["data"], os.sep) + \
			 "bingham_bolts_of_melody_internetarchive_accessed021021_processed.txt",
}


# Classes

class BoltsReader(PoemReader):

	def __init__(self, p_filepath, p_source_map):

		super.init(p_filepath, p_source_map)

		self.m_table_of_contents = {}

	def print_stats(self, test_poem_number=0):

		print("Number of poems: {0}".format(len(self.m_poems)))
		print("Table of contents\n{0}".format(self.m_table_of_contents))

		for section in self.m_source_map["sections"]:

			print(output_dividers["section"])
			print(section)

			for subsection in self.m_source_map["subsections"][section]:

				print(output_dividers["subsections"])
				print(subsection)
				
				if subsection in self.m_source_map["subsubsections"]:
					for subsubsection in self.m_source_map["subsubsections"][subsection]:

						print(output_dividers["subsubsection"])
						print(subsubsection)

						for poem in self.m_poems:
							if section == poem.section and \
							   subsection == poem.subsection and \
							   subsubsection == poem.subsubsection:
							   print("* " + poem.title)
				else:
					for poem in self.m_poems:
						if section == poem.section and \
						   subsection == poem.subsection:
							   print("* " + poem.title)

	def read_books(self):

		# 0. Setup

		# Book locale
		default_locale = BoltsPoem.default_locale
		book_locale = {

			"section": default_locale,
			"subsection": default_locale,
			"subsubsection": default_locale
		}

		# Poem identifier
		poem_start_regex = self.m_source_map["poem_identifier_regex"]

		# Storage for poem lines
		poem_lines = []

		# Reading flags
		new_poem = False
		new_section = False
		reading_poem = False
		
		# 1. Read in poems in this book
		with open(self.m_filepath, "r") as book_file:

			# A. Read in lines from file
			book_lines = book_file.readlines()

			# B. Parse lines and store as poem objects
			for line in book_lines:

				# I. Clean line of leading and trailing whitespace
				clean_line = line.strip()

				# II. Ignore lines in page ignore list
				if clean_line in self.m_source_map["page_ignore"]:
					continue

				# III. Check for book locale

				# a. Check for a new section
				if clean_line in self.m_source_map["sections"]:
					book_locale["section"] = clean_line
					book_locale["subsection"] = default_locale
					book_locale["subsubsection"] = default_locale

					# print("FOUND SECTION: " + clean_line)

					# Add section to table of contents
					self.m_table_of_contents[book_locale["section"]] = {}
					
					new_section = True

				# b. Check for a new subsection
				elif default_locale != book_locale["section"] and \
					 clean_line in self.m_source_map["subsections"][book_locale["section"]]:

					# print("FOUND SUBSECTION: " + clean_line)
					
					book_locale["subsection"] = clean_line
					book_locale["subsubsection"] = default_locale

					# Add subsection to current section in table of contents
					self.m_table_of_contents[book_locale["section"]][book_locale["subsection"]] = {}

					new_section = True

				# c. Check for a sub-subsection
				elif default_locale != book_locale["subsection"] and \
					 book_locale["subsection"] in self.m_source_map["subsubsections"] and \
					 clean_line in self.m_source_map["subsubsections"][book_locale["subsection"]]:

					# print("FOUND SUBSUBSECTION: " + clean_line)
					
					book_locale["subsubsection"] = clean_line

					# Add sub-subsection to current subsection in table of contents
					if isinstance(self.m_table_of_contents[book_locale["section"]][book_locale["subsection"]], list):
						self.m_table_of_contents[book_locale["section"]][book_locale["subsection"]] = {}
					self.m_table_of_contents[book_locale["section"]][book_locale["subsection"]][book_locale["subsubsection"]] = []					

					new_section = True

				# d. Check for poem start
				elif re.match(poem_start_regex, clean_line):
					new_poem = True

				# e. Check if reading poem
				elif reading_poem:
					poem_lines.append(clean_line)

				# f. Check if this line indicated section or poem start
				if new_section or new_poem:

					# i. Save the current poem if one was being read
					if reading_poem:

						self.m_poems.append(BoltsPoem(poem_id, poem_lines,
							book_locale["section"], book_locale["subsection"],
							book_locale["subsubsection"]))

						# last_poem = self.m_poems[len(self.m_poems) - 1]
						# print("New poem added in {0}, {1}, {2}".format(last_poem.section,
						# 	last_poem.subsection, last_poem.subsubsection))


						# Add poem to current sub-subsection in table of contents
						if book_locale["subsubsection"] != BoltsPoem.default_locale:
							self.m_table_of_contents[book_locale["section"]][book_locale["subsection"]][book_locale["subsubsection"]].append(poem_lines[0])
						else:
							self.m_table_of_contents[book_locale["section"]][book_locale["subsection"]] = []
							self.m_table_of_contents[book_locale["section"]][book_locale["subsection"]].append(poem_lines[0])

					# ii. Save the new poem id if starting new poem
					if new_poem:
						poem_id = clean_line

					# iii. Clear all lines from previous poem in temp storage
					poem_lines = []

					# iv. Flag if a poem is about to be read
					reading_poem = True if new_poem else False

					# v. Reset new flags
					new_section = False
					new_poem = False


class BoltsPoem(DickinsonPoem):

	# Constructor	

	def __init__(self, p_id, p_lines, p_section, p_subsection, p_subsubsection=""):	

		self.m_id = p_id
		self.m_lines = p_lines

		self.m_section = p_section
		self.m_subsection = p_subsection
		self.m_subsubsection = p_subsubsection
		if "" == self.m_subsubsection:
			self.m_subsubsection = BoltsPoem.default_locale

		# Find title
		self.m_title = ""
		for index in range(len(self.m_lines)):
			if len(self.m_lines[index].strip()) > 0:
				self.m_title = self.m_lines[index]		


	# Properties

	@property
	def lines(self):
		return self.m_lines
	@property
	def section(self):
		return self.m_section
	@property
	def subsection(self):
		return self.m_subsection
	@property
	def subsubsection(self):
		return self.m_subsubsection
	@property
	def title(self):
		return self.m_title
	
	
	# Static fields

	default_locale = "N/A"


# Test function
def main():

	pass

if "__main__" == __name__:
	main()
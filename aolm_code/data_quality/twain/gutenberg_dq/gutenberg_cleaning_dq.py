# Author: Jonathan Armoza
# Creation date: October 9, 2021
# Purpose: Iterative look at how text cleaning processes affect data quality of
# 		   Project Gutenberg texts

import os

# Classes

# Project Gutenberg text base class
class ProjectGutenbergText(object):
	
	# Constructor and Private Methods
	def __init__(self, p_filepath, p_file_components, p_component_reading_method):

		# 0. Class field initialization
		self.m_components = p_file_components
		self.m_raw_text = ""
		self.m_text_filepath = p_filepath
		self.m_text_filename = os.path.basename(self.m_text_filepath)

		# 0. Save parameters
		self.__read_components = p_component_reading_method

		# 1. Read in the file in raw, plain text
		self.__read_raw_text()

		# 2. Store file data (header, body, footer, etc.)
		self.__read_components()

	def __read_raw_text(self):

		with open(self.m_text_filepath, "r") as text_file:
			self.m_raw_text = text_file.readlines()
			
	@property
	def components(self):
		return self.m_components

	def output(self, p_output_folder):

		illegal_filename_chars = ": .,"

		# 1. Make a folder in the given output folder based on the filename
		full_folder = p_output_folder + os.path.splitext(self.m_text_filename)[0] + os.sep
		if not os.path.isdir(full_folder):
			os.mkdir(full_folder)

		# 2. Output each component as its own file into the given output folder
		for key in self.m_components:

			# A. Transform key into filename
			filename = key
			for ch in illegal_filename_chars:
				if ch in filename:
					filename = filename.replace(ch, "_")

			# B. Write out component as text file
			with open(full_folder + filename + ".txt", "w") as component_file:
				component_file.write("\n".join(self.m_components[key]))
			
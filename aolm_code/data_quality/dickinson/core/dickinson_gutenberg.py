# Author: Jonathan Armoza
# Creation date: January 28, 2021
# Purpose: Read and store Dickinson txt files downloaded from Project Gutenberg


# Imports

# Built-ins
import os


# Globals
paths = {

	"gutenberg_data_path": os.getcwd() + "{0}..{0}gutenberg{0}".format(os.sep)
}


# Utility functions
def is_roman_numeral(p_string):

	# 0. Short circuit blank strings
	if 0 == len(p_string):
		return False

	# Roman numeral characters
	valid_roman_numerals = ["M", "D", "C", "L", "X", "V", "I", "(", ")"]

	# 1. Uppercase the string
	p_string = p_string.upper()

	# 2. Search for an invalid character
	valid = True
	for letter in p_string:
		if letter not in valid_roman_numerals:
			valid = False
			break

	return valid

def is_all_caps(p_string):

	return False not in [ord(ch) >= ord('A') and ord(ch) <= ord('Z') for ch in p_string]


# Classes
class GutenbergDickinsonPoem:

	# Constructor

	def __init__(self, p_raw_title, p_raw_lines):

		# 1. Process title and lines from txt file
		self.m_title = self.__process_raw_title(p_raw_title)
		self.m_stanzas, self.m_lines = self.__process_raw_lines(p_raw_lines)

		# 2. Determine if poem is without 'real' title
		self.m_title_is_numeral = is_roman_numeral(self.m_title)

	# Private methods

	def __process_raw_lines(self, p_raw_lines):

		index = -1
		lines = []
		stanzas = []
		new_stanza = True
		
		# 1. Process given lines as collection of stanzas and lines
		for line in p_raw_lines:

			# A. Clean whitespace surrounding line
			clean_line = line.strip()

			# B. Check to see if new stanza flagged
			if new_stanza:
				index += 1
				new_stanza = False
				stanzas.append([])

			# C. Skip blank lines, signaling new stanza
			if 0 == len(clean_line):
				new_stanza = True
				continue

			# D. Stores this line in the current stanza and collection of lines
			lines.append(clean_line)
			stanzas[index].append(clean_line)
			
		return stanzas, lines

	def __process_raw_title(self, p_raw_title):

		return p_raw_title.strip().rstrip(".")

	# Properties

	@property
	def has_real_title(self):
		return not self.m_title_is_numeral
	@property
	def lines(self):
		return self.m_lines
	@property
	def stanzas(self):
		return self.m_stanzas
	@property
	def title(self):
		return self.m_title

	# Static methods

	@staticmethod
	def is_roman_numeral_line(p_string):

		clean_line = p_string.strip()
		return clean_line.endswith(".") and \
			is_roman_numeral(clean_line.rstrip("."))

	@staticmethod
	def is_title_line(p_string):

		clean_line = p_string.strip()
		return clean_line.endswith(".") and \
			is_all_caps(clean_line.rstrip("."))

	@staticmethod
	def read_poems_from_file(p_folder, p_filename):

		# 0. Stores all poem objects
		poems = []

		with open(p_folder + p_filename, "r") as input_file:

			# 0. Get the line to start reading after from the static file dictionary
			start_line = GutenbergDickinsonPoem.filename_dict[p_filename]

			# 0. Stores preprocessed title and stanzas
			raw_title = ""
			raw_lines = []
			temp_title = ""
	
			# 1. Read all lines of the file into memory
			lines = list(input_file.readlines())
			
			# 2. Read lines till beginning of poems in file
			index = 0
			for index in range(len(lines)):

				# 0. Clean whitespace
				clean_line = lines[index].strip()

				# A. Short circuit continue blank lines
				if 0 == len(clean_line):
					continue
				
				# B. Check for start line
				if start_line == clean_line:
					index += 1
					break

			# 3. Read all poems and store as poem objects
			reading_poem = False
			for index in range(index, len(lines)):

				# 0. Clean whitespace
				clean_line = lines[index].strip()				

				# A. Read poem lines
				if not reading_poem:

					# I. Short circuit continue blank lines
					if 0 == len(clean_line):
						continue

					# II. Check for title and roman numeral preface
					if GutenbergDickinsonPoem.is_roman_numeral_line(clean_line):

						# a. Flag poem beginning
						reading_poem = True

						# b. Save roman numeral as possible temp title
						# (for poems without titles)
						temp_title = clean_line.rstrip(".")

						continue
				else:

					# I. Short circuit continue blank lines unless more stanzas coming
					if 0 == len(clean_line):
						
						# a. Check to see if poem done
						if len(raw_lines) and \
						   index < len(lines) and \
						   0 == len(lines[index + 1].strip()):
							
							# i. Flag poem end
							reading_poem = False

							# ii. Store current poem
							title_to_use = raw_title if len(raw_title) > 0 else temp_title
							poems.append(GutenbergDickinsonPoem(title_to_use, raw_lines))

							# iii. Wipe fields
							raw_title = ""
							raw_lines = []
							temp_title = ""

							continue


					# II. Check for title line
					if GutenbergDickinsonPoem.is_title_line(clean_line):
						raw_title = clean_line
					# Else, store poem lines
					else:
						raw_lines.append(clean_line)

		return poems

	# Static variables

	filename_dict = {

		"pg12241_poems_by_emily_dickinson__third_series_by_emily_dickinson.txt": "POEMS.",
		# "pg12242_poems_by_emily_dickinson__three_series__complete_by_emily_dickinson.txt": "I. LIFE.",
		"pg2678_poems_by_emily_dickinson__series_one_by_emily_dickinson.txt": "LIFE.",
		"pg2679_poems_by_emily_dickinson__series_two_by_emily_dickinson.txt": "LIFE."
	}
	

# Main script
def main():

	# 0. Stores poem objects in memory indexed by source filename
	poems_by_file = { filename: None for filename in GutenbergDickinsonPoem.filename_dict }

	# 1. Read and store poem objects for each listed Dickinson Gutenberg file
	for filename in GutenbergDickinsonPoem.filename_dict:
		poems_by_file[filename] = GutenbergDickinsonPoem.read_poems_from_file(
			paths["gutenberg_data_path"], filename)

	# Sandbox

	for filename in poems_by_file:
		print("File {0}".format(filename))
		for poem in poems_by_file[filename]:
			print("Poem title: \"{0}\"".format(poem.title))

if "__main__" == __name__:
	main()


# Author: Jonathan Armoza
# Created: October 16, 2021
# Purpose: Class that offers several way of cleaning up a text file and
#		   producing tokens from it

# Imports

# Built-ins
from collections import Counter
import os

# Custom
from utilities import aolm_paths
from utilities.aolm_utilities import clean_string

# Setup data paths
aolm_paths.setup_paths()

# Globals


class AoLM_TextCleaner(object):

	# Constructor

	def __init__(self, p_filepath, p_stopwords_type, p_tokenization_type):

		# 0. Save parameters
		self.m_filepath = p_filepath
		self.m_stopwords_type = p_stopwords_type
		self.m_tokenization_type = p_tokenization_type

		# 0. Initialization of other fields
		self.m_stopwords = None
		self.m_stopwords_filepath = ""
		self.m_text_lines_clean = []
		self.m_text_lines_no_sw = []
		self.m_tokens = None

		# 1. Read and store the text file
		self.__read_text()

		# 2. Read in the chosen stopwords
		self.__read_stopwords()

		# 3. Tokens are counted by user of object
		self.m_token_frequencies = None

		# 4. Set up tokenization method based on tokenization type
		if "aolm" == self.m_tokenization_type:
			self.m_tokenization_method = self.__manual_process
		else:
			self.m_tokenization_method = self.__manual_process

	# Private methods

	def __manual_process(self):

		# 1. Build a collection of tokens split by whitespace and cleaned by
		# the AOLM string cleaning function
		# Cleaning does the following to each token:
		# a. Strips surround whitespace and lowercases all letters
		# b. Remove characters with diacritics and replace them with their non-diacritic version
		# c. Replace any remaining endline and tab characters with single spaces
		# d. Remove all punctuation characters
		# e. Tokenizes the line split by spaces
		# f. Cleans up non-alpha numeric unicode characters
		# g. Recreates a string with its tokens separated by a single space
		
		# A. Using string cleaning method on lines
		self.m_text_lines_clean = []
		for index in range(len(self.m_text_lines)):

			# I. Clean the original line with the above cleaning method
			clean_line = clean_string(self.m_text_lines[index])

			# II. Save the cleaned line
			self.m_text_lines_clean.append(clean_line)

		# B. Remove stop words from lines
		self.m_text_lines_no_sw = \
				self.__remove_stopwords(self.m_text_lines_clean)

		# C. Create tokens from the clean and stopword-less lines
		self.m_tokens = []
		for line in self.m_text_lines_no_sw:
			self.m_tokens.extend(line.split())

		return self.m_tokens

	def __read_stopwords(self):

		# 0. Set stopwords filepath based on the stopwords type
		self.m_stopwords_filepath = \
			AoLM_TextCleaner.s_stopword_files[self.m_stopwords_type]

		# 1. Read in stop words from given file
		with open(self.m_stopwords_filepath, "r") as stopwords_file:
			stopwords = stopwords_file.readlines()

		# 2. Clean stop words
		self.m_stopwords = [word.strip() for word in stopwords]	

	def __read_text(self):

		# 1. Open the text file for reading
		if os.path.exists(self.m_filepath):

			# A. Read in the text line by line
			with open(self.m_filepath, "r") as text_file:
				self.m_text_lines = text_file.readlines()
		else:
			raise FileNotFoundError("Cannot find file {0}".format(self.m_filepath))

	def __remove_stopwords(self, p_lines=None):

		# 0. Raw text lines default if none given
		lines = self.m_text_lines if None == p_lines else p_lines

		# 1. Produce lines without stopwords
		new_lines = []
		for line in lines:
			new_words = []
			for word in line.split():
				if word.lower() not in self.m_stopwords:
					new_words.append(word)
			new_lines.append(" ".join(new_words))

		return new_lines

	# Properties

	@property
	def clean_text(self):
		return self.m_text_lines_clean
	@property
	def clean_text_no_sw(self):
		return self.m_text_lines_no_sw
	@property
	def text(self):
		return self.m_text_lines
	@property
	def token_frequencies(self):
		if None == self.m_token_frequencies:
			self.m_token_frequencies = Counter(self.m_tokens)
		return self.m_token_frequencies

	# Public methods

	def tokenize(self):
		if None == self.m_tokens:
			self.m_tokenization_method()
		return self.m_tokens

	

	# Static fields

	# Dictionary matching stopword types to file locations

	s_stopword_files = {

		"voyant": aolm_paths.data_paths["aolm_general"]["voyant_stopwords"]
	}


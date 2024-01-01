# Author: Jonathan Armoza
# Creation date: November 2019
# Purpose: Contains generic utility functions for string and file manipulation, etc.
#          for 'The Art of Literary Modeling'

# Imports

# Standard library
import os   	   # Working directory and folder separator char
import string 	   # Punctuation
import unicodedata # Removing diacritics from characters

# Debug

debug_separator = "========================================================================"

terminal_width = 80

output_dividers = {
	
	"section": "=" * terminal_width,
	"subsection": "–" * terminal_width,
	"subsubsection": "-" * terminal_width
}

def print_debug_header(p_title, p_header_width=80, p_header_char="="):
	
	print(p_title + " " + (p_header_char * (p_header_width - len(p_title) - 1)))


# Strings

def clean_string(p_original_string, p_remove_internal_punctuation=False):

	# 1. Strip whitespace and lowercase
	new_str = p_original_string.strip().lower()

	# 2. Remove all accents
	new_str = remove_diacritics(new_str)

	# 3. Replace all \n and \t with ' '
	new_str = new_str.replace("\n", " ").replace("\t", " ")	

	# 4. Split by spaces
	new_str_parts = new_str.split()
	# a. Removing single n's - unicode error converted em-dash to n-tilda
	new_str_parts = [part for part in new_str_parts if "n" != part]

	# 5. Remove punctuation from each word
	new_str_parts = [remove_punctuation(new_str, p_remove_internal_punctuation)	\
		for new_str in new_str_parts]

	# 6. Rejoin with single spaces
	new_str = " ".join(new_str_parts)

	return new_str.strip()

def clean_word(p_word):

	# Returns a lowercase word with leading/trailing whitespace and punctuation stripped
	return p_word.lower().strip().strip(string.punctuation).strip()

# Source: https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
def remove_diacritics(p_original_string):

	new_str = []
	for char in p_original_string:
	    # Gets the base character of char, by "removing" any
	    # diacritics like accents or curls and strokes and the like.

	    desc = unicodedata.name(char)
	    cutoff = desc.find(" WITH ")
	    if cutoff != -1:
	        desc = desc[:cutoff]
	        try:
	            char = unicodedata.lookup(desc)
	        except KeyError:
	            continue  # removing "WITH ..." produced an invalid name
	    new_str.append(char)

	return "".join(new_str)

def remove_punctuation(p_original_string, p_remove_internal_punctuation=False):

	# 1. Remove punctuation from the given string

	# A. Remove all punctuation, external and internal
	if p_remove_internal_punctuation:

		new_str_parts = []

		for char in p_original_string:
			if char in string.punctuation:
				continue
			new_str_parts.append(char)
		return "".join(new_str_parts)
	# B. Remove external punctuation only
	else:

		# A. Find first alphanumeric character
		first_index = -1
		for index in range(len(p_original_string)):
			if p_original_string[index].isalnum():
				first_index = index
				break

		# B. Find last alphanumeric character
		last_index = -1
		for index in reversed(range(len(p_original_string))):
			if p_original_string[index].isalnum():
				last_index = index
				break

		return p_original_string[first_index:last_index + 1]
		# return p_original_string[first_index:last_index]

	return p_original_string


# File handling

def format_path(p_original_filepath):

	new_path = p_original_filepath.strip()
	return new_path + os.sep if os.sep != new_path[len(new_path) - 1] else new_path

def is_valid_file(p_filepath, p_tag):
	return p_filepath.endswith("." + p_tag) and os.path.isfile(p_filepath)

# Tokenization

def aolm_tokenize():
	pass

def nltk_tokenize(p_string):

	# 0. Import here so all uses of aolm_utilities do not incur nltk import load time
	import nltk

	return


# Stopwords

def remove_stopwords(p_tokens, p_stopwords_type="voyant"):

	# NOTE: It is presumed that string cleaning has been handled before this call

	# 0. Import for data paths here so not all uses of aolm_utilities incur
	# data_paths load time
	from utilities import aolm_paths
	aolm_paths.setup_paths()

	# 1. Read in stopwords from given list
	if p_stopwords_type == "voyant":
		with open(aolm_paths.data_paths["aolm_general"]["voyant_stopwords"], "r") as stopwords_file:
			stopwords = [sw.strip() for sw in stopwords_file.readlines()]
	# Other stopword list handlin here
	else:
		return []

	# 2. Remove stopwords from token list
	new_token_list = [token.lower() for token in p_tokens if token.lower() not in stopwords]

	return new_token_list


	







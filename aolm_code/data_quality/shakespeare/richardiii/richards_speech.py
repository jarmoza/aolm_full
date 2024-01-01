# Author: Jonathan Armoza
# Creation date: October 15, 2021
# Purpose: Demonstrate the different ways to count Richard's speech from the
#		   beginning of Richard III

# Imports

# Standard library
import argparse
import os

# Third party libraries
import nltk

# Custom
from data_quality.core.dq_cleaner import AoLM_TextCleaner
from utilities import aolm_paths

# Setup data paths
aolm_paths.setup_paths()

# Globals

# Filepaths
paths = {
	
	"richards_speech": "{0}input{1}richards_speech.txt".format(aolm_paths.data_paths["aolm_shakespeare"]["richardiii"], os.sep),
	"richards_speech_1s": "{0}input{1}richards_speech_1s.txt".format(aolm_paths.data_paths["aolm_shakespeare"]["richardiii"], os.sep),
}


# Script functions

def main(p_args):

	# 0. Text is selected manually for this script here
	text_filepath = paths["richards_speech_1s"]

	# 1. Show what different cleaning and tokenization methods do to the speech

	# A. Create the text cleaner object
	text_cleaner = AoLM_TextCleaner(text_filepath, p_args.stopwords_type,
		p_args.tokenization_type)

	# B. Get tokens and frequencies of the speech
	tokens = text_cleaner.tokenize()
	frequencies = text_cleaner.token_frequencies
	
	print("Richard's speech cleaned by {0} string cleaning:".format(p_args.tokenization_type))
	print("\n".join(text_cleaner.clean_text_no_sw))
	print("Word counts:\n{0}".format(frequencies))

	# C. NLTK tokenization
	with open(text_filepath, "r") as text_file:
		richard1s_lines = text_file.readlines()
	tokens = nltk.word_tokenize("\n".join(richard1s_lines))
	print("NLTK tokens: {0}".format(tokens))
	

if "__main__" == __name__:

	# 0. Create the argument parse
	parser = argparse.ArgumentParser()

	# 1. Set up valid flag arguments
	parser.add_argument("tokenization_type", default="aolm")
	parser.add_argument("stopwords_type", default="voyant")

	# 2. Get the arguments from the command line
	args = parser.parse_args()

	main(args)
# Author: Jonathan Armoza
# Created: January 4, 2022
# Purpose: Script that takes an input text file, tokenizes and counts its words,
#		   and plots the counts on a simple bar graph

# Imports

# Standard library
from collections import Counter
from collections import OrderedDict
import json
import math
import os
import sys

# Third party libraries
import nltk
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Local
from utilities import aolm_paths
from utilities.aolm_utilities import debug_separator
aolm_paths.setup_paths()

# Globals

# Main script
def main(p_args):

	# 0. Interpret script arguments
	flag = p_args[0]
	filetag = p_args[1]
	
	# 1. Read in text file

	# Filepath
	text_data = {}
	if "-f" == flag:
		with open(filetag, "r") as input_file:
			text_data[os.path.basename(filetag)] = input_file.readlines()
	# Stock files
	elif "-s" == flag:
		if "richardiii" == filetag:
			with open(aolm_paths.data_paths["aolm_shakespeare"]["richardiii"] + "input" + os.sep + "richardiii_counts.json", "r") as json_file:
				text_data = json.load(json_file)
		else:
			return False

	# 2. Clean and tokenize each text in the json file
	token_dict = {}
	for text in text_data:
		token_dict[text] = nltk.word_tokenize("\n".join(text_data[text]))

	# 3. Plot the counts of each given text
	number_cols = 2
	number_rows = math.ceil(len(text_data) / number_cols)
	i = 1
	j = 1

	# A. Create the plotly figure
	fig = make_subplots(rows=number_rows, cols=number_cols)

	# B. Create a plot for each text's word frequencies
	for text in text_data:

		# I. Create an ordered dictionary of the word frequencies
		word_frequencies = OrderedDict(Counter(token_dict[text]))

		# II. Create a new bar plot based on the text's word frequencies
		fig.add_trace(
			go.Bar(x=list(word_frequencies.keys()), y=[word_frequencies[word] for word in word_frequencies]),
			row=i, col=j
		)

		# III. Increment rows and columns indices
		j += 1
		if j > 2:
			i += 1
			j = 1
	
	# C. Show the plot
	fig.show()

if "__main__" == __name__:

	if len(sys.argv) >= 3:
		main(sys.argv[1:])


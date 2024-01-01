# Author: Jonathan Armoza
# Project: Art of Literary Modeling
# Date: August 28, 2019

# 0. Setup

# Debugging lists of texts
from collections import Counter
import sys

# glob()
import glob

# getcwd() and sep
import os

# Numpy arrays
import numpy

# Progress bar for print output
from tqdm import tqdm

# Class object for poems from Emily Dickinson Archive (https://www.edickinson.org/)
from dickinson_poem import DickinsonPoem

# Class object for labelled texts from Emily Dickinson Correspondence
# (https://rotunda.upress.virginia.edu/edc/)
from dc_edctext import EDCText

# LogisticRegression wrapper with simple functionality and utility functions
from logreg import LogReg

# Datasets
paths = {

	"correspondence": EDCText.default_tei_filepath,
	"poems": os.getcwd() + "{0}..{0}poems{0}tei{0}".format(os.sep),
	"output": os.getcwd() + os.sep
}

# Input and text processing functions
def read_texts(p_text_tuples):

	# 1. Create text objects from each of the files in the given paths
	# path key, file extension, class name
	text_object_lists = []
	for item in p_text_tuples:

		path_key = item[0]
		file_extension = item[1]
		class_name = item[2]

		print("Reading in {0}...".format(path_key))
		texts = []
		for text_filepath in tqdm(glob.glob(paths[path_key] + "*." + file_extension)):
			texts.append(class_name(text_filepath))

		text_object_lists.append(texts)

	return text_object_lists

def get_lexicon(p_lexicon_tuples):

	# 1. Create a dictionary of lexicons - lexicon_name: lexicon_create_function(text_object_list)
	lexicons = {}
	for lexical_item in p_lexicon_tuples:
		print("Determining lexicon for {0}...".format(lexical_item[0]))
		lexicons[lexical_item[0]] = lexical_item[1](lexical_item[2])

	# 2. Create a lexicon that consists of all lexicons
	lexicons["all"] = []
	for key in lexicons:
		lexicons["all"] += set(lexicons[key])
	lexicons["all"] = list(lexicons["all"])

	return lexicons

def make_bow_vectors(p_text_object_lists, p_lexicon, p_top_word_count="all"):

	# 1. Create full bag-of-words vectors for each text with the given lexicon
	print("Creating bag-of-words vectors for all texts...")
	all_texts = p_text_object_lists[0]
	for index in range(1, len(p_text_object_lists)):
		all_texts += p_text_object_lists[index]
	for text in tqdm(all_texts):
		text.create_bow_vector(p_lexicon)

	# 2. Determine frequency of words in lexicon and sort lexicon accordingly in decreasing order
	print ("Calculating frequency of words across all texts...")
	lexicon_bow_vector = all_texts[0].bow_vector
	for index in range(1, len(all_texts)):
		lexicon_bow_vector += all_texts[index].bow_vector
	lexicon_bow_map = [(p_lexicon[index], lexicon_bow_vector[index]) for index in range(len(p_lexicon))]
	lexicon_bow_map = sorted(lexicon_bow_map, key=lambda x: x[1], reverse=True)
	lexicon_words_sorted = [lexicon_bow_map[index][0] for index in range(len(lexicon_bow_map))]

	# 3. Create bag-of-words vectors for each text, considering only the top N words, if requested
	if "all" != p_top_word_count:
		print("Getting bag-of-words vectors using top {0} words for all texts...".format(p_top_word_count))
		for text in tqdm(all_texts):
			text.create_bow_vector(lexicon_words_sorted, p_top_word_count)


def main():

	# 1. Read in poems and correspondence
	text_object_lists = read_texts([("poems", "tei", DickinsonPoem),
							 		("correspondence", "xml", EDCText)])
	poems = text_object_lists[0]
	correspondence = text_object_lists[1]

	# A. Create a dictionary of correspondence based on editor assigned type
	text_type_map = {}
	for text in correspondence:
		text_type = text.editor_assigned_type
		if text_type not in text_type_map:
			text_type_map[text_type] = []
		text_type_map[text_type].append(text)	

	# 2. Create lexicon from poems and correspondence
	lexicons = get_lexicon([("poems", DickinsonPoem.create_lexicon, poems),
							("correspondence", EDCText.create_lexicon, correspondence)])

	# 3. Make bag-of-words frequency vectors for all texts (top N only)
	make_bow_vectors([poems, correspondence], lexicons["all"], 100)

	# 4. Create collection of texts for training/validation and holdouts for later prediction
	# 'verse-letter': 34
	# 'verse': 26
	# 'letter': 6
	# 'letter-with-enclosed-verse': 4
	# 'letter-with-embedded-verse': 4
	print("Separating texts for training/validation and holdouts for prediction...")
	all_texts, holdouts = LogReg.split_data_and_holdouts_half(poems)
	for text_type in text_type_map:
		more_texts, more_holdouts = LogReg.split_data_and_holdouts_half(text_type_map[text_type])
		all_texts.extend(more_texts)
		holdouts.extend(more_holdouts)

	# 5. Create an object for logistic regression modeling with the given text and holdout data sets
	all_texts_data = numpy.array([text.bow_vector for text in all_texts])
	all_texts_labels = numpy.array([text.editor_assigned_type for text in all_texts])
	holdouts_data = numpy.array([text.bow_vector for text in holdouts])
	holdouts_labels = [text.editor_assigned_type for text in holdouts]
	holdouts_titles = [text.title for text in holdouts]	
	logistic_regression = LogReg(all_texts_data, all_texts_labels,
								 holdouts_data, holdouts_labels, holdouts_titles,
								 p_verbose=True)

	# 6. Create training and validation data sets
	logistic_regression.split_training_and_validation(True)

	# 6. Train logistic regression model based on train/validation split
	logistic_regression.fit(True)

	# 7. Determine model validation score
	validation_score = logistic_regression.validation_score(True)

	# 8. Make predictions on held out text set
	holdout_prediction_scores = logistic_regression.holdout_score(True)

if "__main__" == __name__:
	main()
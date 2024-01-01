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

# Classifier for differentiating between Dickinson text types
from sklearn.linear_model import LogisticRegression

# Splitting up training and test data sets
from sklearn.model_selection import train_test_split

# Progress bar for print output
from tqdm import tqdm

# Class object for poems from Emily Dickinson Archive (https://www.edickinson.org/)
from dickinson_poem import DickinsonPoem

# Class object for labelled texts from Emily Dickinson Correspondence
# (https://rotunda.upress.virginia.edu/edc/)
from dc_edctext import EDCText

# LogisticRegression wrapper with simple functionality and utility functions
import logreg

# Datasets
paths = {

	"correspondence": EDCText.default_tei_filepath,
	"poems": os.getcwd() + "{0}..{0}poems{0}tei{0}".format(os.sep),
	"output": os.getcwd() + os.sep
}

# Functions
def read_texts(p_text_tuples):

	text_object_lists = []
	for item in p_text_tuples:

		print("Reading in {0}...".format(item[0]))
		texts = []
		for text_filepath in tqdm(glob.glob(paths[item[0]] + "*." + item[1])):
			texts.append(item[2](text_filepath))

		text_object_lists.append(texts)

	# print("Reading in poems...")
	# poems = []
	# for poem_filepath in tqdm(glob.glob(paths["poems"] + "*.tei")):
	# 	poems.append(DickinsonPoem(poem_filepath))

	# print("Reading in correspondence...")
	# correspondence = []
	# for correspondence_filepath in tqdm(glob.glob(paths["correspondence"] + "*.xml")):
	# 	correspondence.append(EDCText(correspondence_filepath))

	# return poems, correspondence

	return text_object_lists

def get_lexicon(p_lexicon_tuples):

	# 1. Create a dictionary of lexicons - lexicon_name: lexicon_create_function(text_object_list)
	lexicons = { }
	for lexical_item in p_lexicon_tuples:
		print("Determining lexicon for {0)...".format(lexical_item[0]))
		lexicons[lexical_item[0]] = lexical_item[1](lexical_item[2])

	# 2. Create a lexicon that consists of all lexicons
	lexicons["all"] = []
	for key in lexicons:
		lexicons["all"] += set(lexicons[key])
	lexicons["all"] = list(lexicons["all"])

	# lexicons = { 
	# 	"poems": DickinsonPoem.create_lexicon(poems),
	# 	"correspondence": EDCText.create_lexicon(correspondence)
	# }
	# lexicons["all"] = list(set(lexicons["poems"] + lexicons["correspondence"]))

	return lexicons

def make_bow_vectors(p_text_object_lists, p_lexicon, p_top_word_count="all"):

	# 1. Create full bag-of-words vectors for each text with the given lexicon
	print("Creating bag-of-words vectors for all texts...")
	all_texts = p_text_object_lists[0]:
	for index in range(1, len(p_text_object_lists)):
		all_texts += p_text_object_lists[index]
	for text in tqdm(all_texts):
		text.create_bow_vector(p_lexicon)

	# 2. Determine frequency of words in lexicon and sort lexicon accordingly in decreasing order
	print ("Calculating frequency of words across all texts...")
	lexicon_bow_vector = all_texts[0].bow_vector
	for index in range(1, len(all_texts)):
		lexicon_bow_vector += all_texts[index].bow_vector
	lexicon_bow_map = [(lexicons["all"][index], lexicon_bow_vector[index]) for index in range(len(lexicons["all"]))]
	lexicon_bow_map = sorted(lexicon_bow_map, key=lambda x: x[1], reverse=True)
	lexicon_words_sorted = [lexicon_bow_map[index][0] for index in range(len(lexicon_bow_map))]

	# 3. Create bag-of-words vectors for each text, considering only the top N words, if requested
	if "all" != p_top_word_count:
		print("Getting bag-of-words vectors using top {0} words for all texts...".format(p_top_word_count))
		for text in tqdm(all_texts):
			text.create_bow_vector(lexicon_words_sorted, p_top_word_count)

	# all_texts = poems + correspondence
	# for text in tqdm(all_texts):
	# 	text.create_bow_vector(lexicons["all"])
	# print ("Calculating frequency of words across all texts...")
	# lexicon_bow_vector = all_texts[0].bow_vector
	# for index in range(1, len(all_texts)):
	# 	lexicon_bow_vector += all_texts[index].bow_vector
	# lexicon_bow_map = [(lexicons["all"][index], lexicon_bow_vector[index]) for index in range(len(lexicons["all"]))]
	# lexicon_bow_map = sorted(lexicon_bow_map, key=lambda x: x[1], reverse=True)
	# lexicon_words_sorted = [lexicon_bow_map[index][0] for index in range(len(lexicon_bow_map))]

	# # 4. Create bag-of-words vectors for each text
	# top_word_count = 100
	# print("Getting bag-of-words vectors using top {0} words for all texts...".format(top_word_count))
	# for text in tqdm(all_texts):
	# 	text.create_bow_vector(lexicon_words_sorted, top_word_count)


def main():

	# 1. Read in poems and correspondence
	text_object_lists = read_texts([("poems", "tei", DickinsonPoem),
							 		("correspondence", "xml", EDCText)])
	poems = text_object_lists[0]
	correspondence = text_object_lists[1]

	# A. Create a dictionary of correspondence based on editor assigned type
	corr_type_map = {}
	for text in correspondence:
		text_type = text.editor_assigned_type
		if text_type not in corr_type_map:
			corr_type_map[text_type] = []
		corr_type_map[text_type].append(text)	

	# 2. Create lexicon from poems and correspondence
	lexicons = get_lexicon([("poems", DickinsonPoem.create_lexicon, poems),
							("correspondence", EDCText.create_lexicon, correspondence)])

	# 3. Make bag-of-words frequency vectors for all texts (top N only)
	make_bow_vectors([poems, correspondence], lexicons["all"], 100)

	# 4. Create collection of texts for training/test and holdouts for later prediction

	# 'verse-letter': 34
	# 'verse': 26
	# 'letter': 6
	# 'letter-with-enclosed-verse': 4
	# 'letter-with-embedded-verse': 4
	print("Separating texts for training/test and holdouts for prediction...")
	all_texts, holdouts = LogReg.split_data_and_holdouts_half(poems)
	for text_type in corr_type_map:
		more_texts, more_holdouts = LogReg.split_data_and_holdouts_half(corr_type_map[text_type])
		all_texts.extend(more_texts)
		holdouts.extend(more_holdouts)

	# all_texts = poems[0:int(len(poems) / 2.0)]
	# all_texts += corr_type_map["verse-letter"][0:int(len(corr_type_map["verse-letter"]) / 2.0)]
	# all_texts += corr_type_map["letter"][0:int(len(corr_type_map["letter"]) / 2.0)]
	# all_texts += corr_type_map["letter-with-enclosed-verse"][0:int(len(corr_type_map["letter-with-enclosed-verse"]) / 2.0)]
	# all_texts += corr_type_map["letter-with-embedded-verse"][0:int(len(corr_type_map["letter-with-embedded-verse"]) / 2.0)]

	# holdouts = poems[int(len(poems) / 2.0) + 1:]
	# holdouts += corr_type_map["verse"]
	# holdouts += corr_type_map["verse-letter"][int(len(corr_type_map["verse-letter"]) / 2.0) + 1:]
	# holdouts += corr_type_map["letter"][int(len(corr_type_map["letter"]) / 2.0) + 1:]
	# holdouts += corr_type_map["letter-with-enclosed-verse"][int(len(corr_type_map["letter-with-enclosed-verse"]) / 2.0) + 1:]
	# holdouts += corr_type_map["letter-with-embedded-verse"][int(len(corr_type_map["letter-with-embedded-verse"]) / 2.0) + 1:]

	# A. Save holdout counts by text type
	holdout_labels = [text.editor_assigned_type for text in holdouts]
	holdout_counts = Counter(holdout_labels)
	# holdout_counts = { 
		
	# 	"verse": int(len(poems) / 2.0) + len(corr_type_map["verse"]),
	# 	"verse-letter": int(len(corr_type_map["verse-letter"]) / 2.0),
	# 	"letter": int(len(corr_type_map["letter"]) / 2.0), 
	# 	"letter-with-enclosed-verse": int(len(corr_type_map["letter-with-enclosed-verse"]) / 2.0),
	# 	"letter-with-embedded-verse": int(len(corr_type_map["letter-with-embedded-verse"]) / 2.0)
	# }

# 5. Create training and validation data
print("Splitting up training and validation data sets...")
text_data = numpy.array([text.bow_vector for text in all_texts])
text_labels = numpy.array([text.editor_assigned_type for text in all_texts])
training_data, validation_data, training_labels, validation_labels = train_test_split(text_data, text_labels, test_size=0.25, random_state=0)

# 6. Train logistic regression model based on train/test split
print("Training model...")
logistic_regression = LogisticRegression(solver="lbfgs", multi_class="auto", max_iter=500)
logistic_regression.fit(training_data, training_labels)

# 7. Determine model validation score
score = logistic_regression.score(validation_data, validation_labels)
print("Validation score: {0}".format(score))

# 8. Make predictions on held out poem set
holdout_prediction_scores = { text_type: 0 for text_type in corr_type_map }
for text in holdouts:
	prediction = logistic_regression.predict([text.bow_vector])
	text_type = text.editor_assigned_type
	# print("{0} - Label: {1} Prediction: {2}".format(text.title, text_type, prediction))
	if prediction == text_type:
		holdout_prediction_scores[text_type] += 1
for text_type in holdout_prediction_scores:
	holdout_prediction_scores[text_type] /= float(holdout_counts[text_type])
	print("{0} Holdout prediction accuracy: {1}%%".format(text_type,
		  holdout_prediction_scores[text_type] * 100))
# Author: Jonathan Armoza
# Project: Art of Literary Modeling
# Date: July 23, 2019

# Plan
# 1. Check out attributes of the 4 different editor-assigned correspondence types
# 2. Gather bag of words stat and other general stats as features for vectorizing the correspondences
# 3. Train and evaluate an SVM using the editor-assigned types as classes

import glob
import os
import random
from collections import Counter

from sklearn import svm

from dc_edctext import EDCText

hyper_parameters = {
	
	"training_percentage": 0.65
}


def main():

	# 1. Collection of TEI xml files as EDCText objects
	edc_instances = {}
	for tei_filepath in glob.glob(EDCText.default_tei_filepath + "*.xml"):
		base_filename = os.path.basename(tei_filepath)
		edc_instances[base_filename] = EDCText(tei_filepath)

	# 2. Form vectors for training and test
	edc_data = {

		"training": { "sources": [], "vectors": [] },
		"test": { "sources": [], "vectors": [] },

		"targets": [],
	}

	# a. Randomize keys for training and test sets
	edc_keys = list(edc_instances.keys())
	random.shuffle(edc_keys)
	for index in range(len(edc_keys)):
		if index < len(edc_keys) * hyper_parameters["training_percentage"]:
			edc_data["training"]["sources"].append(edc_keys[index])
			edc_data["targets"].append(edc_instances[edc_keys[index]].editor_assigned_type)
		else:
			edc_data["test"]["sources"].append(edc_keys[index])

	# b. Get lexicon for the texts
	edc_lexicon = EDCText.create_lexicon(edc_instances)

	# c. Create regularized bag of words vectors for each text, given the lexicon
	for source_name in edc_instances:
		edc_instances[source_name].bow_vector = edc_lexicon

	# d. Create the vectors for training and test
	for source_list in [edc_data["training"], edc_data["test"]]:
		for source_name in source_list["sources"]:
		
			line_count = edc_instances[source_name].line_count
			word_count = len(edc_instances[source_name].body_words)
			bow_vector = edc_instances[source_name].bow_vector

			sample = [line_count, word_count]
			sample.extend(bow_vector)

			source_list["vectors"].append(sample)


	# 3. Create and train the model using the training set and target editor assigned types (labels)
	classifier = svm.SVC(gamma=0.001, C=100.0)
	classifier.fit(edc_data["training"]["vectors"], edc_data["targets"])

	# 4. Predict the editor assigned types of the test set
	results = classifier.predict(edc_data["test"]["vectors"])

	# 5. Compute the loss (% incorrectly predicted labels in the test set)
	test_size = len(edc_data["test"]["sources"])
	error_count = 0
	for index in range(test_size):
		# print("Predicted type: {0} | Assigned type: {1}".format(results[index],
		# 	edc_instances[edc_data["test"]["sources"][index]].editor_assigned_type))
		if results[index] != edc_instances[edc_data["test"]["sources"][index]].editor_assigned_type:
			error_count += 1
	print("Accuracy: {0:0.2f}%".format(100 * (test_size - error_count) / test_size))


if "__main__" == __name__:
	main()
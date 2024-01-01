# Author: Jonathan Armoza
# Project: Art of Literary Modeling
# Date: June 4, 2019

# Plan
# 1. Look at history tag in each of the TEI files
# 2. gather provenance - notBefore/notAfter attributes
# 3. Regress these poems date ranges by line counts
# 4. Learn the line (linear regression)

# Thought - create a BeautifulSoup meta class for easily working with the TEI files
# - Have to learn how to parse these XML files (specifically the content)

import glob
import math
import os
import random
import sys

import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

from dc_edctext import EDCText


def print_dict(p_dict, p_separator="=", p_separator_length=25):

	for key in p_dict:
		print("{0}:\n{1}".format(key, p_dict[key]))
		print(p_separator * p_separator_length)

def print_exists(p_dict, p_key, p_not_exists=False):

	if p_key in p_dict:
		print(p_dict[p_key])
	elif p_not_exists:
		print("{0} not in given dict".format(p_key))

def get_index_based_2d_array(p_1d_list):

	two_dimensional_list = []
	for index in range(len(p_1d_list)):
		two_dimensional_list.append([index, p_1d_list[index]])
	return two_dimensional_list


def linear_regress(p_x_values, p_y_values):

	# Split the data into training/testing sets
	x_values_training = p_x_values[:int(math.floor(len(p_x_values) / 2.0) - 1)]
	x_values_training_2d = get_index_based_2d_array(x_values_training)
	x_values_test = p_x_values[int(math.floor(len(p_x_values) / 2.0)):]
	x_values_test_2d = get_index_based_2d_array(x_values_test)

	# Split the targets into training/testing sets
	y_values_training = p_y_values[:int(math.floor(len(p_y_values) / 2.0) - 1)]
	y_values_training_2d = get_index_based_2d_array(y_values_training)
	y_values_test = p_y_values[int(math.floor(len(p_y_values) / 2.0)):]
	y_values_test_2d = get_index_based_2d_array(y_values_test)

	# Create linear regression object
	regr = linear_model.LinearRegression()

	# Train the model using the training sets
	regr.fit(x_values_training_2d, y_values_training_2d)

	# Make predictions using the testing set
	y_values_predictions = regr.predict(x_values_test_2d)

	# The coefficients
	print("Coefficients: \n", regr.coef_)
	# The mean squared error
	print("Mean squared error: {0:.2f}".format(mean_squared_error(y_values_test_2d, y_values_predictions)))
	# Explained variance score: 1 is perfect prediction
	print("Variance score: {0:.2f}".format(r2_score(y_values_test_2d, y_values_predictions)))

	# Plot outputs
	plt.scatter(x_values_test_2d, y_values_test_2d,  color="black")
	plt.plot(x_values_test_2d, y_values_predictions, color="blue", linewidth=3)

	plt.xticks(())
	plt.yticks(())

	plt.show()

def main():

	search_tag = "history"
	search_sub_tag = "origin"
	search_attributes = ["notbefore", "notafter"]

	# 1. Get history tag in each of the TEI files
	edc_instances = {}
	history_tags = {}
	for tei_filepath in glob.glob(EDCText.default_tei_filepath + "*.xml"):
		base_filename = os.path.basename(tei_filepath)
		edc_instances[base_filename] = EDCText(tei_filepath)
		history_tags[base_filename] = edc_instances[base_filename].first_tag(search_tag)

	# 2. Get 'start' and 'end' - notbefore/notafter dates
	for key in history_tags:
		origin_tag = history_tags[key].find(search_sub_tag)
		edc_instances[key].start_date = origin_tag.attrs[search_attributes[0]] if search_attributes[0] in origin_tag.attrs else EDCText.default_na
		edc_instances[key].end_date = origin_tag.attrs[search_attributes[1]] if search_attributes[1] in origin_tag.attrs else EDCText.default_na
		
		# print(key + ":")
		# print_exists(origin_tag.attrs, search_attributes[0], p_not_exists=True)
		# print_exists(origin_tag.attrs, search_attributes[1], p_not_exists=True)
		# print("=" * 25)

	# 3. Determine date range of all texts
	all_dates = []
	for key in edc_instances:
		all_dates.append(edc_instances[key].start_date)
		all_dates.append(edc_instances[key].end_date)
	all_dates.sort()

	index = 0
	while EDCText.default_na == all_dates[index]:
		index += 1
	# earliest_date_continuous = EDCText.datetime_continuous(all_dates[index])
	earliest_date_continuous = EDCText.datetime_continuous(EDCText.format_date("1840"))

	index = len(all_dates) - 1
	while EDCText.default_na == all_dates[index]:
		index -= 1
	# latest_date_continuous = EDCText.datetime_continuous(all_dates[index])
	latest_date_continuous = EDCText.datetime_continuous(EDCText.format_date("1920"))

	start_dates = []
	for key in edc_instances:
		start_dates.append((edc_instances[key].start_date, edc_instances[key]))
	start_dates = sorted(start_dates, key=lambda x:x[0], reverse=False)

	# print(start_dates[len(start_dates) - 1][1].filepath)
	# for d in start_dates:
	# 	print("[{0} -> {1}]".format(d[0], d[1].end_date))

	# 4. Get line counts
	line_counts = {}
	for key in edc_instances:
		line_counts[key] = edc_instances[key].line_count
	# print_dict(line_counts)

	# Get date range averages (for easy regression purposes)
	average_dates = []
	line_counts_list = []

	for key in edc_instances:
		sdc = edc_instances[key].start_date_continuous()
		edc = edc_instances[key].end_date_continuous()
		average_dates.append((sdc + edc) / 2.0)
		line_counts_list.append(edc_instances[key].line_count)

	linear_regress(average_dates, line_counts_list)

	if True:
		return


	# 5. Plot date ranges by line count
	date_continuous_delta = latest_date_continuous - earliest_date_continuous
	for key in edc_instances:
		print("============\n{0}\n{1} - {2}, lines: {3}".format(key,
			(edc_instances[key].start_date_continuous() - earliest_date_continuous) / date_continuous_delta,
			(edc_instances[key].end_date_continuous() - earliest_date_continuous)/ date_continuous_delta,
			edc_instances[key].line_count))
		color_tuple = (random.randint(0,255) / 255.0,
			random.randint(0,255) / 255.0,
			random.randint(0,255) / 255.0)
		plt.axhline(xmin=(edc_instances[key].start_date_continuous() - earliest_date_continuous)/ date_continuous_delta,
					xmax=(edc_instances[key].end_date_continuous() - earliest_date_continuous)/ date_continuous_delta,
					y=edc_instances[key].line_count, linestyle='-', color=color_tuple, linewidth=5)
	plt.show()
 

if "__main__" == __name__:
	main()
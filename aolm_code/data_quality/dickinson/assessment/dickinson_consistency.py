# Author: Jonathan Armoza
# Creation date: November 18, 2019
# Last Updated: September 11, 2020
# Purpose: The "consistency" data quality metric for Emily Dickinson works


# Imports

# Built-in
import csv				# Dictionary reader
import glob				# File searching
from math import ceil	# Number ranges for graphing
import operator			# Finding max value in dictionary
import os				# Working directory and folder separator char
import sys				# Terminal arguments

# Third party
import numpy as np
from tqdm import tqdm

# Local
import aolm_string_utilities as asu						# String formatting
from dickinson_poem import DickinsonPoem				# Text objects
from dickinson_collection import DickinsonCollection	# Text collection

# Debug messaging
# import my_logging
# logger = my_logging.get_logger(__name__)
# debug = logger.debug
# # logger.disable(logging.DEBUG)	# Comment out to enable debug messages

import my_logging
from my_logging import logging
from my_logging import tqdm
debug = logging.debug
# logging.disable(logging.DEBUG) # Comment out to enable debug messages

# Disable matplotlib debug messages
# logging.getLogger("matplotlib").setLevel(logging.WARNING)


# Globals

corpora_paths = { "root": "..{0}..{0}..{0}dq_assessment{0}data{0}dickinson{0}".format(os.sep) }
corpora_paths["all"] = corpora_paths["root"] + "all" + os.sep
corpora_paths["curated"] = corpora_paths["root"] + "curated" + os.sep
corpora_paths["metadata"] = corpora_paths["root"] + "dickinson_poem_list.csv"

# Corpora split up by Dickinson collection (arranged in date order here)
corpora_paths["todd_higginson_1890"] 	 = corpora_paths["curated"] + "todd_higginson_1890" + os.sep
corpora_paths["higginson_todd_2nd_1891"] = corpora_paths["curated"] + "higginson_todd_2nd_1891" + os.sep
corpora_paths["todd_letters_1894"] 		 = corpora_paths["curated"] + "todd_letters_1894" + os.sep
corpora_paths["todd_3rd_1896"] 			 = corpora_paths["curated"] + "todd_3rd_1896" + os.sep
corpora_paths["bianchi_1914"] 			 = corpora_paths["curated"] + "bianchi_1914" + os.sep
corpora_paths["johnson_1955"] 			 = corpora_paths["curated"] + "johnson_1955" + os.sep
corpora_paths["franklin_1998"] 			 = corpora_paths["curated"] + "franklin_1998" + os.sep

# Expected counts
corpora_count_expectations = {
	
	"todd_higginson_1890": 115, # 26 + 18 + 31 + 40
	"higginson_todd_2nd_1891": 166, # 57 + 16 + 51 + 42
	"todd_letters_1894": 102,
	"todd_3rd_1896": 165, # 55 + 22 + 29 + 59
	"bianchi_1914": 142,
	"johnson_1955": 1775,
	"franklin_1998": 1789
}

paths = {

	"archive_corpus": "..{0}data{0}dickinson{0}curated{0}franklin_1998{0}".format(os.sep),
	"distributions": os.getcwd() + os.sep + ("..{0}".format(os.sep) * 5) + \
					"datasets{0}metadata{0}".format(os.sep) + \
					"dickinson_franklin_poem_yeardistribution.csv",
	"dictionary": "{0}{1}..{1}data{1}general{1}words_dictionary.json".format(os.getcwd(), os.sep)
}


# Retrieves Wikipedia table of Emily Dickinson poems and metadata
# and returns a dict that matches the table's manuscript ID of a work with its title
def get_master_list(p_known_non_ids):

	# 0. Metadata file columns
	# First Line (often used as title),F/S[2],1st,1stS.P,Collect,J#[3],Fr#[4],Franklin_fullid
	title_column = "First Line (often used as title)"
	franklin_id_column = "Fr#[4]"

	# 1. Create dictionary that matches ID with title
	debug("Reading poem metadata master list....")
	master_list = {}
	with open(DickinsonCollection.metadata, "r", encoding="ISO-8859-1") as metadata_file:
		reader = csv.DictReader(metadata_file)
		for row in reader:
			if row[franklin_id_column] in p_known_non_ids:
				master_list[row[franklin_id_column]] = row[title_column]
			else:
				master_list["F" + row[franklin_id_column]] = row[title_column]

	return master_list



class AOLM_DQ_Dickinson_Consistency(object):

	def __init__(self, p_texts_path, p_corpus_name, p_file_extension="tei", p_text_collection=None):

		# 1. Create a collection object of Dickinson texts
		self.m_texts = DickinsonCollection(p_texts_path, p_corpus_name, p_file_extension, p_text_collection)

		# 2. Consistency values are stored here
		self.m_consistency = {}

		# 3. Read distributions by year
		self.read_distribution_by_year(paths["distributions"])		

		# 4. Match, mismatch, and missing IDs list for comparison between Wiki poem list and
		# digital corpus from Emily Dickinson Archive
		self.m_matches = None
		self.m_mismatches = None
		self.m_missing_ids = None

	# Properties

	@property
	def collection(self):
		return self.m_texts
	@property
	def distributions_by_year(self):
		return self.m_distributions_by_year
	@distributions_by_year.setter
	def distributions_by_year(self, p_distributions):
		self.m_distributions_by_year = p_distributions		
	@property
	def matches(self):
		return self.m_matches
	@property
	def mismatches(self):
		return self.m_mismatches
	@property
	def missing(self):
		return self.m_missing
	@property
	def matches_mismatches_missing(self):
		return self.m_matches, self.m_mismatches, self.m_missing_ids
	@property
	def text_count(self):
		return len(self.m_texts)


	def compare(self, p_expected_count, p_master_title_list, p_match_threshold=0.75):

		# NOTE: All messaging here is of primary functionality and not for debugging purposes

		# 0. Output header
		print("Making 'consistency' data quality comparisons....")
		print("==================================")
		print(self.m_texts.corpus_name)		

		# 1. Compare raw text vs expected count
		self.compare_text_count(p_expected_count)

		# 2. Compare text titles to master list of titles
		self.compare_title_match(p_master_title_list, p_expected_count, p_match_threshold)

		# 3. Get integrity of manuscript ID matches between Dickinson Archive and the Franklin distribution by year table
		self.compare_dist_manuscript_ids_to_edarchive_ids(p_expected_match_count)		

		# 4. Compare text bodies (TO BE IMPLEMENTED?)

		print("==================================")

	def dq_metric(self, p_metric_title):

		return self.m_consistency[p_metric_title]

	def find_matches_mismatches_missing(self, p_master_title_list, p_match_threshold):

		# 0. Matched titles, mismatched titles, and IDs missing from corpus on disk
		matches = {}
		mismatches = {}
		missing_ids = []

		# 1. Compare each text on disk with the master list
		for master_id in p_master_title_list:

			# a. Retrieve nonnumeric version of this manuscript ID
			# If found, it will be the first nonnumeric ID found
			# Alternate manuscripts may be examined later.
			compared_id = AOLM_DQ_Dickinson_Consistency.check_dict_for_numeric_id(
				list(self.m_texts.m_id_dict.keys()), master_id[1:])

			# print("Master ID: {0} Compared ID: {1}".format(master_id, compared_id))
						
			# b. If a text on disk has this manuscript ID
			if None != compared_id:

				# print("Match or mismatch")

				# i. Get 'clean' title of text on disk
				compared_title = asu.clean_string(self.m_texts[compared_id].title)

				# ii. Get 'clean' title of text master list
				master_title = asu.clean_string(p_master_title_list[master_id])

				# iii. Check that titles match at least above the requested threshold
				# Save matches and mismatches
				if DickinsonPoem.percent_line_match(compared_title, master_title) >= p_match_threshold:
					matches[master_id] = (compared_title, master_title)
				else:
					mismatches[master_id] = (compared_title, master_title)
			# Else, an ID on the master list cannot be found on disk
			else:
				# print("Missing")
				missing_ids.append(master_id)

		# 2. Look for alternate manuscripts for mismatches
		debug("Attempting to resolve some of {0} mismatches....".format(len(mismatches)))
		reconciled_mismatches = []
		for mismatch_id in tqdm(mismatches):

			# a. Gather possible texts for mismatch resolution
			possible_texts = []
			for text in self.m_texts.list:

				# Look for numeric ID - all mismatch IDs will be strictly numeric
				# debug("{0} {1}".format(mismatch_id, text.numeric_manuscript_id))
				if mismatch_id[1:] == text.numeric_manuscript_id:
					possible_texts.append(text.manuscript_id)

			# Continue if no possible texts or just one text found
			# This is considered an irreconcilable mismatch
			if len(possible_texts) <= 1:
				continue

			debug("Found {0} texts to look at for mismatch id {1}".format(len(possible_texts), mismatch_id))

			# b. Compare titles of possible texts with the title on the master list
			comparison_results = {}
			for possible_id in possible_texts:

				master_title = p_master_title_list[mismatch_id]
				compared_title = self.m_texts[possible_id].title
				comparison_results[possible_id] = DickinsonPoem.percent_line_match(compared_title, master_title)

			# c. Save all texts match above requested threshold
			texts_above_threshhold = {id: comparison_results[id] for id in comparison_results if comparison_results[id] >= p_match_threshold}

			# If none of the title alternates meet the match threshold
			# This is considered an irreconcilable mismatch
			if 0 == len(texts_above_threshhold):
				continue

			# d. Find the text with the highest % title match
			best_match_id = max(texts_above_threshhold.items(), key=operator.itemgetter(1))[0]

			# e. Add this pairing into the match list
			matches[self.m_texts[best_match_id].numeric_manuscript_id] = \
				(self.m_texts[best_match_id].title, p_master_title_list[mismatch_id])

			# f. Queue the removal of this ID from the mismatch list
			reconciled_mismatches.append(mismatch_id)

		# 3. Clear mismatches from mismatch dictionary
		for mismatch_id in reconciled_mismatches:
			mismatches.pop(mismatch_id)

		# 4. Save matched, mismatched, and missing manuscript IDs
		self.m_matches = matches
		self.m_mismatches = mismatches
		self.m_missing_ids = missing_ids

	# Returns a dictionary reflecting R.W. Franklin's listed poem distribution by year
	def read_distribution_by_year(self, p_filepath):

		# 0. Dictionary storing poem distributions by year
		self.m_distributions_by_year = { "ordered_years": [], "years": {} }

		# 1. Read in distribution year, manuscript IDs, manuscript count
		with open(p_filepath, "r") as csv_file:

			# a. Read in each distribution by year(s)
			reader = csv.DictReader(csv_file)
			for row in reader:

				# i. Save an ordered list of years
				self.m_distributions_by_year["ordered_years"].append(row["Year"])

				# ii. Each year maps to a range of manuscript IDs and a count of manuscripts
				self.m_distributions_by_year["years"][row["Year"]] = {}
				if "-" in row["Numbers"]:
					self.m_distributions_by_year["years"][row["Year"]]["ids"] = [int(id) for id in row["Numbers"].split("-")]
				else:
					self.m_distributions_by_year["years"][row["Year"]]["ids"] = [int(row["Numbers"]), int(row["Numbers"])]
				self.m_distributions_by_year["years"][row["Year"]]["count"] = int(row["Total"])

			# Ensure years are sorted
			self.m_distributions_by_year["ordered_years"].sort()		

	# Data quality metrics

	# Determines integrity between distribution table IDs and Emily Dickinson Archive IDs
	def compare_dist_manuscript_ids_to_edarchive_ids(self, p_expected_match_count):

		# 1. Enumerate manuscript IDs from Franklin's distribution by year table
		distribution_ids = []
		for year in self.m_distributions_by_year["years"]:
			distribution_ids.extend(range(self.m_distributions_by_year["years"][year]["ids"][0],
								  	self.m_distributions_by_year["years"][year]["ids"][1]))

		# 2. Enumerate manuscript IDs from Emily Dickinson Archive's TEI files
		archive_ids = [int(text.numeric_manuscript_id) for text in self.m_texts.list]

		# 3. Compare the two ID lists
		actual_match_count = 0
		debug("Archive ID count: {0}\nDistribution ID count: {1}".format(len(self.m_archive_matches.keys()), len(distribution_ids)))
		arch_dist_matches = []
		for a_id in self.m_archive_matches.keys():
			for d_id in distribution_ids:

				a_numeric_id = DickinsonPoem.get_numeric_id(a_id)
				if len(a_numeric_id):
					a_numeric_id = int(a_numeric_id)
				else:
					debug("Zero length archive match")
				if a_numeric_id == d_id:
					actual_match_count += 1
					arch_dist_matches.append(a_numeric_id)
					break

		# 4. Find the differences between the two lists
		arch_set = set([int(DickinsonPoem.get_numeric_id(a_id)) for a_id in self.m_archive_matches.keys()])
		dist_set = set(distribution_ids)
		debug("IN ARCH BUT NOT DIST:")
		debug(arch_set - dist_set)
		debug(debug_separator)
		debug("IN DIST BUT NOT ARCH:")
		debug(dist_set - arch_set)

		sym_diff_ids = arch_set.symmetric_difference(dist_set)
		# all_ids = arch_set.union(dist_set)
		# intersect_ids = arch_set.intersection(dist_set)
		# diff_ids = all_ids - intersection
		debug("SYMMETRIC DIFFERENCE")
		debug(sym_diff_ids)


		# 5. Output actual vs. expected ID match
		debug("{0}% match ({1}/{2}) mansuscript IDs match".format(actual_match_count/float(p_expected_match_count),
			  actual_match_count, p_expected_match_count))

		# 6. Save integrity data quality metric for manuscript ID match count
		# between Dickinson Archive and Franklin distribution table
		self.m_integrity["manuscript_id_match"] = \
			actual_match_count/float(p_expected_match_count)	

	def compare_text_count(self, p_expected_count):

		# NOTE: All messaging here is of primary functionality and not for debugging purposes

		# 1. Calculate raw text vs expected count
		self.m_consistency["text_count"] = (self.text_count - p_expected_count) / self.text_count
		print("==================================")
		print("Actual count: {0}".format(len(self.m_texts)))
		print("Expected count: {0}".format(p_expected_count))
		print("Discrepancy: {0:.2f}%".format(100 * self.m_consistency["text_count"]))
		print("==================================")

	def compare_title_match(self, p_master_title_list, p_expected_count, p_match_threshold):

		# 1. Get matched titles, mismatched titles, and IDs missing from corpus on disk
		self.find_matches_mismatches_missing(p_master_title_list, p_match_threshold)
		matches, mismatches, missing_ids = self.matches_mismatches_missing
					
		# 2. Save the data quality metrics
		print("Expected count: {0}".format(p_expected_count))
		print("Length matches: {0}".format(len(matches)))
		print("Text count: {0}".format(self.text_count))
		self.m_consistency["title_match"] = (p_expected_count - len(matches)) / self.text_count
		self.m_consistency["num_titles_matching"] = len(matches)
		self.m_consistency["num_titles_mismatching"] = len(mismatches)
		self.m_consistency["num_titles_missing"] = len(missing_ids)

		# 3. Debug messaging
		print("==================================")
		print("Titles matching: {0}".format(len(matches)))
		print("Match threshold: {0}".format(p_match_threshold))
		print("Discrepancy: {0:.2f}%".format(100 * self.m_consistency["title_match"]))
		print("==================================")
		print("Mismatches:")
		for mm in mismatches:
			print("{0}: {1}".format(mm, mismatches[mm]))
		print("==================================")
		print("Missing IDs:")
		for missing_id in missing_ids:
			print(missing_id)

	# Static fields and methods

	@staticmethod
	def check_dict_for_numeric_id(p_ids, p_numeric_id):

		# print("Passed in ID: {0}".format(p_numeric_id))
		# print("p_ids: {0}".format(p_ids))

		# Returns the nonnumeric ID if found in the ID dictionary
		for nonnumeric_id in p_ids:
			# debug("check_dict_for_numeric_id: {0},{1}".format(DickinsonPoem.get_numeric_id(nonnumeric_id), p_numeric_id))
			if DickinsonPoem.get_numeric_id(nonnumeric_id) == p_numeric_id:
				return nonnumeric_id

		# Else, returns nothing to indicate no version of the numeric ID was found
		return None

	@staticmethod
	def plot_dq_metric(p_title, p_x, p_y, p_label_x, p_label_y, p_control_ticks=False):

		import matplotlib.pyplot as plt

		plt.style.use("seaborn-whitegrid")
		plt.plot(p_x, p_y)
		plt.title(p_title)
		plt.xlabel(p_label_x)
		plt.ylabel(p_label_y);

		# Special control on frequency of y-ticks
		if p_control_ticks:
			plt.yticks(np.arange(0.0, float(ceil(max(p_y))), 0.25))

		plt.show()


def main(p_args):

	# 0. Setup

	collection_name = franklin_1998

	# for name in corpora_count_expectations:

	# 	# 1. Create a consistency object
	# 	consistency_obj = AOLM_DQ_Dickinson_Consistency(DickinsonCollection.collections[name], name)

	# 	# 2. Compare expectation to actuality
	# 	consistency_obj.compare(corpora_count_expectations[name])

	# 1. Get master title list from 'dickinson_poem_list'
	# Source: 'Poems of Emily Dickinson', ed. R.W. Franklin
	# Source: https://en.wikipedia.org/wiki/List_of_Emily_Dickinson_poems
	# Known IDs from master list not specifically listed as an 'F' manuscript
	known_non_franklin_ids = ["A13-6","A13-8", "excluded","A13-2"]
	master_title_list = get_master_list(known_non_franklin_ids)

	# 2. Create a consistency object
	consistency_obj = AOLM_DQ_Dickinson_Consistency(
		DickinsonCollection.collections["franklin_1998"],
		"franklin_1998")

	# 3. Compare expectation to actuality
	# (Variable length arguments are inquiring about multiple match thresholds)
	title_match_percentage = []
	num_titles_matching = []
	num_titles_mismatching = []
	num_titles_missing = []
	for threshold in p_args:
		
		print("MATCH THRESHOLD: {0}".format(threshold))
		
		# a. Compare digital corpus with Wiki master title list
		consistency_obj.compare(corpora_count_expectations["franklin_1998"],
							 	master_title_list,
							 	p_match_threshold=float(threshold))

		# b. Save data quality metrics for plotting below
		title_match_percentage.append((threshold, consistency_obj.dq_metric("title_match")))
		num_titles_matching.append((threshold, consistency_obj.dq_metric("num_titles_matching")))
		num_titles_mismatching.append((threshold, consistency_obj.dq_metric("num_titles_mismatching")))
		num_titles_missing.append((threshold, consistency_obj.dq_metric("num_titles_missing")))

	# 4. Plot data quality metrics
	x_label = "match threshold"
	x, y = zip(*title_match_percentage)
	AOLM_DQ_Dickinson_Consistency.plot_dq_metric("Title Match Percentage",
		x, [float(point) * 100 for point in y], x_label, "match discrepancy (%)",
		p_control_ticks=True)
	x, y = zip(*num_titles_matching)
	AOLM_DQ_Dickinson_Consistency.plot_dq_metric("# Matching Titles",
		x, y, x_label, "# titles")
	x, y = zip(*num_titles_mismatching)
	AOLM_DQ_Dickinson_Consistency.plot_dq_metric("# Mismatched Titles",
		x, y, x_label, "# titles")
	x, y = zip(*num_titles_missing)
	AOLM_DQ_Dickinson_Consistency.plot_dq_metric("# Missing Titles",
		x, y, x_label, "# titles")



if "__main__" == __name__:
	main(sys.argv[1:])
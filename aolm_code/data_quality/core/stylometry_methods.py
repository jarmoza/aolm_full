# Author: Jonathan Armoza
# Purpose: Stores stylometric analysis methods for Art of Literary Modeling
# Creation date: March 26, 2021
# Last updated: March 26, 2021

# Imports

# Built-ins

import glob
import math
import os

# Third party

import nltk


# Globals

federalist_papers = {
	
	"Madison":  [10, 14, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48],
	"Hamilton": [1, 6, 7, 8, 9, 11, 12, 13, 15, 16, 17, 21, 22, 23, 24,
				 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 59, 60,
				 61, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77,
				 78, 79, 80, 81, 82, 83, 84, 85],
	"Jay": 		[2, 3, 4, 5],
	"Shared": 	[18, 19, 20],
	"Disputed": [49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 62, 63],
	"TestCase": [64]
}

paths = {
	
	"test_case": f"{os.getcwd()}{os.sep}..{os.sep}data{os.sep}test_case{os.sep}",
	"text_collection": f"{os.getcwd()}{os.sep}..{os.sep}data{os.sep}collection{os.sep}",
}
paths["federalist_papers"] = "{0}{1}..{1}..{1}..{1}tutorials{1}stylometry_laramee{1}data{1}federalist_papers{1}".format(os.getcwd(), os.sep)
paths["federalist_test_case"] = paths["federalist_papers"] + "federalist_64.txt"


# Classes

class TextCollection(object):

	def __init__(self):
		pass

	def kilgariff_chi_squared(p_division_ids, p_comparison_id, n_most_frequent_words=500):

		# 1. Lowercase the tokens so that the same word, capitalized or not,
		# counts as one word
		division_tokens = { div_id: [token.lower() 
			for token in self.m_texts[div_id].tokens()] 
				for div_id in p_division_ids }
		division_tokens[p_comparison_id] = [token.lower() 
			for token in self.m_texts[p_comparison_id].tokens()]

		# 2. Calculate chisquared for each of the text collection divisions
		for div_id in p_division_ids:

			# A. First, build a joint corpus and identify the n most frequent words in it
			joint_corpus = (division_tokens[div_id] + 
				division_tokens[p_comparison_id])
			joint_freq_dist = nltk.FreqDist(joint_corpus)
			most_common = list(joint_freq_dist.most_common(n_most_frequent_words))

			# B. What proportion of the joint corpus is made up
			# of the candidate division's tokens?
			division_share = len(division_tokens[div_id]) / len(joint_corpus)

			# C. Now, let's look at the n most common words in the candidate
			# division's corpus and compare the number of times they can be observed
			# to what would be expected if the division's texts
			# and the comparison texts were both random samples from the same distribution.
			chisquared = 0
			for word, joint_count in most_common:

				# I. How often do we really see this common word?
				division_count = division_tokens[div_id].count(word)
				comparison_count = division_tokens[p_comparison_id].count(word)

				# II. How often should we see it?
				expected_division_count = joint_count * division_share
				expected_comparison_count = joint_count * (1 - division_share)

				# III. Add the word's contribution to the chi-squared statistic
				chisquared += ((division_count - expected_division_count) *
							   (division_count - expected_division_count) /
							   expected_division_count)

				chisquared += ((comparison_count - expected_comparison_count) *
							   (comparison_count - expected_comparison_count) / 
							   expected_disputed_count)

			print("The Chi-squared statistic for candidate", div_id, "is", chisquared)

	# Static methods

	# A function that reads a list text files into a single string
	@staticmethod
	def read_files_into_one_string(p_filepaths):
		
		strings = []

		for filepath in p_filepaths:
			with open(filepath, "r") as f:
				strings.append(f.read())

		return "\n".join(strings)

class Text(object):

	def __init__(self, p_filepath):

		self.m_filepath = p_filepath
		
		self.m_file_as_string = None
		self.m_tokens = []
		
		self.m_file_as_string = self.__read_file_to_string()
		self.m_tokens = self.__tokenize()

	def __read_file_to_string(self):

		with open(self.m_filepath, "r") as filehandle:
			file_as_string = filehandle.read()
		return file_as_string

	def __tokenize(self):
		
		return nltk.word_tokenize(self.m_file_as_string)

	@property
	def tokens(self):
		return self.m_tokens
	

class BurrowsDelta(object):

	# Constructor

	def __init__(self, p_collection_by_div_id, p_testcase_text, p_most_common_tokens=None):

		# 1. Clear all fields
		self.__initialize()

		# 2. Save parameters

		# A. Text collection fields
		self.m_collection_by_div_id = p_collection_by_div_id
		self.m_division_ids = list(self.m_collection_by_div_id.keys())

		# B. Test case text fields
		self.m_testcase_text = p_testcase_text

		# C. Remember how many most common tokens are being examined as features
		self.m_most_common_tokens = BurrowsDelta.feature_stats_mc_tokens \
			if not p_most_common_tokens else p_most_common_tokens

		# 3. Transform the authors' corpora into lists of lowercase word tokens
		# Filter out punctuation
		for div_id in self.m_division_ids:
			
			tokens = nltk.word_tokenize(self.m_collection_by_div_id[div_id])
			
			self.m_tokens_by_division[div_id] = ([token.lower() for token in tokens
				if any(c.isalpha() for c in token)])

		# 4. Combine tokens of every text except our comparison case into a single collection
		for div_id in self.m_division_ids:
			self.m_whole_corpus_tokens += self.m_tokens_by_division[div_id]

		# 5. Get a frequency distribution of all tokens in the corpus
		self.m_whole_corpus_freq_dist = list(
			nltk.FreqDist(self.m_whole_corpus_tokens).most_common(self.m_most_common_tokens))						

	# Private methods

	def __initialize(self):

		# Token fields
		self.m_tokens_by_division = {}
		self.m_whole_corpus_tokens = []

		# Features fields
		self.m_features = []
		self.m_feature_freqs = {}
		self.m_feature_zscores = {}

		# Corpus fields
		self.m_collection_by_div_id = {}
		self.m_corpus_features = {}
		self.m_division_ids = []
		self.m_whole_corpus_freq_dist = []

		# Test case fields
		self.m_testcase_text = None
		self.m_testcase_freqs = {}
		self.m_testcase_tokens = []
		self.m_testcase_zscores = {}

	# Interface methods

	def run(self):

		# 1. Determine features to be examined and their frequencies in the collection
		self.feature_selection()

		# 2. Calculate feature means and standard deviations across the collection
		self.feature_stats()

		# 3. Calculate z-scores for each feature in each text in the collection
		self.feature_z_scores()

		# 4. Determine the stats and z-scores of the same features in a test case text
		self.test_case()

		# 5. Calculate delta between test case features and features in teach text
		self.delta()

	# Helper methods

	def feature_selection(self):

		# 1. Calculate features for each subcorpus
		self.m_features = [token for token, freq in self.m_whole_corpus_freq_dist]
		self.m_feature_freqs = {}

		for div_id in self.m_division_ids:

			# A. Create a dictionary for each candidate's features
			self.m_feature_freqs[div_id] = {}

			# B. Calculate the number of tokens in the division's subcorpus
			overall = len(self.m_tokens_by_division[div_id])

			# C. Calculate each feature's presence in the subcorpus
			for feature in self.m_features:
				presence = self.m_tokens_by_division[div_id].count(feature)
				self.m_feature_freqs[div_id][feature] = presence / overall

	def feature_stats(self):

		# 0. The data structure into which we will be storing the "corpus standard" statistics
		self.m_corpus_features = {}

		# 1. Calculate mean and standard deviation for each feature
		for feature in self.m_features:
			
			# A. Create a sub-dictionary that will contain the feature's mean
			# and standard deviation
			self.m_corpus_features[feature] = {}

			# B. Calculate the mean of the frequencies expressed in the subcorpora
			feature_average = 0
			for div_id in self.m_division_ids:
				feature_average += self.m_feature_freqs[div_id][feature]
			feature_average /= len(self.m_division_ids)
			self.m_corpus_features[feature][BurrowsDelta.feature_stats_mean] = feature_average

			# C. Calculate the standard deviation using the basic formula for a sample
			feature_stdev = 0
			for div_id in self.m_division_ids:
				diff = self.m_feature_freqs[div_id][feature] - \
					self.m_corpus_features[feature][BurrowsDelta.feature_stats_mean]
				feature_stdev += diff * diff
			feature_stdev /= len(self.m_division_ids) - 1
			feature_stdev = math.sqrt(feature_stdev)
			self.m_corpus_features[feature][BurrowsDelta.feature_stats_stddev] = feature_stdev

	def feature_z_scores(self):
		
		# 1. Calculate z-scores for features in each corpus division
		for div_id in self.m_division_ids:
			
			self.m_feature_zscores[div_id] = {}
			for feature in self.m_features:

				# Z-score definition = (value - mean) / stddev
				
				# Intermediate variables to make the code easier to read
				feature_val = self.m_feature_freqs[div_id][feature]
				feature_mean = self.m_corpus_features[feature][BurrowsDelta.feature_stats_mean]
				feature_stdev = self.m_corpus_features[feature][BurrowsDelta.feature_stats_stddev]

				# A. Calculate Z-score for this feature in the division
				self.m_feature_zscores[div_id][feature] = \
					((feature_val - feature_mean) / feature_stdev)

	def test_case(self):

		# 1. Tokenize the test case
		self.m_testcase_tokens = self.m_testcase_text.tokens

		# 2. Filter out punctuation and lowercase the tokens
		self.m_testcase_tokens = [token.lower() for token in self.m_testcase_tokens
						   if any(c.isalpha() for c in token)]

		# 3. Calculate the test case's features
		overall = len(self.m_testcase_tokens)
		for feature in self.m_features:
			presence = self.m_testcase_tokens.count(feature)
			self.m_testcase_freqs[feature] = presence / overall

		# 4. Calculate the test case's feature z-scores
		for feature in self.m_features:
			feature_val = self.m_testcase_freqs[feature]
			feature_mean = self.m_corpus_features[feature][BurrowsDelta.feature_stats_mean]
			feature_stdev = self.m_corpus_features[feature][BurrowsDelta.feature_stats_stddev]
			self.m_testcase_zscores[feature] = (feature_val - feature_mean) / feature_stdev
			print("Test case z-score for feature", feature, "is", self.m_testcase_zscores[feature])

	def delta(self):

		# 1. Calculate delta between z-scores of feature in test case and in each text
		for div_id in self.m_division_ids:

			# A. Delta calculation
			delta = 0
			for feature in self.m_features:
				delta += math.fabs((self.m_testcase_zscores[feature] -
									self.m_feature_zscores[div_id][feature]))
			delta /= len(self.m_features)
			print("Delta score for candidate", div_id, "is", delta)		

	# Static fields

	feature_stats_mean = "Mean"
	feature_stats_stddev = "StdDev"
	feature_stats_mc_tokens = 30


# Script functions

# A function that compiles all of the text files associated with a single author into a single string
def read_federalist_files_by_division():

	# Make a dictionary out of the authors' corpora
	federalist_by_author = {}
	for author, files in federalist_papers.items():

		strings = []
		for filename in files:
			with open(f"{paths['federalist_papers']}federalist_{filename}.txt", "r") as f:
				strings.append(f.read())

		federalist_by_author[author] = "\n".join(strings)

	return federalist_by_author

def read_collection_by_division():

	pass


def main():

	# 0. Script parameters
	text_collection_path = paths["federalist_papers"]
	test_case_path = paths["federalist_test_case"]
	read_collection = read_federalist_files_by_division
	
	# 1. Read text collection
	text_collection_by_div_id = read_collection()

	# text_collection = [Text(text_filepath) \
	# 	for text_filepath in glob.glob(text_collection_path + "*.txt")]

	# 2. Read test case text
	test_case_text = Text(test_case_path)

	# 3. Calculate Burrow's delta
	delta = BurrowsDelta(text_collection_by_div_id, test_case_text)
	delta.run()


if "__main__" == __name__:
	main()
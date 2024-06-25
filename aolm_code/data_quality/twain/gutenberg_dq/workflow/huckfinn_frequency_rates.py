# Author: Jonathan Armoza
# Created: November 13, 2021
# Purpose: Demonstrate measurement and visualization of data quality metric measurements
# as a rate (e.g. a function of time) over the course of 'text-time' in a text
# The idea here is to demonstrate the simplest example of data quality for humanities

# Example #1: Word frequency distribution by chapter

# Steps
# 1: Ingest text by chapter
# 2: Calculate word frequencies for each chapter
# 3: Create cumulative word frequencies for each chapter
# 4: Visualize the change in word frequencies of the top N words by chapter
# 5: Measure the rate of change of each of those top N words by chapter
# 6: Visualize the rate of change of each of those top N words by chapter
# 7: Perform steps 1-6 on a text variant (different edition, different publisher, etc.)
# 8: Compare the change in word frequencies and the rate of change across text variants
# 9: Write about observations

# Requirements
# 1: A document class
# 2: A Text class that contains documents
# 3: Document functionality that tallies word frequencies
# 4: Text functionality that tallies cumulative word frequencies across documents
# 5: A Visualization class that takes word frequency counts and plots them by chapter
# 6: Text functionality that measures the rate of change for word frequencies across documents
# 7: Visualization functionality that plots the rate of change of word frequencies
# 8: A TextCollection class
# 9: TextCollection functionality that compares word frequencies, cumulative word frequencies,
#    and rates of change in word frequency

# Text(s) for example
# 1: Versions of Mark Twain's Huckleberry Finn on Project Gutenberg

# Idea
# Create a datalad for text versions used in The Art of Literary Modeling

# Imports

# Standard library
from collections import Counter
from collections import OrderedDict
import glob
import json
import os

# Third parties libraries
import nltk
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# Local libraries
from data_quality.core.dq_cleaner import AoLM_TextCleaner
from utilities import aolm_paths
from utilities.aolm_utilities import clean_string
from utilities.aolm_utilities import debug_separator

from data_quality.dickinson.core.dickinson_poem_final import DickinsonPoem

# Setup code and data paths
aolm_paths.setup_paths()

# Work todo:
# 1) Finish word differences function
# 2) Convert word progression plot function into a subplot
# 3) Fix the input/output folder situation with the HuckFinn data
# 4) Try this all out on the HuckFinn editions

# Classes

class WordFrequencyTracker:

	# Constructor

	def __init__(self, p_json_path, p_master_text, p_stopwords_filepath="", p_process=True):

		# 0. Save constructor arguments
		self.m_json_path = p_json_path
		self.m_source_text = p_master_text
		self.m_stopwords_filepath = p_stopwords_filepath

		# 0. Tracker object can compare texts or just depict one text
		self.m_single_text = self.m_json_path.endswith(".json")

		# 1. Initialize other class fields
		self.m_texts = {}

		# 2. Read in texts
		self.__read_texts()

		# 3. Only perform text processing if requested. Otherwise class user can make the calls
		if p_process:

			# A. Perform the multi-step processing
			self.process(
				p_cleaning_function=clean_string,
				p_tokenization_function=nltk.word_tokenize,
				#p_tokenization_function=DickinsonPoem.tokenize_line
			)
		
	# Private methods

	def __create_clean_components(self, p_cleaning_function):

		# 1. Clean each text
		# NOTE: Subcomponents will be flattened and brought up to the top level
		for text in self.m_texts:

			# A. Create a clean version of the text's components
			self.m_texts[text]["clean_components"] = {}

			# B. Clean each component in the text
			for component in self.m_texts[text]["flat_components"]:

				# I. Create an entry for the clean version
				self.m_texts[text]["clean_components"][component] = []
			
				# II. Clean each line in the component
				for line in self.m_texts[text]["flat_components"][component]:
					self.m_texts[text]["clean_components"][component].append(
						p_cleaning_function(line))

	def __flatten_components(self):

		# 1. Clean each text
		# NOTE: Subcomponents will be flattened and brought up to the top level
		for text in self.m_texts:

			# A. Create a clean version of the text's components
			self.m_texts[text]["flat_components"] = {}

			# B. Bring all subcomponents up to the top level 
			for component in self.m_texts[text]["components"]:

				# I. Create an entry for the subcomponents in the flattened components
				if dict == type(self.m_texts[text]["components"][component]):
					for subcomponent in self.m_texts[text]["components"][component]:
						self.m_texts[text]["flat_components"][subcomponent] = [line for line in self.m_texts[text]["components"][component][subcomponent]]

	def __read_texts(self):

		# 1. Single text
		if self.m_single_text:

			# A. Filename without the extension is the edition key
			filename_noext = os.path.splitext(os.path.basename(self.m_json_path))[0]

			# B. Read and save the given json file
			with open(self.m_json_path, "r") as json_fileobject:
				self.m_texts[filename_noext] = json.load(json_fileobject)

		# 2. Multiple texts
		else:

			for json_filepath in glob.glob(self.m_json_path + "*.json"):

				# A. Filename without the extension is the edition key
				filename_noext = os.path.splitext(os.path.basename(json_filepath))[0]

				# B. Read json in the folder
				with open(json_filepath, "r") as json_fileobject:
					self.m_texts[filename_noext] = json.load(json_fileobject)
	
	def __tally_cumulative_word_frequencies_by_component(self, p_component_skip_list):

		for text in self.m_texts:
			
			# A. New json section to store cumulative word counts of components in chronological text time
			self.m_texts[text]["cumulative_word_counts"] = {}

			# B. Temporary dictionary to store word counts as they accumulate
			cumulative_counts = {}

			for component in self.m_texts[text]["clean_components"]:

				# I. Skip specified components
				if component in p_component_skip_list:
					continue

				self.m_texts[text]["cumulative_word_counts"][component] = {}

				# II. Add word counts of this component to the cumulative total
				for word in self.m_texts[text]["word_counts"][component]:
					if word not in cumulative_counts:
						cumulative_counts[word] = 0
					cumulative_counts[word] += self.m_texts[text]["word_counts"][component][word]

				# III. Store cumulative word counts thus far for this component
				for word in cumulative_counts:
					self.m_texts[text]["cumulative_word_counts"][component][word] = cumulative_counts[word]

	def __tally_total_word_frequencies(self):

		# 1. Tally up the counts of all the words in all the components of each text
		for text in self.m_texts:

			self.m_texts[text]["total_word_frequencies"] = {}

			for component in self.m_texts[text]["word_counts"]:

				for word in self.m_texts[text]["word_counts"][component]:

					if word not in self.m_texts[text]["total_word_frequencies"]:
						self.m_texts[text]["total_word_frequencies"][word] = 0
					self.m_texts[text]["total_word_frequencies"][word] += 1

	def __tally_word_frequencies(self, p_tokenization_function):

		for text in self.m_texts:

			# A. New json section to store word counts of sections
			self.m_texts[text]["word_counts"] = {}

			for component in self.m_texts[text]["clean_components"]:
				
				tokens = p_tokenization_function("\n".join(self.m_texts[text]["clean_components"][component]))
				# tokens = nltk.word_tokenize("\n".join(self.m_texts[text]["clean_components"][component]))
				# tokens = DickinsonPoem.tokenize_line("\n".join(self.m_texts[text]["clean_components"][component]))
				self.m_texts[text]["word_counts"][component] = Counter(tokens)

	# Properties

	@property
	def text(self, p_textname):
		return self.m_texts[p_textname]
	@property
	def texts(self):
		return self.m_texts
	
	# Public methods

	def process(self, p_cleaning_function=clean_string,
		p_tokenization_function=nltk.word_tokenize,
		p_component_skip_list=["header", "footer", "frontmatter"]):

			# A. Bring all subcomponents up to the top level
			# NOTE: All processing is done of the "flat_components" key in m_texts
			# so as to preserve the original text components
			self.__flatten_components()

			# B. Create a set of components cleaned with the 'clean_string' function
			self.__create_clean_components(p_cleaning_function)

			# C. Calculate word frequencies for each text component
			self.__tally_word_frequencies(p_tokenization_function)

			# D. Calculate word frequencies as they accumulate by successive components
			self.__tally_cumulative_word_frequencies_by_component(p_component_skip_list)

			# E. Calculate word frequencies across the entirety of each text
			self.__tally_total_word_frequencies()

	def plot_top_words_progression(self):

		# 1. Build a line chart for each text showing the word frequency accumulation for each text

		# A. Create traces
		for text in self.m_texts:
			fig = go.Figure()
			for word in self.m_texts[text]["top_word_counts_by_chapter"]:
				fig.add_trace(
					go.Scatter(
						x=list(self.m_texts[text]["cumulative_word_counts"].keys()),
						y=self.m_texts[text]["top_word_counts_by_chapter"][word],
						mode="lines", name=word
					)
				)
			fig.show(title=text)
				
	def top_n_words(self, p_top_n, p_last_component, p_save_results=True,
		p_remove_stopwords=False, p_stopwords_filepath=None):

		# last_component = "footer"
		# last_component = "HUCKLEBERRYFINN_BODY_CHAPTER THE LAST"
		top_n_words = {}	

		# 1. Find the top N words from each text and compare them
		for text in self.m_texts:
			
			# A. Create an orderable dictionary from the cumulative word counts for this text
			cumulative_word_counts = OrderedDict(self.m_texts[text]["cumulative_word_counts"][p_last_component])

			# B. Create a list of tuples from the ordered dictionary
			word_freq_tuples = [(word, cumulative_word_counts[word]) for word in cumulative_word_counts]

			# C. Remove stopwords from the tuple list
			if p_remove_stopwords and len(self.m_stopwords_filepath):

				# I. Read in stop words from given file
				# with open(aolm_paths.data_paths["aolm_general_root"] + "input" + os.sep + "voyant_stopwords.txt", "r") as stopwords_file:
				with open(p_stopwords_filepath, "r") as stopwords_file:
					stopwords = [word.strip() for word in stopwords_file.readlines()]

				# II. Remove all listed stopwords from the tuples
				word_freq_tuples = [tuple for tuple in word_freq_tuples if tuple[0] not in stopwords]

			# D. Sort the tuples by their overall frequency in the text
			word_freq_tuples = sorted(word_freq_tuples, key=lambda x: x[1], reverse=True)[0:p_top_n]
			for index in range(len(word_freq_tuples)):
				print("{0}: {1}, {2}".format(index + 1, word_freq_tuples[index][0], word_freq_tuples[index][1]))

			# E. Save the filtered top words
			top_n_words[text] = word_freq_tuples
			if p_save_results:
				self.m_texts[text]["top_words"] = word_freq_tuples

			return top_n_words	

	def top_words_by_component(self, p_top_n, p_save_results=True):

		top_words = {}

		# 1. Track changes of top N words per component per text
		for text in self.m_texts:
			
			# A. Make sure the top words for this text have been determined
			if "top_words" not in self.m_texts[text]:
				self.top_words(p_top_n)

			# NOTE: Cumulativ word counts are tallied during process()

			# A. Keep strack of word frequencies in each component for the top N words
			top_words = [word_tuple[0] for word_tuple in self.m_texts[edition]["top_words"]]
			top_word_counts_by_component = {word:[] for word in top_words}

			# B. Fill out list of word frequencies for the top N words for each component
			for component in self.m_texts[edition]["cumulative_word_counts"]:
				for word in top_word_counts_by_component:
					if word not in self.m_texts[edition]["cumulative_word_counts"][component]:
						top_word_counts_by_component[word].append(0)
					else:
						top_word_counts_by_component[word].append(self.m_texts[edition]["cumulative_word_counts"][component][word])
			
			# C. Save top counts by component for this text
			top_words[text] = top_word_counts_by_component
			if p_save_results:
				self.m_texts[edition]["top_word_counts_by_component"] = top_word_counts_by_component

		return top_words

	def word_count_differences(self, p_last_component):

		# 1. Determine and plot the word frequency differences between a source text
		# and the other texts contained in this object
		# NOTE: This only functions if multiple texts are stored
		if not self.m_single_text:

			# A. Prepare for subplot plotting of word differences between source and other texts
			number_cols = 2
			number_rows = len(self.m_texts) - 1
			row_index = 1

			# B. Create the plotly figure
			fig = make_subplots(rows=number_rows, cols=number_cols)

			# C. Determine increased and decreased for each non-source text and create subplot traces for each
			for text in self.m_texts:

				# I. Keeps track of increasing and decreasing word frequencies from source text
				self.m_texts[text]["increases"] = {}
				self.m_texts[text]["decreases"] = {}

				# II. Build increase and decrease lists of word frequency differences between this text and the source text
				if text != self.m_source_text:

					# a. Build the increased and decreased word lists for this text
					for word in self.m_texts[text]["total_word_frequencies"]:

						# a. Only examine words that are in both the source and compared texts' vocabularies
						if word in self.m_texts[self.m_source_text]["total_word_frequencies"]:

							if self.m_texts[text]["total_word_frequencies"][word] > \
								self.m_texts[self.m_source_text]["total_word_frequencies"][word]:

								self.m_texts[text]["decreases"][word] = \
									self.m_texts[text]["total_word_frequencies"][word] - \
										self.m_texts[self.m_source_text]["total_word_frequencies"][word]

							elif self.m_texts[text]["total_word_frequencies"][word] < \
								self.m_texts[self.m_source_text]["total_word_frequencies"][word]:

								self.m_texts[text]["increases"][word] = \
									self.m_texts[self.m_source_text]["total_word_frequencies"][word] - \
										self.m_texts[text]["total_word_frequencies"][word]

					# b. Sort these lists
					increase_tuples = [(word, self.m_texts[text]["increases"][word]) \
						 for word in self.m_texts[text]["increases"]]
					increase_tuples = sorted(increase_tuples, key=lambda x: x[1], reverse=True)
					decrease_tuples = [(word, self.m_texts[text]["decreases"][word]) \
						 for word in self.m_texts[text]["decreases"]]
					decrease_tuples = sorted(decrease_tuples, key=lambda x: x[1], reverse=True)
										 
					# print(debug_separator)
					# print(text)
					# print("Increased words")
					# for word_tuple in increase_tuples:
					# 	print("{0}: {1}".format(word_tuple[0], word_tuple[1]))
					# print("Decreased words")
					# for word_tuple in decrease_tuples:
					# 	print("{0}: {1}".format(word_tuple[0], word_tuple[1]))

					# c. Add bar plot trace for the increase and decreases as a subplot

					# NEXT: fix trace addition and then show the plot
					fig.add_trace(
						go.Bar(x=[word_tuple[0] for word_tuple in increase_tuples],
							   y=[word_tuple[1] for word_tuple in increase_tuples]),
						row=row_index, col=1
					)
					fig.add_trace(
						go.Bar(x=[word_tuple[0] for word_tuple in decrease_tuples],
							   y=[-1 * int(word_tuple[1]) for word_tuple in decrease_tuples]),
						row=row_index, col=1
					)

					# d. Increment rows index
					row_index += 1

			# D. Show the plot
			fig.show()
					
		else:
			print("WordFrequencyTracker only contains text: {0}".format(self.m_json_path))
	
	def write(self, p_output_path, p_new_filetag="processed"):
		
		# 1. Write out the json with processed data
		for text in self.m_texts:
			with open(p_output_path + "{0}_{1}.json".format(text, p_new_filetag), "w") as cleaned_json_fileobj:
				json.dump(self.m_texts[text], cleaned_json_fileobj, indent=4)


def main():

	# Setup for word frequency tracking
	# input_folder = aolm_paths.data_paths["aolm_twain"]["gutenberg_dq"] + "input" + os.sep
	# output_folder = aolm_paths.data_paths["aolm_twain"]["gutenberg_dq"] + "output" + os.sep
	input_folder = "{0}txt{1}demarcated{1}".format(aolm_paths.data_paths["twain"]["internet_archive"], os.sep)
	output_folder = "{0}txt{1}demarcated{1}output{1}".format(aolm_paths.data_paths["twain"]["internet_archive"], os.sep)
	stopwords_filepath = aolm_paths.data_paths["aolm_general"]["voyant_stopwords"]
	# last_text_component = "HUCKLEBERRYFINN_BODY_CHAPTER THE LAST"
	source_text_filename = "2021-02-21-HuckFinn_cleaned"

	# 1. Track the word frequencies for all the "Adventures of Huckleberry Finn" editions (in json form)
	tracker = WordFrequencyTracker(input_folder, source_text_filename, stopwords_filepath)

	# 2. Examine word count differences between the editions
	# tracker.word_count_differences(last_text_component)

	# 3. Write the new json from the tracker to the outptu folder
	tracker.write(output_folder)

if "__main__" == __name__:
	main()

# # Main script


# # huckfinn = HuckleberryFinn(paths["input"] + paths["2021-02-21"], huckfinn_headers)
# # output_folder = "{0}{1}data{1}output{1}".format(os.getcwd(), os.sep)
# # huckfinn.output(output_folder)


# # 1. Read in chapters of Huckleberry Finn editions

# # A. Folder where json versions of the Huckleberry Finn editions are output
# json_folder = aolm_paths.data_paths["aolm_twain"]["gutenberg_dq"] + "input" + os.sep

# # B. Read in each edition json
# edition_data = {}
# for json_filepath in glob.glob(json_folder + "*.json"):

# 	# I. Filename without the extension is the edition key
# 	filename_noext = os.path.splitext(os.path.basename(json_filepath))[0]

# 	# II. Read json but skip non-"HuckFinn" files in the folder
# 	if "HuckFinn" in filename_noext and "cleaned" not in filename_noext:
# 		# print(json_filepath)
# 		with open(json_filepath, "r") as json_fileobject:
# 			edition_data[filename_noext] = \
# 				json.load(json_fileobject)

# # 2. Clean each edition
# # NOTE: From this point "body" subcomponents will be brought up to the level of header and footer
# for edition in edition_data:

# 	# A. Create a clean version of the edition's components
# 	edition_data[edition]["clean_components"] = {}

# 	# I. Clean each component in the edition
# 	for component in edition_data[edition]["components"]:

# 		# a. Treat body differently since it has subcomponents
# 		if "body" == component:

# 			for subcomponent in edition_data[edition]["components"]["body"]:
				
# 				# i. Create an entry for the clean version	
# 				edition_data[edition]["clean_components"][subcomponent] = []
			
# 				# ii. Clean each line in the component
# 				for line in edition_data[edition]["components"]["body"][subcomponent]:
# 					edition_data[edition]["clean_components"][subcomponent].append(
# 						clean_string(line))
# 		else:
# 			# i. Create an entry for the clean version
# 			edition_data[edition]["clean_components"][component] = []
		
# 			# ii. Clean each line in the component
# 			for line in edition_data[edition]["components"][component]:
# 				edition_data[edition]["clean_components"][component].append(
# 					clean_string(line))

# # 3. Calculate word frequencies for each chapter
# for edition in edition_data:

# 	# A. New json section to store word counts of sections
# 	edition_data[edition]["word_counts"] = {}

# 	for component in edition_data[edition]["clean_components"]:
		
# 		tokens = nltk.word_tokenize("\n".join(edition_data[edition]["clean_components"][component]))
# 		# tokens = DickinsonPoem.tokenize_line("\n".join(edition_data[edition]["clean_components"][component]))
# 		edition_data[edition]["word_counts"][component] = Counter(tokens)

# # 4. Create cumulative word frequencies for each chapter
# for edition in edition_data:
	
# 	# A. New json section to store cumulative word counts of sections in chronological text time
# 	edition_data[edition]["cumulative_word_counts"] = {}

# 	# B. Temporary dictionary to store word counts as they accumulate
# 	cumulative_counts = {}

# 	for component in edition_data[edition]["clean_components"]:

# 		to_be_skipped = ["header", "footer", "frontmatter"]
# 		if component in to_be_skipped:
# 			continue

# 		edition_data[edition]["cumulative_word_counts"][component] = {}

# 		# A. Add word counts of this component to the cumulative total
# 		for word in edition_data[edition]["word_counts"][component]:
# 			if word not in cumulative_counts:
# 				cumulative_counts[word] = 0
# 			cumulative_counts[word] += edition_data[edition]["word_counts"][component][word]

# 		# B. Store cumulative word counts thus far for this component
# 		for word in cumulative_counts:
# 			edition_data[edition]["cumulative_word_counts"][component][word] = cumulative_counts[word]
		

# # 5. Find the top N words from each edition and compare them
# # last_component = "footer"
# last_component = "HUCKLEBERRYFINN_BODY_CHAPTER THE LAST"
# top_count = 5
# for edition in edition_data:
	
# 	# A. Create an orderable dictionary from the cumulative word counts for this edition
# 	cumulative_word_counts = OrderedDict(edition_data[edition]["cumulative_word_counts"][last_component])

# 	# B. Create a list of tuples from the ordered dictionary
# 	word_freq_tuples = [(word, cumulative_word_counts[word]) for word in cumulative_word_counts]

# 	print(debug_separator)
# 	print(edition)

# 	# # C. Remove stopwords from the tuple list

# 	# # I. Read in stop words from given file
# 	# stopwords_file = "voyant_stopwords.txt"
# 	# with open(aolm_paths.data_paths["aolm_general_root"] + "input" + os.sep + stopwords_file, "r") as stopwords_file:
# 	# 	stopwords = [word.strip() for word in stopwords_file.readlines()]

# 	# # II. Remove all listed stopwords from the tuples
# 	# word_freq_tuples = [tuple for tuple in word_freq_tuples if tuple[0] not in stopwords]

# 	# D. Sort the tuples by their overall frequency in the edition
# 	word_freq_tuples = sorted(word_freq_tuples, key=lambda x: x[1], reverse=True)[0:top_count]
# 	for index in range(len(word_freq_tuples)):
# 		print("{0}: {1}, {2}".format(index + 1, word_freq_tuples[index][0], word_freq_tuples[index][1]))

# 	edition_data[edition]["top_words"] = word_freq_tuples

# # 6. Track changes of top N words per chapter per edition
# for edition in edition_data:

# 	# A. Keep strack of word frequencies in each chapter for the top N words
# 	top_words = [word_tuple[0] for word_tuple in edition_data[edition]["top_words"]]
# 	top_word_counts_by_chapter = {word:[] for word in top_words}

# 	# B. Fill out list of word frequencies for the top N words for each chapter
# 	for component in edition_data[edition]["cumulative_word_counts"]:
# 		for word in top_word_counts_by_chapter:
# 			if word not in edition_data[edition]["cumulative_word_counts"][component]:
# 				top_word_counts_by_chapter[word].append(0)
# 			else:
# 				top_word_counts_by_chapter[word].append(edition_data[edition]["cumulative_word_counts"][component][word])
	
# 	# C. Save top counts by chapter for this edition
# 	edition_data[edition]["top_word_counts_by_chapter"] = top_word_counts_by_chapter

# # 7. Build a line chart for each edition showing the word frequency accumulation for each edition

# # A. Create traces
# # for edition in edition_data:
# # 	fig = go.Figure()
# # 	for word in edition_data[edition]["top_word_counts_by_chapter"]:
# # 		fig.add_trace(
# # 			go.Scatter(
# # 				x=list(edition_data[edition]["cumulative_word_counts"].keys()),
# # 				y=edition_data[edition]["top_word_counts_by_chapter"][word],
# # 				mode="lines", name=word
# # 			)
# # 		)
# # 	fig.show(title=edition)

# # Write out the json with clean data
# for edition in edition_data:
# 	with open(json_folder + edition + "_cleaned.json", "w") as cleaned_json_fileobj:
# 		json.dump(edition_data[edition], cleaned_json_fileobj, indent=4)



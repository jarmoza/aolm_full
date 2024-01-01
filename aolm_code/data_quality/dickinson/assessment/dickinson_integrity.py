# File notes: 	

# Currently uses words_dictionary.json - A json format of 466K English words
# Source: https://github.com/dwyl/english-words

# Source chronological list of R.W. Franklin manuscript IDs from:
# https://books.google.ca/books?id=GYuUA9gn1hUC&printsec=frontcover#v=onepage&q&f=false

# Built-ins
import csv 		# Dictionary reader
import glob    	# File searching
import json 	# Reading in dictionary file
import os   	# Working directory and folder separator char

# Third party
from tqdm import tqdm

# Local
from dickinson_poem import DickinsonPoem
from dickinson_collection import DickinsonCollection
from dickinson_consistency import get_master_list

# Debug messaging

# import my_logging
# logger = my_logging.get_logger(__name__)
# debug = logger.debug
# # logger.disable(logging.DEBUG)	# Comment out to enable debug messages

import my_logging
from my_logging import logging
from my_logging import tqdm
from my_logging import debug_separator
debug = logging.debug
# logging.disable(logging.DEBUG) # Comment out to enable debug messages

# NOTES: Next integrity metric: 
# the number of words in given texts accountable to a dictionary

# Globals

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


class AOLM_DQ_Dickinson_Integrity(object):

	def __init__(self, p_texts_path, p_corpus_name, p_file_extension="tei"):

		print(p_texts_path)

		# 1. Create a collection object of Dickinson texts
		self.m_texts = DickinsonCollection(p_texts_path, p_corpus_name, p_file_extension)

		# 2. Integrity values are stored here
		self.m_integrity = {}


	# Properties

	@property
	def collection(self):
		return self.m_texts	

	@property
	def metric(self):
		return self.m_integrity
	
	@property
	def text_count(self):
		return len(self.m_texts)


	# Primary functionality

	def compare(self, p_expected_match_count, p_dictionary_filepath):

		# 1. Get integrity of unique, known words in texts
		self.compare_words_to_dictionary(p_dictionary_filepath)

		# 2. Check for tag integrity across Dickinson archive TEI files
		self.compare_teiheader_tags()

	# Compares words of the texts in this object to a given dictionary
	# Currently uses words_dictionary.json - A json format of 466K English words
	# Source: https://github.com/dwyl/english-words
	def compare_words_to_dictionary(self, p_dictionary_filepath):

		# 1. Read in given dictionary file
		dictionary = AOLM_DQ_Dickinson_Integrity.read_dictionary(p_dictionary_filepath)

		# 2. Gather and store lexicon of the text collection
		lexicon = self.m_texts.lexicon

		# 3. Account for all words in the lexicon not in the dictionary
		missing_words_list = []
		for word in lexicon:
			if word not in dictionary:
				cleaned_word = word if "'" not in word else word[0:word.find("'")]
				if cleaned_word in dictionary:
					continue
				missing_words_list.append(cleaned_word)

		# 4. Save integrity metric: percent words known to the dictionary / all words in the collection
		self.m_integrity["known_words"] = 100 * (len(lexicon) - len(missing_words_list)) / float(len(lexicon))

		# 5. Save missing words for further data quality iteration checks
		self.m_integrity["missing_words_list"] = missing_words_list

	# Accounts for the integrity/agreement of the types of content (tags) in
	# teiheader tags of the current poem collection
	def compare_teiheader_tags(self):

		# 0. Manuscript ID to tag dictionary
		poem_tag_dict = {}
		all_tags = []

		# 1. Create a counting dictionary of tags inside each poem's tei header
		for poem in self.m_texts.list:

			# a. Set up an empty dictionary to count tags in the header
			poem_tag_dict[poem.manuscript_id] = {}

			# b. Count all tags for this poem
			for tag in poem.soup.tei.find("teiheader").findChildren():
				if tag.name not in poem_tag_dict[poem.manuscript_id]:
					poem_tag_dict[poem.manuscript_id][tag.name] = 0
				poem_tag_dict[poem.manuscript_id][tag.name] += 1
				if tag.name not in all_tags:
					all_tags.append(tag.name)

		# 2. Calculate total and average amounts of tags in poem tei headers
		self.m_integrity["tag_average"] = { tag_name: 0 for tag_name in all_tags }
		for manu_id in poem_tag_dict:
			for tag_name in poem_tag_dict[manu_id]:
				self.m_integrity["tag_average"][tag_name] += 1
		self.m_integrity["tag_total"] = { tag_name: self.m_integrity["tag_average"][tag_name] \
										  for tag_name in all_tags }
		self.m_integrity["works_total"]	= len(self.m_texts.list)
		for tag_name in all_tags:				
			self.m_integrity["tag_average"][tag_name] /= len(self.m_texts.list)
			self.m_integrity["tag_average"][tag_name] *= 100


	# Static methods

	@staticmethod
	def read_dictionary(p_filepath, p_format="json"):

		with open(p_filepath, "r") as dictionary_file:
			dictionary = json.load(dictionary_file)

		return dictionary

def main():

	corpus_name = "franklin_1998"
	dictionary_filepath = ""

	# 1. Create an integrity DQ object and read Emily Dickinson Archive TEI texts
	integrity_obj = AOLM_DQ_Dickinson_Integrity(paths["archive_corpus"], corpus_name)

	# 2. Compare archive manuscript IDs with distribution table manuscript IDs 
	integrity_obj.compare(corpora_count_expectations[corpus_name], paths["dictionary"])

	# 3. Output metrics to screen
	for m in integrity_obj.metric:
		print("{0}\n{1}: {2}".format(debug_separator, m, integrity_obj.metric[m]))


if "__main__" == __name__:
	main()



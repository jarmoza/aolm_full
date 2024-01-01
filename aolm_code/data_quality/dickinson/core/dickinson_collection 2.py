# Author: Jonathan Armoza
# Creation date: November 25, 2019
# Last Updated: September 11, 2020
# Purpose: Stores information about a whole collection of Emily Dickinson texts.
# Each text is stored internally as a DickinsonPoem object.

# Imports

# Built-in
import glob    	   # File searching
import itertools   # Turning lists of a lists into one list
import os   	   # Working directory and folder separator char

# Local
import aolm_string_utilities as asu			# String formatting
from dickinson_poem import DickinsonPoem	# Text objects

# Debug messaging
import my_logging
from my_logging import logging
from my_logging import tqdm
debug = logging.debug
# logging.disable(logging.DEBUG) # Comment out to enable debug messages


# Objects

class DickinsonCollection:

	# Constructor

	def __init__(self, p_corpus_name, p_texts_path="",  p_file_extension="tei", p_text_collection=None):

		# 0. Save parameters

		# Path to text files
		self.m_texts_path = p_texts_path
		if "" != p_texts_path:
			self.m_texts_path = asu.format_path(p_texts_path)

		self.m_file_extension = p_file_extension	# Expected file extension of the text files
		self.m_corpus_name = p_corpus_name			# String name of the corpus

		# 1. For text collections built from known paths, use the corpus name
		# as a key in the static collection dictionary
		if "" == self.m_texts_path and None == p_text_collection:
			self.m_texts_path = DickinsonCollection.data_folder + \
				DickinsonCollection.collections[p_corpus_name]

		# 2. Build object instances from the texts (if not passed in)
		self.__ingest(p_text_collection)

		# 3. Lexicon, a list of all unique words in all texts (only gathered if requested)
		self.m_lexicon = None

	# Generators

	# Path with files of extension p_file_extension. Name is used as an
	# identifier only.
	@classmethod
	def from_path(cls, p_texts_path, p_corpus_name, p_file_extension="tei"):
		return cls(p_corpus_name,
				   p_texts_path=p_texts_path,
				   p_file_extension=p_file_extension)

	# Already built set of text objects. Name is used as an identifier only.
	@classmethod
	def from_collection(cls, p_collection, p_corpus_name, p_texts_path="", p_file_extension=""):
		return cls(p_corpus_name,
				   p_texts_path=p_texts_path,
				   p_file_extension=p_file_extension,
				   p_text_collection=p_collection)

	# Uses corpus name as identifier to load texts from
	# static DickinsonCollection.collections dictionary
	@classmethod
	def from_corpus_name(cls, p_corpus_name, p_file_extension="tei"):
		return cls(p_corpus_name, p_texts_path="", p_file_extension=p_file_extension)

	# Private methods

	def __build_lexicon(self):

		# 1. Get unique words from each text and merge them into one lexical list
		self.m_lexicon = list(itertools.chain.from_iterable([text.lexicon for text in self.m_texts]))

		# 2. De-duplicate and sort collection lexicon
		self.m_lexicon = list(set(self.m_lexicon))
		self.m_lexicon.sort()

	def __ingest(self, p_text_collection):

		# 1. Get DickinsonPoem objects from all files (presumably tei files)
		#    Or save collection reference if passed in.
		if None == p_text_collection:
			debug("Reading poems into memory from {0}....".format(self.m_texts_path))
			self.m_texts = [DickinsonPoem(text_filepath) for text_filepath in \
							glob.glob(self.m_texts_path + "*.{0}".format(self.m_file_extension))]
		else:
			self.m_texts = p_text_collection.list

		# 2. Create a dictionary keyed on manuscript id
		self.m_id_dict = { text.manuscript_id: [] for text in self.m_texts }
		for text in self.m_texts:
			self.m_id_dict[text.manuscript_id].append(text)

		# 3. Create a sort order for works by their numeric IDs from the manuscript ID
		self.m_numeric_id_order = [text.numeric_manuscript_id for text in self.m_texts]
		self.m_numeric_id_order.sort()
		self.m_numeric_to_manuscript_dict = { 
			str(text.numeric_manuscript_id): text.manuscript_id for text in self.m_texts
		}
		self.m_publication_order = [ self.m_numeric_to_manuscript_dict[str(numeric_id)] \
			for numeric_id in self.m_numeric_id_order ]

		# 4. Create a list of manuscripts with duplicate IDs (multiple editions of the same text)
		temp_id_list = []
		self.m_duplicate_ids = []
		for manuscript_id in self.m_publication_order:
			if manuscript_id not in temp_id_list:
				temp_id_list.append(manuscript_id)
			else:
				self.m_duplicate_ids.append(manuscript_id)

	# Operator overloads

	def __getitem__(self, p_manuscript_id):
		return self.m_id_dict[p_manuscript_id]

	def __len__(self):
		return len(self.m_texts)

	def __setitem__(self, p_manuscript_id, p_text_object):
		self.m_id_dict[p_manuscript_id] = p_text_object

	# Properties

	@property
	def corpus_name(self):
		return self.m_corpus_name
	@property
	def dict(self):
		return self.m_id_dict
	@property
	def duplicate_ids(self):
		return self.m_duplicate_ids
	@property
	def ids(self):
		return self.m_id_dict.keys()
	@property
	def list(self):
		return self.m_texts
	@property
	def lexicon(self):
		if None == self.m_lexicon:
			self.__build_lexicon()
		return self.m_lexicon
	@property
	def publication_order(self):
		return self.m_publication_order
	
	# Static methods and variables

	@staticmethod
	def get_tfidf_matrix(p_bow_vectors):

		transformer = TfidfTransformer(smooth_idf=True)
		tfidf = transformer.fit_transform(p_bow_vectors)

		return tfidf.toarray()

	# Relative collection paths
	data_folder = "{0}{1}..{1}data{1}dickinson{1}".format(os.getcwd(), os.sep)
	collections = {

		# Collections below are within data_folder

		# All works

		"all": "all{0}".format(os.sep),

		# Publications

		"bianchi_1914":  		   "curated{0}bianchi_1914{0}".format(os.sep),
		"franklin_1998": 		   "curated{0}franklin_1998{0}".format(os.sep),
		"higginson_todd_2nd_1891": "curated{0}higginson_todd_2nd_1891{0}".format(os.sep),
		"johnson_1955": 		   "curated{0}johnson_1955{0}".format(os.sep),
		"todd_3rd_1896": 		   "curated{0}todd_3rd_1896{0}".format(os.sep),
		"todd_higginson_1890": 	   "curated{0}todd_higginson_1890{0}".format(os.sep),
		"todd_letters_1894": 	   "curated{0}todd_letters_1894{0}".format(os.sep),
	}

	metadata = ""

DickinsonCollection.metadata = DickinsonCollection.data_folder + "dickinson_poem_list.csv"


# Command line script (testing)

def main():

	# 0. Setup
	collection_name = "bianchi_1914"

	# 1. Create a collection of Dickinson works in memory
	collection = DickinsonCollection.from_corpus_name(collection_name)

if "__main__" == __name__:
	main()

# Built-ins
import glob    	   # File searching
import os   	   # Working directory and folder separator char

# Local
import aolm_string_utilities as asu
from dickinson_poem import DickinsonPoem

# Debug messaging
import my_logging
from my_logging import logging
from my_logging import tqdm
debug = logging.debug
# logging.disable(logging.DEBUG) # Comment out to enable debug messages


class DickinsonCollection:

	def __init__(self, p_texts_path, p_corpus_name, p_file_extension="tei", p_text_collection=None):

		# 0. Save parameters
		self.m_texts_path = asu.format_path(p_texts_path)	# Path to text files
		self.m_file_extension = p_file_extension			# Expected file extension of the text files
		self.m_corpus_name = p_corpus_name					# String name of the corpus

		# 1. Build object instances from the texts (if not passed in)
		self.__ingest(p_text_collection)

	def __ingest(self, p_text_collection):

		# 1. Get DickinsonPoem objects from all files (presumably tei files)
		#    Or save collection reference if passed in.
		if None == p_text_collection:
			debug("Reading poems into memory....")
			self.m_texts = [DickinsonPoem(text_filepath) for text_filepath in \
							glob.glob(self.m_texts_path + "*.{0}".format(self.m_file_extension))]
		else:
			self.m_texts = p_text_collection.list

		# 2. Create a dictionary keyed on manuscript id
		self.m_id_dict = { text.manuscript_id: text for text in self.m_texts }


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
	def ids(self):
		return self.m_id_dict.keys()
	@property
	def list(self):
		return self.m_texts

	@staticmethod
	def get_tfidf_matrix(p_bow_vectors):

		transformer = TfidfTransformer(smooth_idf=True)
		tfidf = transformer.fit_transform(p_bow_vectors)

		return tfidf.toarray()


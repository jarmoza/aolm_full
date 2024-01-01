# Author: Jonathan Armoza
# Creation date: March 18, 2021
# Last Updated: March 18, 2021
# Purpose: Line matching algorithms

# Built-ins
import math

class LineMatch(object):

	# Match methods

	@staticmethod
	def firstword_or_nothing(p_line1, p_line2):

		pass

	@staticmethod
	def allngram_iterative_search(p_line1, p_line2):

		# 1. Build list of ngrams in each line
		pass

	# Character overlap matching

	@staticmethod
	def jaccard_measure(p_line1, p_line2):

		# 1. Get unique characters of each line
		line1_chars = set(p_line1)
		line2_chars = set(p_line2)

		# 2. Compute intersection of those characters
		intersection_length = len(intersection(line1_chars, line2_chars))

		# 3. Compute union of those characters
		union_length = len(union(line1_chars, line2_chars))

		# 4. Return Jaccard measure: intersection length divided by union length
		return intersection_length / union_length

	# Utility methods

	@staticmethod
	def tf_idf(p_terms, p_all_tokens, p_documents_with_term, p_all_documents):

		# 1. Calculate the term frequency
		term_frequency = p_terms / p_all_tokens

		# 2. Calculate the inverse document frequency
		inverse_document_frequency = math.log(p_all_documents / p_documents_with_term)

		# 3. Return tf-idf value
		return term_frequency * inverse_document_frequency

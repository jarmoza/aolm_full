# Author: Jonathan Armoza
# Creation date: March 17, 2021
# Last Updated: March 17, 2021
# Purpose: Reads in poems of differing formats/sources and makes various kinds
# of comparisons between them

class PoemComparer(object):

	# Constructor

	def __init__(self):

		self.m_poem_lists = {}
		self.m_comparison_method = None

	# Public methods

	def compare(self, p_poem_object1, p_poem_object2, p_options=None, p_comparison_method=None):

		# 0. Comparison method defaults to assigned method if not given
		comparison_method = p_comparison_method if p_comparison_method else self.m_comparison_method

		# 1. String comparison methods
		expected_percent_match = 100
		if p_options:
			try
				expected_percent_match = p_options["expected_percent_match"]
			except:
				print("Error: Percent match not found in title_compare() options...")


	# Static methods

	# Comparison methods

	@staticmethod
	def title_compare(self, p_poem_object1, p_poem_object2, p_options=None):

		return PoemComparer.percent_line_match(p_poem_object1.title, p_poem_object2.title)

	# Utility methods

    @staticmethod
    def percent_line_match(p_original_line, p_compared_line):

    	# 0. Clean lines of white space and split into separate tokens for comparison
        line_words = p_original_line.strip().split(" ")
        compared_line_words = p_compared_line.strip().split(" ")

        # 0. Save word counts of each line
        line_word_count = len(line_words)
        compared_line_word_count = len(compared_line_words)

        # 1. Try to find an initial word match
        match_index = -1
        for index in range(line_word_count):
            if index < compared_line_word_count and line_words[index] == compared_line_words[index]:
                match_index = index
                break

        # If no beginning to matching sequence found, return 0% similarity
        if -1 == match_index:
            return 0

        # 2. Count all word matches that follow the initial word match
        matches = 0
        for index in range(match_index, line_word_count):
            if index < compared_line_word_count and line_words[index] == compared_line_words[index]:
                matches += 1

        # Return percentage match (re: the above match rules) of compared line with original line
        return float(matches) / float(line_word_count)


		





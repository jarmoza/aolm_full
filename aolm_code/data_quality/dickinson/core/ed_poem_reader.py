"""
Author: Jonathan Armoza
Creation date: May 25, 2021
Last Updated: May 25, 2021
Purpose: Base reader object that allows Emily Dickinson poems to be read from
         multiple types of sources
"""


class PoemReader(object):

	# Private methods

	def __init__(self, p_filepath, p_source_map):

		self.m_filepath = p_filepath
		self.m_source_map = p_source_map

		self.m_frequency_table = None
		self.m_poems = []
		

	def _source_to_objects(self):
		pass

	def _tally_word_frequencies(self):

		# 0. Keep track of word frequencies and the works words appear in
		frequency_dict = {}
		works_dict = {}
		works_tallies = {}

		# 1. Tally word counts in all poems and attribute them to their works
		for poem in self.m_poems:
			
			for line in poem.lines:

				# A. Get cleaned words from line (exclude blank strings)
				words = [PoemBookReader.clean_word(word) for word in line.strip().split(" ")]
				words = list(filter("".__ne__, words))
				
				# B. Count words in frequency table
				for word in words:

					# I. Increment frequency count
					if word not in frequency_dict:
						frequency_dict[word] = 0
					frequency_dict[word] += 1

					# II. Note word occurring in this poem
					if poem.title not in works_dict:
						works_dict[poem.title] = []
					if word not in works_dict[poem.title]:
						works_dict[poem.title].append(word)

		# 2. Tally number of works each word appears in
		for word in frequency_dict:
			for title in works_dict:
				if word in works_dict[title]:
					if word not in works_tallies:
						works_tallies[word] = 0
					works_tallies[word] += 1

		# 3. Return frequency table with frequency and works tally
		return [[word, frequency_dict[word], works_tallies[word]] for word in frequency_dict]


	# Properties

	@property
	def frequency_table(self):
		if None == self.m_frequency_table:
			self.m_frequency_table = self._tally_word_frequencies()
		return self.m_frequency_table	

	@property
	def poems(self):
		return self.m_poems

	@property
	def source(self):
		return self.m_source
	

	# Public methods

	def frequency_table_to_file(self, p_filepath):

		# 0. Get frequency table
		frequency_table = self.frequency_table

		# 1. Write frequency table to given file
		with open(p_filepath, "w") as output_file:

			# A. Write header
			output_file.write("token,count,works\n")

			# B. Write out token frequency data
			for token in frequency_table:
				output_file.write("\"{0}\",{1},{2}\n".format(token[0], token[1], token[2]))	

	def read(self):
		pass
	





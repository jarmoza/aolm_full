
# Imports

# Built-ins
from collections import Counter
import glob
from itertools import chain
import os
import re
import string

# Third party
from bs4 import BeautifulSoup
from tqdm import tqdm

# NOTE: Requires spacy pip installation and python -m spacy download en_core_web_sm
# import spacy


class EDAPoem:

	def __init__(self, p_filepath):

		# Parse file path
		self.m_file = {}
		self.m_file["path"] = p_filepath
		self.m_file["folder"] = os.path.dirname(self.m_file["path"])
		self.m_file["name"] = os.path.basename(self.m_file["path"])
		self.m_file["extension"] = os.path.splitext(os.path.basename(self.m_file["path"]))[1]

		# Create BeautifulSoup object based on TEI file		
		self.__init_soup()

		# Create stanza, line, and string representations of poem
		self.__get_full_text()

		# Properties from TEI file
		self.m_publication_statement = self.__m_soup.tei.publicationstmt.p.string.strip()		
		self.__get_publication_date()
		self.m_title = self.__m_soup.tei.titlestmt.title.string.strip()
		self.__get_manuscript_id()

		# Bag of words-related fields (computed and stored only upon request)
		self.m_bow = None
		self.m_colletion_bow_vector = None


	# Internal functions

	def __compute_bow(self):

		# 1. Determine counts of all words
		# (not including tokens that are solely punctuation)
		word_dict = {}
		for line in self.m_lines:
			line_words = line[1]
			for item in line_words:
				# All items that are solely punctuation are disregarded
				if item in string.punctuation:
					continue
				if item not in word_dict:
					word_dict[item] = 0
				word_dict[item] += 1

		return word_dict	  

	def __get_full_text(self):

		# 1. Parse stanzas from TEI
		self.__get_stanzas()

		# 2. Aggregate full text from stanzas in a single, endline-delimited string
		self.m_full_text = "\n".join(list(chain.from_iterable(self.m_stanzas)))

		# 3. Create a line by line list of the poem
		self.__get_lines()

	def __init_soup(self):

		self.__m_soup = BeautifulSoup(open(self.m_file["path"], "rU"), features="html.parser")

	def __get_lines(self):

		# self.m_lines = [re.sub(r"[\n]+", "\n", self.full_text).split("\n")]
		text_split_by_line = self.full_text.split("\n")

		self.m_lines = []
		for index in range(len(text_split_by_line)):
			self.m_lines.append([text_split_by_line[index]])
		for index in range(len(self.m_lines)):
			
			self.m_lines[index].append(self.tokenize_line(self.m_lines[index][0]))
			
			# self.m_lines[index].append(self.m_lines[index][0].strip().split(" "))

			# spacy_tokenized_line = DickinsonPoem.nlp(self.m_lines[index][0].strip())
			# self.m_lines[index].append([token.text for token in spacy_tokenized_line])

	def __get_manuscript_id(self):

		# 0. Default manuscript ID will be "N/A"
		self.m_manuscript_id = "N/A"

		# 1. Get all div tags
		div_tags = self.__m_soup.tei.find_all("div")

		# 2. Look for manuscript ID
		# ex. <div type="transcript" id="F752A">
		for tag in div_tags:

			if "type" in tag.attrs and tag.attrs["type"] == "transcript" and \
			   "id" in tag.attrs:
			   self.m_manuscript_id = tag.attrs["id"]

		# 3. Retrieve the numeric manuscript ID
		self.m_numeric_manuscript_id = DickinsonPoem.get_numeric_id(self.m_manuscript_id)

	def __get_publication_date(self):

		last_comma = self.m_publication_statement.rfind(",")
		self.m_publication_date = self.m_publication_statement[last_comma + 1:].strip() if -1 != last_comma else "1"

	def __get_stanzas(self):

		# Stanzas are accessible in list form
		self.m_stanzas = []

		# BeautifulSoup identification for plain text within an 'l' tag
		poem_text_soupclass = "<class 'bs4.element.NavigableString'>"

		# 1. Get all lg tags (with attribute 'stanza') within the 'text' tags are considered stanzas
		lg_tags = self.__m_soup.tei.find_all("text")[0].div.find_all('lg')

		# 2. Gather all stanzas
		for tag in lg_tags:
			
			# Looking only at lg tags attributed to be a stanza
			if "type" in tag.attrs and tag["type"] == "stanza":
				
				# A. Add a new stanza, a list of lines
				self.m_stanzas.append([])

				# B. Find all lines in this 'lg' stanza tag
				l_tags = tag.find_all('l')
				
				# C. Add all lines to this stanza
				for index in range(len(l_tags)):

					# Thoughtfully collect line fragments in a list, later converted to string
					current_line_text = []
					for line_subpart in l_tags[index].contents:

						# Plain text (<class 'bs4.element.NavigableString'>)
						if poem_text_soupclass == str(type(line_subpart)):
							current_line_text.append(line_subpart.strip() + " ")
						# Emphasis tag (looks to be Dickinson-specific TEI)
						elif "em" == str(line_subpart.name):
							current_line_text.append(str(line_subpart.contents[0]) + " ")
						# Apparatus tag
						elif "app" == str(line_subpart.name):
							for tag in line_subpart.contents:
								# Alternate 'readings' (seems to be spelling, punctuation corrections)
								# Always listed within an apparatus emendation tag
								# The preference here is for the emendation version vs the (potentially-
								# errored) version within the adjacent 'lem' tag
								if "rdg" == tag.name and len(tag.contents) > 0:
									if poem_text_soupclass == str(type(tag.contents[0])):
										current_line_text.append(str(tag.contents[0]) + " ")
										break

					# Add this line to the current stanza
					self.m_stanzas[len(self.m_stanzas) - 1].append("".join(current_line_text).strip())


	# Properties

	@property
	def bow(self):
		# Compute and store bag of words if not yet done
		if not self.m_bow:
			self.m_bow = self.__compute_bow()
		return self.m_bow

	@property
	def collection_bow_vector(self):
		return self.m_colletion_bow_vector
	@collection_bow_vector.setter
	def collection_bow_vector(self, p_bow_vector):
		self.m_colletion_bow_vector = p_bow_vector

	@property
	def clean_title(self):
		return self.clean_line(self.title)

	@property
	def collection_id(self):
		collection_id = ""
		for index in range(len(self.m_manuscript_id)):
			if self.m_manuscript_id[index].isalpha():
				collection_id += self.m_manuscript_id[index]
		return collection_id  

	@property
	def file_extension(self):
		return self.m_file["extension"]	

	@property
	def file_folder(self):
		return self.m_file["folder"]

	@property
	def file_name(self):
		return self.m_file["name"]

	@property
	def file_path(self):
		return self.m_file["path"]

	@property
	def line_match_threshold(self):
		return DickinsonPoem.line_match_threshold
	@line_match_threshold.setter
	def line_match_threshold(self, p_threshold):
		DickinsonPoem.line_match_threshold = p_threshold

	@property
	def lines(self):
		return self.m_lines

	@property
	def manuscript_id(self):
		return self.m_manuscript_id

	@property
	def numeric_manuscript_id(self):
		return self.m_numeric_manuscript_id
		# return DickinsonPoem.get_numeric_id(self.m_manuscript_id)
	

	@property
	def title(self):
		return self.m_title
	@title.setter
	def title(self, p_title):
		self.m_title = p_title

	@property
	def poem_match_threshold(self):
		return DickinsonPoem.poem_match_threshold
	@poem_match_threshold.setter
	def poem_match_threshold(self, p_threshold):
		DickinsonPoem.poem_match_threshold = p_threshold	   

	@property
	def publication_date(self):
		return self.m_publication_date
	@publication_date.setter
	def publication_date(self, p_publication_date):
		self.m_publication_date = p_publication_date

	@property
	def publication_statement(self):
		return self.m_publication_statement
	@publication_statement.setter
	def publication_statement(self, p_publication_statement):
		self.m_publication_statement = p_publication_statement

	@property
	def full_text(self):
		return self.m_full_text
	@full_text.setter
	def full_text(self, p_text):
		self.m_full_text = p_text
	
	@property 
	def stanzas(self):
		return self.m_stanzas
	

	# Utility functions
	@staticmethod
	def tokenize_line(p_line):

		# 1. Make sure tokens are evenly spaced by one space character
		new_line = re.sub(r"\s+", " ", p_line)
		new_line = new_line.strip().split(" ")

		# 2. Clean each token in the line
		clean_tokens = []
		for token in new_line:

			# a. Remove whitespace around token and lowercase
			new_token = token.strip().lower()

			# b. Remove non-alphanumeric characters around token if token has alphanumeric characters
			has_alnum = False
			first_alnum_index = last_alnum_index = -1

			# c. Check for alphanumeric characters
			for index in range(len(new_token)):
				if new_token[index].isalnum():
					has_alnum = True
					first_alnum_index = index
					break

			# d. Remove non-alphanumeric characters if at least one alphanumeric character exists
			if has_alnum:
			
				# i. Look for last alphanumeric character
				for index in range(len(new_token) - 1,-1,-1):
					if new_token[index].isalnum():
						last_alnum_index = index
						break

				# ii. Produce a cleaned substring
				if first_alnum_index != last_alnum_index:
					
					possible_token = new_token[first_alnum_index:last_alnum_index + 1]

					# Check for commas (special case)
					for c in possible_token:
						if c in string.punctuation and c is not "'":
							possible_token = possible_token.replace(c, " ")
					possible_tokens = possible_token.split(" ")
					for token in possible_tokens:
						clean_tokens.append(token.strip())

				else:
					clean_tokens.append(new_token[first_alnum_index])
			# Else, all characters are non-alphanumeric
			else:
				clean_tokens.append(new_token)

		return [token for token in clean_tokens if len(token) > 0]


	def clean_line(self, line):

		# Lowercase
		clean_line = line.lower()

		# Clean remaining tags
		clean_line = re.sub(r"<[^>]*>", " ", clean_line)

		# Clean any other non-alphanumeric character
		clean_line = "".join([char for char in clean_line if char not in string.punctuation])

		# Clean multi-spaces
		clean_line = " ".join([word for word in clean_line.split() if "" != word])

		return clean_line

	def convert_to_plaintext(self, p_output_directory, p_output_filename):

		with open(p_output_directory + p_output_filename, "w") as output_file:

			for stanza in self.stanzas:
				for line in stanza:

					# Clean tags
					output_line = re.sub(r"<[^>]*>", " ", line.replace("\n", "")) + "\n"

					# Write to plain text file
					output_file.write(str(output_line).encode("utf-8"))

	# NOTE: Needs re-implementation (J. Armoza 08/19/2019) 
	# Purpose: Consider more complex annotations made in the TEI files
	def get_formatted_stanzas(self, with_formatting=False, use_alternate_lines=False):

		#global add_types
		#global del_types
		poem_text_soupclass = "<class 'bs4.element.NavigableString'>"

		stanzas = []
		data = self.__m_soup.tei.find_all('text')[0].div.find_all('lg')
		for tag in data:
			
			if 'type' in tag.attrs and tag['type'] == 'stanza':
				
				stanzas.append([])
				current_stanza_index = len(stanzas) - 1
				l_tags = tag.find_all('l')
				
				for index in range(len(l_tags)):

					current_line_text = ''
					
					for line_subpart in l_tags[index].contents:
						if poem_text_soupclass == str(type(line_subpart)):
							current_line_text += line_subpart.strip() + ' '
						elif 'em' == str(line_subpart.name):
							current_line_text += str(line_subpart.contents[0]) + ' '
						elif 'app' == str(line_subpart.name):
							for tag in line_subpart.contents:
								if 'rdg' == tag.name and len(tag.contents) > 0:
									if poem_text_soupclass == str(type(tag.contents[0])):
										current_line_text += str(tag.contents[0]) + ' '
										break

					stanzas[current_stanza_index].append(current_line_text.strip())

					#app_tags = l_tags[index].find_all('app')
					#if l_tags[index].find_all('add'):
					#	for add in l_tags[index].find_all('add'):
					#		#print(add)
					#		if add['type'] not in add_types:
					#			add_types[add['type']] = ''
					#if l_tags[index].find_all('del'):
					#	for deltag in l_tags[index].find_all('del'):
					#		#print(deltag)
					#		if deltag['type'] not in del_types:
					#			del_types[deltag['type']] = ''
					#if with_formatting:
					#	if app_tags and app_tags[0]['type'] == 'division':
					#		stanzas[current_stanza_index].append('\n')
		return stanzas		  


	# Debug

	def print_stats(self):

		print("==============================")
		print("Title: {0}".format(self.title))
		print("Manuscript ID: {0}".format(self.manuscript_id))
		print("Filename: {0}".format(self.file_name))
		print("Publication statement: {0}".format(self.publication_statement))
		print("Publication date: {0}".format(self.publication_date))
		print("==============================")


	# Static fields and functions		

	# Static DickinsonPoem thresholds for similarity testing
	line_match_threshold = 0.75
	poem_match_threshold = 0.75

	# Spacy object for tokenization, NLP functions
	# nlp = spacy.load("en_core_web_sm")

	@staticmethod
	def clean_folder(p_folder_name):

		if len(p_folder_name) and os.sep != p_folder_name[len(p_folder_name) - 1]:
			return p_folder_name + os.sep
		return p_folder_name

	@staticmethod
	def bow_vectors_for_collection(p_poems):

		# 1. Get all bags of words for the poems and construct an overall word list
		all_words = []
		for poem in p_poems:

			# a. Get bag of words for this poem
			bow = poem.bow

			# b. Save all its words
			all_words += bow.keys()

		# 2. Save a lowercase, sorted list of all unique words
		all_words = list(set([word.lower() for word in all_words]))
		all_words.sort()

		# 3. Create vectors that will store all counts for each poem
		# with respect to the entire given collection (a list of lists)
		all_bow_vectors = []
		for poem in p_poems:

			# a. Blank bow vector
			bow_vector = []
			for word in all_words:

				# i. Determine the number of times the word occurs in the poem
				poem_word_count = 0 if word not in poem.bow else poem.bow[word]

				# ii. Add the entry to the poem's full collection bow vector
				bow_vector.append([word, poem_word_count])

			# b. Store the bow vector in the poem
			poem.collection_bow_vector = bow_vector

			# c. Save bow vector for returning in list of bow vectors
			all_bow_vectors.append(bow_vector)

		return all_bow_vectors

	@staticmethod
	def bow_vector_from_bow_tuple_list(p_tuple_list):

		bow_dict = {}
		for word_tuple in p_tuple_list:
			bow_dict[word_tuple[0]] = word_tuple[1]
		return bow_dict

	@staticmethod
	def get_numeric_id(p_nonnumeric_id):

		temp_manuscript_id = ""
		for index in range(len(p_nonnumeric_id)):
			if 0 == index and p_nonnumeric_id[index].isalpha():
				continue
			if p_nonnumeric_id[index].isdigit():
				temp_manuscript_id += p_nonnumeric_id[index]
			else:
				break

		if 0 == len(temp_manuscript_id):
			print("Original ID: {0} becomes zero length".format(p_nonnumeric_id))

		return temp_manuscript_id		   

	@staticmethod
	def is_poem_similar(original_poem, compared_poem):

		# 0. Get poem lines and line counts
		my_lines = original_poem.lines
		compared_lines = compared_poem.lines
		my_lines_count = len(my_lines)
		compared_lines_count = len(compared_lines)

		# 1. Look for the first highly similar match
		match_index = -1
		for index in range(my_lines_count):
			if index < compared_lines_count and DickinsonPoem.percent_line_match(my_lines[index], compared_lines[index], True) > DickinsonPoem.line_match_threshold:
				match_index = index
				break

		# If there are no similar line matches, poems are either different or very dissimilar
		if -1 == match_index:
			return False

		# 2. Count the remaining matches
		matches = 0
		for index in range(match_index, my_lines_count):
			if index < compared_lines_count and DickinsonPoem.percent_line_match(my_lines[index], compared_lines[index], True) > DickinsonPoem.line_match_threshold:
				matches += 1

		# If there is a significant amount of similar lines, then the poems are considered similar
		return float(matches) / float(my_lines_count) > DickinsonPoem.poem_match_threshold

	@staticmethod
	def is_poem_similar_bow(p_first_poem, p_second_poem, p_requested_percent=0.9):

		# 0. Get poem words
		compared_poems = [p_first_poem, p_second_poem]
		compared_words = []
		overall_word_count = 0
		for index in range(len(compared_poems)): 
			word_dict = {}
			for line in compared_poems[index].lines:
				# line_words = line.strip().split(" ")
				line_words = line[1]
				for item in line_words:

					# All items that are solely punctuation are disregarded
					if item in string.punctuation:
						continue

					overall_word_count += 1

					if item not in word_dict:
						word_dict[item] = 0

					word_dict[item] += 1

			compared_words.append(word_dict)

		# 1. Count the number of matches (re: bag of words)
		match_count = 0
		for item in compared_words[0]:
			if item in compared_words[1]:
				match_count += compared_words[0][item] + \
							   compared_words[1][item]

		# 2. Percentage of poem words that match from a bag of words perspective
		percent_match = float(match_count) / overall_word_count


		return percent_match >= p_requested_percent



	@staticmethod
	def compare_collection_titles(p_tei_folder, p_collection_id1, p_collection_id2):

		collection1 = []
		collection2 = []
		matched_titles = []

		# Format folder name
		p_tei_folder = DickinsonPoem.clean_folder(p_tei_folder)

		# Create DickinsonPoem objects from each TEI file and see if they are in either collection
		print("Gathering poems...")
		for tei_filename in glob.glob(p_tei_folder + "*.tei"):

			poem = DickinsonPoem(tei_filename)

			if p_collection_id1 == poem.collection_id:
				collection1.append(poem)
			elif p_collection_id2 == poem.collection_id:
				collection2.append(poem)

		for poem in collection1:
			for poem2 in collection2:
				if DickinsonPoem.percent_line_match(poem.title, poem2.title) > DickinsonPoem.line_match_threshold:
					matched_titles.append(poem.title)

		matched_titles.sort()
		for title in matched_titles:
			print(title)

	@staticmethod
	def percent_line_match(p_original_line, p_compared_line, p_prepared_line=False):

		line_words = None
		compared_line_words = None

		# 0. Make sure we are comparing lists of words
		# NOTE: If this is a prepared line it is an array sized 2,
		# array[0] is the line, array[1] is the array of the line's words
		if p_prepared_line:
			line_words = p_original_line[1]
			compared_line_words = p_compared_line[1]
		else:
			line_words = p_original_line.strip().split(" ")
			compared_line_words = p_compared_line.strip().split(" ")

		# Save word counts of each line
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

	@staticmethod
	def show_poems_by_collection_id(p_tei_folder):

		all_poems = []
		manuscript_collections = {}

		# Format folder name
		p_tei_folder = DickinsonPoem.clean_folder(p_tei_folder)

		# Create DickinsonPoem objects from each TEI file and tally their collection IDs
		print("Gathering poems and their collection IDs...")
		for tei_filename in glob.glob(p_tei_folder + "*.tei"):

			poem = DickinsonPoem(tei_filename)
			
			if poem.collection_id not in manuscript_collections:
				manuscript_collections[poem.collection_id] = 0
			manuscript_collections[poem.collection_id] += 1

		print("Manuscript Collections:\n{0}".format(manuscript_collections))

	@staticmethod
	def show_poems_by_publication_date(p_tei_folder):

		all_poems = []
		publication_dates = {}

		# Format folder name
		p_tei_folder = DickinsonPoem.clean_folder(p_tei_folder)

		# Create DickinsonPoem objects from each TEI file and tally their publication dates
		print("Gathering poems and their publication dates...")
		for tei_filename in glob.glob(p_tei_folder + "*.tei"):

			poem = DickinsonPoem(tei_filename)
			
			if poem.publication_date not in publication_dates:
				publication_dates[poem.publication_date] = 0
			publication_dates[poem.publication_date] += 1

		print("Publication dates:\n{0}".format(publication_dates))

	@staticmethod
	def show_poems_by_publication_info(p_tei_folder):

		all_poems = []
		collection_ids = {}

		# Format folder name
		p_tei_folder = DickinsonPoem.clean_folder(p_tei_folder)

		# Create DickinsonPoem objects from each TEI file and tally their publication info
		print("Gathering poems and their publication info...")
		for tei_filename in glob.glob(p_tei_folder + "*.tei"):

			poem = DickinsonPoem(tei_filename)
			
			if poem.collection_id not in collection_ids:
				collection_ids[poem.collection_id] = {}
			if poem.publication_statement not in collection_ids[poem.collection_id]:
				collection_ids[poem.collection_id][poem.publication_statement] = 0
			collection_ids[poem.collection_id][poem.publication_statement] += 1

		for key in collection_ids:
			print("=================================================")
			print("ID: {0}".format(key))
			print("Publication statements:\n{0}".format(collection_ids[key])	   )

	@staticmethod
	def show_collection_titles(p_tei_folder, p_collection_id):

		all_poems = []
		titles = []

		# Format folder name
		p_tei_folder = DickinsonPoem.clean_folder(p_tei_folder)

		# Create DickinsonPoem objects from each TEI file and collect their titles for a collection
		print("Gathering titles for collection {0}...".format(p_collection_id))
		for tei_filename in glob.glob(p_tei_folder + "*.tei"):

			poem = DickinsonPoem(tei_filename)
			
			if p_collection_id == poem.collection_id:
				titles.append(poem.title)

		# Sort titles alphabetically
		titles.sort()

		for title in titles:
			print(title)

	@staticmethod
	def gather_poems(p_tei_folder, p_txt_folder, p_publication_date="N/A", p_collection_id="N/A", p_similarity_comparison=True, p_remove_old_plaintext=False):

		# 0. Setup	  

		# Format folder names
		p_tei_folder = DickinsonPoem.clean_folder(p_tei_folder)
		p_txt_folder = DickinsonPoem.clean_folder(p_txt_folder)

		# Option only for testing purposes (cleans out errored TEI->TXT transformations)
		if p_remove_old_plaintext:
			
			print("Removing old plaintext files...")

			# Clear all files in the plain text directory
			for old_file in os.listdir(p_txt_folder):
				file_path = os.path.join(p_txt_folder, old_file)
				try:
					if file_path.endswith(".txt") and os.path.isfile(file_path):
						os.unlink(file_path)
				except Exception as e:
					print(e)

		# 1. Create DickinsonPoem objects from each TEI file
		# (and flag them as not yet written to the txt folder)
		print("Gathering poems into memory...")
		all_poems = []
		for tei_filename in glob.glob(p_tei_folder + "*.tei"):
			all_poems.append([DickinsonPoem(tei_filename), False])

		print("Filtering poems...")

		# 2. Filter poems by publication date or collection ID if requested
		if "N/A" != p_publication_date:
			for index in range(len(all_poems)):
				if p_publication_date != all_poems[index][0].publication_date:
					all_poems[index][1] = True
		if "N/A" != p_collection_id:
			for index in range(len(all_poems)):
				if p_collection_id != all_poems[index][0].collection_id:
					all_poems[index][1] = True					

		# 3. Compare all poems to determine similarity matches and filter similar ones out of final corpus
		write_count = 0
		for index in range(len(all_poems)):

			# Skip poems pre-flagged by publication date filtering
			if all_poems[index][1]:
				continue

			# Keep track of how many poems have been written to the txt folder
			write_count += 1

			# A. Gather all similar poems, if requested
			similar_poems = [index]
			if p_similarity_comparison:
				
				print("Comparing poems...")

				for index2 in range(len(all_poems)):

					# Skip comparisons to self or poems flagged by publication date filtering
					if index == index2 or all_poems[index2][1]:
						continue

					# Compare two poems for line-based similarity,
					# If so, add compared poem to the similar poem list
					if DickinsonPoem.is_poem_similar(all_poems[index][0], all_poems[index2][0]):
						similar_poems.append(index2)

			# B. If poems are similar by this criteria then determine which one to write out
			if len(similar_poems) > 1:

				#print("Found {0} similar poems".format(len(similar_poems)))

				# NOTE: Separate case, to leave space for future more complex similarity filtering criteria
				# J. Armoza (08/19/2019)

				# i. Default to using the original poem
				poem_to_write_index = similar_poems[0]
				
				# ii. Write out poem in plain text to the txt folder (skipping the other similar poems)
				txt_filename = os.path.splitext(all_poems[poem_to_write_index][0].file_name)[0] + ".txt" 
				all_poems[poem_to_write_index][0].convert_to_plaintext(p_txt_folder, txt_filename)

				# iii. Flag poem as written to the txt folder (and flag similar poems as written as well)
				for poem_index in similar_poems:
					all_poems[poem_index][1] = True
			# Else, just write out the poem
			else:
				poem_to_write_index = similar_poems[0]
				txt_filename = os.path.splitext(all_poems[poem_to_write_index][0].file_name)[0] + ".txt" 
				all_poems[poem_to_write_index][0].convert_to_plaintext(p_txt_folder, txt_filename)
				all_poems[poem_to_write_index][1] = True

		print("Wrote {0} poems to {1}".format(write_count, p_txt_folder))


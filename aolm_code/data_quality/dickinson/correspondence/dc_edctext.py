# Author: Jonathan Armoza
# Project: Art of Literary Modeling
# Date: June 4, 2019

from collections import Counter
import datetime
import os
import string

from bs4 import BeautifulSoup
from bs4 import element
from tqdm import tqdm


class EDCText(object):

	def __init__(self, p_filepath, p_parser_type="html.parser"):

		self.m_filepath = p_filepath
		self.m_parser_type = p_parser_type
		self.m_soup = None
		self.__ingest()

		# Information about this text

		# Title(s)
		self.m_titles = self.__titles()

		# Line count
		self.__calculate_line_count()

		# Editor-assigned type
		self.m_editor_assigned_type = self.__editor_assigned_type()

		# Words
		self.m_body_words = self.__body_words()

		# Bag of words vector should be assigned externally
		self.m_bow_vector = None

	# Private functions

	def __body_words(self):

		body_words = []

		for index in range(1):
			div_tags = self.m_soup.find_all("div{0}".format(index))
			for div_tag in div_tags:
				for child_tag in div_tag.descendants:
					if not isinstance(child_tag, element.NavigableString):
						text_tokens = EDCText.tokenize(child_tag.text)
						for token in text_tokens:
							body_words.append(token)

		return body_words

	def __ingest(self):

		# Read table of contents html and transform into beautiful soup
		with open(self.m_filepath, "r") as dc_file:
			self.m_soup = BeautifulSoup(dc_file.read(), self.m_parser_type)

	def __calculate_line_count(self):

		self.m_line_count = EDCText.default_na

		# No soup? No line count for you!
		if not self.m_soup:
			return

		# Count of all l tags under text tag
		self.m_line_count = 0
		text_tag = self.m_soup.find("text")
		body_tag = text_tag.find("body")
		div_tags = body_tag.find_all("div0")
		for div in div_tags:
			lg_tags = div.find_all("lg")
			for lg in lg_tags:
				self.m_line_count += len(lg.find_all("l"))

	def __editor_assigned_type(self):

		return self.m_soup.find("text").find("body").find("div0")["type"]

	def __titles(self):

		# 1. Get title tags in title statement
		title_tags = self.find_all_tags_in_tag("titlestmt", "title")

		return [title_tag.text for title_tag in title_tags]


	# Properties

	@property
	def body_words(self):
		return self.m_body_words
	
	@property
	def bow_vector(self):
		return self.m_bow_vector
	def create_bow_vector(self, p_lexicon, p_top_words="all"):

		# 1. Tally unique tokens in this text
		self.m_bow_vector = [0] * len(p_lexicon)
		body_words_counter = Counter(self.m_body_words)
		
		# 2. Create a vector with entries counting the words in this text for the given lexicon
		for index in range(len(p_lexicon)):
			if p_lexicon[index] in body_words_counter:
				self.m_bow_vector[index] = body_words_counter[p_lexicon[index]]

		# 3. Return only the top N words, if requested
		if "all" != p_top_words:
			self.m_bow_vector = self.m_bow_vector[0:p_top_words]


	@property
	def editor_assigned_type(self):
		return self.m_editor_assigned_type

	@property
	def filepath(self):
		return self.m_filepath
	
	@property
	def line_count(self):
		return self.m_line_count

	@property
	def start_date(self):
		return self.m_start_date
	@start_date.setter
	def start_date(self, p_start_date):
		self.m_start_date = EDCText.format_date(p_start_date)
	def start_date_continuous(self):
		return EDCText.datetime_continuous(self.start_date)

	@property
	def end_date(self):
		return self.m_end_date
	@end_date.setter
	def end_date(self, p_end_date):
		self.m_end_date = EDCText.format_date(p_end_date)
	def end_date_continuous(self):
		return EDCText.datetime_continuous(self.end_date)

	@property
	def title(self):
		return " | ".join(self.m_titles)
	

	# Primary functions

	def stats(self):

		print("Title: {0}".format(self.title))
		print("Lines: {0}".format(self.line_count))
		print("Editor-assigned Type: {0}".format(self.editor_assigned_type))

	def all_tags(self, p_tag_name):

		return self.m_soup.find_all(p_tag_name)

	def first_tag(self, p_tag_name):

		return self.m_soup.find(p_tag_name)

	def find_all_tags_in_tag(self, p_parent_tagname, p_child_tagname):

		return self.m_soup.find(p_parent_tagname).find_all(p_child_tagname)

	# Static members

	default_tei_filepath = os.getcwd() + "{0}..{0}correspondences{0}tei{0}formatted{0}".format(os.sep)
	default_na = "N/A"
	# default_decade_colors = { "1850s": }

	@staticmethod
	def create_lexicon(p_edc_instances):

		edc_lexicon = []
		for text in tqdm(p_edc_instances):
			# print("Body words for {0}: {1}".format(text.title, text.body_words))
			edc_lexicon.extend(text.body_words)
		edc_lexicon = list(set(edc_lexicon))
		edc_lexicon.sort()

		return edc_lexicon

	@staticmethod
	def datetime_continuous(p_datetime):

		return float(p_datetime.year) + ((p_datetime.month - 1) / 12.0) + ((p_datetime.day - 1) / 365.0)

	@staticmethod
	def format_date(p_date_text, p_default_date=1800):

		# Strip whitespace first
		date_text = p_date_text.strip()

		# No date available
		if EDCText.default_na == date_text:
			return datetime.datetime(p_default_date, 1, 1)

		# YYYY-MM-DD
		if "-" in date_text:
			date_parts = date_text.split("-")
			return datetime.datetime(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
		# YYYY-01-01
		else:
			return datetime.datetime(int(date_text), 1, 1)

	@staticmethod
	def strip_punctuation(word):

		return "".join([c for c in word if c not in string.punctuation]).strip()

	@staticmethod
	def tokenize(p_line):

		# 1. Strip the line of whitespace
		p_line = p_line.strip()

		# 2. Strip leading/trailing punctuation
		p_line = EDCText.strip_punctuation(p_line)

		# 3. Strip the line of whitespace again
		p_line = p_line.strip()

		# 4. Split the line into tokens by internal whitespace
		p_line = p_line.replace("\n", " ")
		p_line = p_line.replace("\t", " ")
		line_tokens = p_line.split(" ")

		# 5. Strip tokens of leading/trailing punctuation
		for index in range(len(line_tokens)):
			line_tokens[index] = EDCText.strip_punctuation(line_tokens[index])

		# 6. Return all non-empty tokens in lowercase form
		return [token.lower() for token in line_tokens if "" != token]


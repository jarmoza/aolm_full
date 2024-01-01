# Author: Jonathan Armoza
# Purpose: Creates csv of all listed poem titles (first lines)
# Creation date: April 20, 2021
# Last updated: April 20, 2021


# Imports

# Built-in

import glob
import os

# Local

from dickinson_poem import DickinsonPoem


# Globals

eda_publications = {

	'The Single Hound,  Bianchi, 1914': [],
	'The Poems of Emily Dickinson, Variorum Edition, Franklin, 1998': [],
	'The Poems of Emily Dickinson, Johnson, 1955': [],
	'Poems by Emily Dickinson, Todd and Higginson, 1890': [],
	'Poems by Emily Dickinson: Second Series, Higginson and Todd, 1891': [],
	'Poems by Emily Dickinson: Third Series, Todd, 1896': []
}

subcorpus_filenames = {

	'The Single Hound,  Bianchi, 1914': "single_hound",
	'The Poems of Emily Dickinson, Variorum Edition, Franklin, 1998': "franklin",
	'The Poems of Emily Dickinson, Johnson, 1955': "johnson",
	'Poems by Emily Dickinson, Todd and Higginson, 1890': "first_series",
	'Poems by Emily Dickinson: Second Series, Higginson and Todd, 1891': "second_series",
	'Poems by Emily Dickinson: Third Series, Todd, 1896': "third_series" 
}

paths = {
	
	"data": "{0}{1}..{1}..{1}..{1}..{1}data{1}dickinson{1}".format(os.getcwd(), os.sep),
	"output": "{0}{1}output{1}".format(os.getcwd(), os.sep)
}

text_locations = {
	
	"bolts_first_lines": "{0}bingham{1}raw{1}".format(paths["data"], os.sep) + \
			 "bolts_index_of_first_lines_raw.txt",
	"ed_archive": "{0}eda{1}tei{1}".format(paths["data"], os.sep)
}

# Utility functions

def clean_string(p_unformatted_string):

	formatted_string = p_unformatted_string.lower().strip()

	return formatted_string


# Primary functions

def compare_titles(p_collection1, p_collection2, p_comparison_fn=None):

	matched_titles = []
	unmatched_titles = []

	for collection1_title in p_collection1:

		collection1_title = clean_string(collection1_title)

		for collection2_title in p_collection2:

			collection2_title = clean_string(collection2_title)

			if None == p_comparison_fn:
				if collection1_title == collection2_title:
					matched_titles.append(collection1_title)
			else:
				if p_comparison_fn(collection1_title, collection2_title):
					matched_titles.append(collection1_title)
		
		if collection1_title not in matched_titles:
			unmatched_titles.append(collection1_title)

	return matched_titles, unmatched_titles


def read_bolts_poem_titles():

	bolts_poem_titles = []

	with open(text_locations["bolts_first_lines"], "r") as first_lines_file:

		# 1. Read all lines
		file_lines = first_lines_file.readlines()

		# 2. Save line as title if it meets this criteria
		for line in file_lines:

			# A. Strip line of whitespace and remove all numeric characters
			clean_line = line.strip()
			clean_list = []
			for ch in line:
				if not ch.isnumeric():
					clean_list.append(ch)
			clean_line = "".join(clean_list).strip()

			# B. Make sure line is a title
			contains_upper = False
			contains_lower = False			
			if len(clean_line):

				# I. Check for upper and lowercase characters
				for ch in clean_line:
					if ch.isupper():
						contains_upper = True
					elif ch.islower():
						contains_lower = True

				# II. Lines with upper and lowercase characters are titles to be saved
				if contains_upper and contains_lower:
					bolts_poem_titles.append(clean_line)

	# print(bolts_poem_titles)
	# print(len(bolts_poem_titles))	

	return bolts_poem_titles

def read_eda_poem_titles():

	return [DickinsonPoem(filepath).title for filepath in glob.glob(text_locations["ed_archive"] + "*")]

def read_eda_poem_objects():

	return [DickinsonPoem(filepath) for filepath in glob.glob(text_locations["ed_archive"] + "*")]

def output_subcorpus_titles(p_subcorpus_name, p_subcorpus_poems):

	with open(paths["output"] + subcorpus_filenames[p_subcorpus_name] + "_titles.csv", "w") as output_file:
		for poem in p_subcorpus_poems:
			output_file.write(poem.title + "\n")

# Main script

def main():

	# 1. Read poem titles from first and second collections
	bolts_poem_titles = read_bolts_poem_titles()
	eda_poems = read_eda_poem_objects()

	# 2. Fill out the poem map by publication
	for poem in eda_poems:
		eda_publications[poem.publication_statement].append(poem)

	# 3. Collection for comparison
	eda_subcorpus_name = 'The Poems of Emily Dickinson, Variorum Edition, Franklin, 1998'

	# for scn in subcorpus_filenames:
	# 	output_subcorpus_titles(scn, eda_publications[scn])

	# 4. Find titles in bolts that are also in subcorpus
	matched_titles, unmatched_titles = compare_titles(
		bolts_poem_titles, [poem.title for poem in eda_publications[eda_subcorpus_name]])

	# 5. Output mismatches to csv
	with open(paths["output"] + "unmatched_titles.csv", "w") as output_file:
		for title in unmatched_titles:
			output_file.write("\"{0}\"\n".format(title.strip()))

if "__main__" == __name__:
	main()


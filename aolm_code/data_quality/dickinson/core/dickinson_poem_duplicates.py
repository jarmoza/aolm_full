import glob
import os
import re
from shutil import copyfile # Copying files

from tqdm import tqdm
from dickinson_poem import DickinsonPoem

# Includes logging and loop progress debug functionality
from my_logging import logging

# Comment out to enable debug messages
# logging.disable(logging.DEBUG)

paths = { "aolm": os.getcwd() + os.sep + "..{0}..{0}..{0}".format(os.sep) }
paths["tei"] = paths["aolm"] + "datasets{0}dickinson{0}poems{0}tei{0}".format(os.sep)
paths["txt"] = paths["aolm"] + "datasets{0}dickinson{0}poems{0}txt{0}".format(os.sep)
paths["output"] = os.getcwd() + "{0}output{0}".format(os.sep)

def get_all_poems():

	# 1. Get all TEI filenames
	logging.debug("Gathering filenames....")
	filepaths = [tei_filepath for tei_filepath in glob.glob(paths["tei"] + "*")]
	
	# 2. Build poem objects
	poems = []
	logging.debug("Building poems in memory....")	
	for tei_filepath in tqdm(filepaths):
		poems.append(DickinsonPoem(tei_filepath))

	return poems

def get_collection_ids(p_poems):

	# 1. Create a dictionary of collection IDs and poem counts
	collection_id_dict = {}
	for poem in tqdm(p_poems):
		if poem.collection_id == "P":
			logging.debug(poem.manuscript_id)	
		if poem.collection_id not in collection_id_dict:
			collection_id_dict[poem.collection_id] = 0
		collection_id_dict[poem.collection_id] += 1

	return collection_id_dict

def find_duplicate_titles_across_collections(p_poems, p_match_percentage=0.5):

	# 1. Find all closely matching titles
	possible_duplicate_titles = {}
	logging.debug("Comparing poem titles....")
	for poem in tqdm(p_poems):
		for compared_poem in p_poems:
			if poem.manuscript_id != compared_poem.manuscript_id and \
			DickinsonPoem.percent_line_match(poem.title, compared_poem.title) > p_match_percentage:
				if poem.title not in possible_duplicate_titles:
					possible_duplicate_titles[poem.title] = []
				possible_duplicate_titles[poem.title].append((poem.manuscript_id, compared_poem.manuscript_id))
	for key in possible_duplicate_titles:
		possible_duplicate_titles[key] = list(set(possible_duplicate_titles[key]))

	return possible_duplicate_titles

def find_duplicate_poems_bow(p_poems, p_match_percentage=0.9):

	logging.debug("Comparing poems as bag of words (similarity threshold: {0})....".format(p_match_percentage))

	# 1. Find all closely matching poems (bag of words perspective)
	poem_matches = {}
	for poem in tqdm(p_poems):
		for poem2 in p_poems:
			if poem.manuscript_id != poem2.manuscript_id and \
			   DickinsonPoem.is_poem_similar_bow(poem, poem2, p_match_percentage):
				if poem.manuscript_id not in poem_matches:
					poem_matches[poem.manuscript_id] = []
				poem_matches[poem.manuscript_id].append(poem2.manuscript_id)

	return poem_matches

def copy_edition_poems_to_folder(p_poems, p_edition, p_output_folder, p_take_alternates=False):

	def str_contains_nonnum(p_str):
		for c in p_str:
			if not c.isdigit():
				return True
		return False

	# 1. Select poems based on edition and alternate request
	logging.debug("Filtering poems....")
	selected_poems = []
	selected_poem_numeric_ids = []
	for poem in tqdm(p_poems):
		if p_edition == poem.manuscript_id[0]:

			if not p_take_alternates:
				if "A" not in poem.manuscript_id and str_contains_nonnum(poem.manuscript_id[1:]):
					# logging.debug("Filtering out: {0}".format(poem.manuscript_id))
					continue
			selected_poems.append(poem)

			if poem.numeric_manuscript_id in selected_poem_numeric_ids:
				logging.debug("Duplicate of {0}".format(poem.numeric_manuscript_id))
			
			selected_poem_numeric_ids.append(poem.numeric_manuscript_id)

	# 2. Copy selected poem files to requested folder
	logging.debug("Copying filtered poems to {0}....".format(p_output_folder))
	for poem in tqdm(selected_poems):

		copyfile(poem.file_path, p_output_folder + poem.file_name)
		# logging.debug(poem.file_path)
		# logging.debug("New path: {0}{1}".format(p_output_folder, poem.file_name))
		# logging.debug("===================================")

def review_duplicate_titles(p_poems, p_collection_filter=None, p_match_percentage=None):

	def clean_manuscript_id(p_original_id):
		return re.sub(r"\[|\]|'| ", "", p_original_id)

	# 0. Create a poem dictionary keyed by manuscript ID
	poem_dict = {}
	for poem in p_poems:
		poem_dict[poem.manuscript_id] = poem

		copyfile(src, dst)

	# 1. Construct a (possible) duplicate poem dictionary
	logging.debug("Building poem duplicate dictionary from file...")
	poem_dupe_dict = {}
	with open(paths["output"] + "dickinson_possible_duplicates.csv", "r") as input_file:

		input_lines = input_file.readlines()

		# Each line is a composed of original manuscript ID + possible duplicate list
		# (Skips csv header)
		for index in tqdm(range(1, len(input_lines))):
			line = input_lines[index]
			line_parts = line.strip().split(",")
			manuscript_id = clean_manuscript_id(line_parts[0])
			poem_dupe_dict[manuscript_id] = []
			for index in range(1, len(line_parts)):
				poem_dupe_dict[manuscript_id].append(clean_manuscript_id(line_parts[index]))

	# 2. Look for identical and different titles

	logging.debug("Attempting to match poem titles...")

	# a. Title match threshold is optional
	requested_match_percent = 1 if not p_match_percentage else p_match_percentage

	# b. Create two dictionaries
	titles_avec_match = {}
	titles_sans_match = {}
	# print(poem_dupe_dict.keys())
	# print("=======================================")
	# print(poem_dict.keys())
	# print("=======================================")
	# print("Poem dupe dict: {0}\nPoem dict: {1}".format(len(poem_dupe_dict.keys()), len(poem_dict.keys())))
	for manuscript_id in tqdm(poem_dupe_dict):

		original_poem = poem_dict[manuscript_id]

		# Insert poem into both dictionaries
		titles_avec_match[manuscript_id] = []
		titles_sans_match[manuscript_id] = []

		for compared_id in poem_dupe_dict[manuscript_id]:

			compared_poem = poem_dict[compared_id]
		
			# i. Get title match percentage
			title_match_percent = DickinsonPoem.percent_line_match(original_poem.title,
																   compared_poem.title)

			# ii. Check match percentage against threshold
			# and insert compared manuscript ID into the appropriate dictionary
			if title_match_percent >= requested_match_percent:
				titles_avec_match[manuscript_id].append(compared_id)
			else:
				titles_sans_match[manuscript_id].append(compared_id)

	# 3. Output file indicating matches and mismatches by manuscript ID, title, and filename
	logging.debug("Generating poem title match and mismatch csv: {0}".format(
		paths["output"] + "dickinson_duplicates_filledout_list.csv"))
	with open(paths["output"] + "dickinson_duplicates_filledout_list.csv", "w") as output_file:

		# a. Write out csv header
		# manuscript ID, title, filename, matches [(manuscript ID, title, filename), ...],
		# mismatches [(manuscript ID, title, filename), ...]
		output_file.write("manuscript_id,title,filename,matches,mismatches\n")

		# b. Write a line of matches and mismatches for each manuscript ID
		for manuscript_id in tqdm(poem_dupe_dict):

			poem = poem_dict[manuscript_id]

			# Poems not thought to have duplicates in the corpus have no title matches/mismatches
			# if manuscript_id not in poem_dupe_dict:
			# 	output_file.write("{0},\"{1}\",{2},,\n".format(manuscript_id, poem.title, poem.file_name))
			# 	continue

			# Filter by collection if requested
			if p_collection_filter and manuscript_id[0] != p_collection_filter:
				continue

			# i. Gather title matches and mismatches
			matches = []
			for compared_id in titles_avec_match[manuscript_id]:
				if p_collection_filter and compared_id[0] != p_collection_filter:
					continue
				matches.append([compared_id,
								poem_dict[compared_id].title,
								poem_dict[compared_id].file_name])
			mismatches = []
			for compared_id in titles_sans_match[manuscript_id]:
				if p_collection_filter and compared_id[0] != p_collection_filter:
					continue				
				mismatches.append([compared_id,
								   poem_dict[compared_id].title,
								   poem_dict[compared_id].file_name])

			# ii. Write out information for each manuscript ID
			output_file.write("{0},\"{1}\",{2},".format(manuscript_id, poem.title, poem.file_name))
			match_parts = ["({0},{1},{2})".format(m[0],m[1],m[2]) for m in matches]
			match_str = "\"" + "|".join(match_parts) + "\""
			# print("Match parts: {0}".format(match_parts))
			# print("Match string: {0}".format(match_str))
			# print("========================================")			
			mismatch_parts = ["({0},{1},{2})".format(m[0],m[1],m[2]) for m in mismatches]
			mismatch_str = "\"" + "|".join(mismatch_parts) + "\""
			output_file.write("{0},{1}\n".format(match_str, mismatch_str))


def main():

	# 1. Gather all poems
	poems = get_all_poems()

	# 2. Find poem IDs
	# print(get_collection_ids(poems))

	# 2. Look for duplicate titles
	# print(find_duplicate_titles_across_collections(poems))
	
	# 2. Look for poems whose bag of words match each other by >= 90%
	# poem_matches = find_duplicate_poems_bow(poems, p_match_percentage=0.9)

	# 3. Write poem matches to a csv file
	# with open(paths["output"] + "dickinson_possible_duplicates.csv", "w") as output_file:
	# 	output_file.write("manuscript_id,matches\n")
	# 	for key in poem_matches:
	# 		output_file.write("{0},{1}\n".format(key, poem_matches[key]))

	# 2. Build full csv containing information on poem title matches and mismatches
	# review_duplicate_titles(poems, p_collection_filter='F', p_match_percentage=0.9)

	# 2. Create a filtered subcorpus of poems
	copy_edition_poems_to_folder(poems, "F", paths["output"] + "franklin_a" + os.sep)

if "__main__" == __name__:
	main()
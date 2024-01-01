# Imports

# Built-in

import os
import re
import string
import sys

# Third party
# import spacy
# spacy.load("en_core_web_sm")

# Local

from aolm_utilities import clean_word
from bingham_bolts import bolts_guide
from dickinson_poem import DickinsonPoem


# Globals

book_maps = {
	
	"bolts": bolts_guide
}

paths = {
	
	"data": "{0}{1}..{1}..{1}..{1}..{1}data{1}dickinson{1}".format(os.getcwd(), os.sep),
	"output": "{0}{1}output{1}".format(os.getcwd(), os.sep)
}




def main(p_text_id):

	# 0. Determine file location and book map
	text_location = text_locations[p_text_id]
	book_map = book_maps[p_text_id]

	# 1. Instantiate a poem reader
	reader = PoemBookReader(text_location, book_map)

	# 2. Read in poems
	reader.read_books()

	# 3. Print out information about book
	reader.print_stats()

	# 4. Save word frequencies to file
	# reader.frequency_table_to_file(paths["output"] + "bolts_frequency_table.csv")


if "__main__" == __name__:

	if len(sys.argv) == 1:
		print("Must specify text name. Current possible texts: [bolts]")
	else:
		main(sys.argv[1])
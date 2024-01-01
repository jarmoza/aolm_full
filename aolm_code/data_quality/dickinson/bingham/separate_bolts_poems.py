# Imports

# Built-ins
import os

# Local
from ed_bolts_reader import BoltsReader

# Read in bolts poems and separate them
bolts_folder = "..{0}..{0}..{0}data{0}dickinson{0}bingham{0}".format(os.sep)
bolts_processed_file = "bingham_bolts_of_melody_internetarchive_accessed021021_processed.txt"
bolts_processed_folder = "{0}processed{1}".format(bolts_folder, os.sep)
bolts_poems_folder = "{0}poems{1}".format(bolts_folder, os.sep)

# Save as text files in data/bingham/poems/
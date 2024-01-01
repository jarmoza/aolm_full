# Author: Jonathan Armoza
# Created: March 2, 2022
# Purpose: Keeps track of Art of Literary modeling notes on metadata of
#          digital editions of Mark Twain's 'The Adventures of Huckleberry Finn'


# =============================================================================
# Imports

# Standard libraries
import glob
import json
import os

# Local libraries
from utilities import aolm_paths


# =============================================================================
# Functions

def add_aolm_notes(p_metadata_json):

    # 1. Create a blank dictionary keyed by all of the metadata's keys
    p_metadata_json["aolm_notes"] = { key: "" for key in p_metadata_json }

    # 2. Return the original json with the new notes object
    return p_metadata_json


# =============================================================================
# Main script

def main():

    # 0. Setup code and data paths
    aolm_paths.setup_paths()
    json_folder = aolm_paths.data_paths["twain"]["internet_archive"] + "json" + os.sep

    # 1. Read in each json file in the input folder
    json_files = {}
    for json_filepath in glob.glob(json_folder + "*"):

        # A. Retrieve the filename
        filename = os.path.basename(json_filepath)

        # B. Read in the file as json
        with open(json_filepath, "r") as input_file:
            json_data = json.load(input_file)

        # C. Save the json file data in the dictionary
        json_files[filename] = json_data

    # 2. Add a blank notes dictionary keyed by all of each file's keys
    for filename in json_files:
        json_files[filename] = add_aolm_notes(json_files[filename])

    # 3. Write out the new version of the json
    for filename in json_files:
        output_filename = os.path.splitext(filename)[0] + "_notes.json"
        with open(json_folder + output_filename, "w") as output_file:
            json.dump(json_files[filename], output_file)

if "__main__" == __name__:
    main()

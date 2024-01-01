# Author: Jonathan Armoza
# Created: March 11, 2022
# Purpose: Programmatic comparison of metadata of all digital editions of
#          Mark Twain's 'The Adventures of Huckleberry Finn'

# Imports

# Standard libraries
from collections import Counter
import glob
from itertools import chain
import json
import os

# Local libraries
from utilities import aolm_paths
from utilities.aolm_utilities import debug_separator

# Initialize all paths for use
aolm_paths.setup_paths()

# Helper functions

def get_metadata_commons(p_metadata_collection):

    # 0. Stores common keys and values
    commons = {}

    # 1. Look for common keys
    key_names = []
    for filename in p_metadata_collection:
        key_names.extend(p_metadata_collection[filename].keys())

    # 2. Count keys
    key_counter = Counter(key_names)

    # 3. Add keys to commons tracker if they occur more than once
    for key_name in key_counter:
        if key_counter[key_name] > 1:
            commons[key_name] = []

    # 4. Save values for common keys as Counter dicts
    for filename in p_metadata_collection:
        for key in p_metadata_collection[filename]:
            if key in commons:

                # A. Add each member of a 2D or 1D list 
                new_value = p_metadata_collection[filename][key]
                if isinstance(new_value, list):
                    
                    # 1. 2D list check
                    new_list = new_value
                    if isinstance(new_value[0], list):
                        new_list = chain.from_iterable(new_list)

                    # 2. Add all values
                    for list_value in new_list:
                        commons[key].append(list_value)
                # B. Otherwise, just add the value
                else:
                    commons[key].append(new_value)
    for key in commons:
        commons[key] = Counter(commons[key])

    # 5. Return a dict keyed on common keys with Counters of their values
    return commons

# Main script

def main():

    # 0. Stores json data, keyed on filename
    edition_metadata = {}

    # 1. Gather metadata from Internet Archive editions
    internet_archive_path = "{0}{1}metadata{1}".format(
        aolm_paths.data_paths["twain"]["internet_archive"],
        os.sep)
    for json_filepath in glob.glob(internet_archive_path + "*"):
        with open(json_filepath, "r") as json_file:
            edition_metadata[os.path.basename(json_filepath)] = json.load(json_file)
    
    # 2. Get common fields and common values of those fields
    commons = get_metadata_commons(edition_metadata)

    # 3. Print output
    for key in commons:
        print(debug_separator)
        print(key)
        print(commons[key])
        

if "__main__" == __name__:
    main()
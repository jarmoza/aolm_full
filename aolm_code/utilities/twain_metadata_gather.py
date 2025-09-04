# Author: Jonathan Armoza
# Created: September 1, 2025
# Purpose: Gather key metadata fields on editions of 'Adventures of Huckleberry Finn'

# Imports

# Built-ins
import glob
import json
import os
import sys

def main():

    editions = {}
    input_directory = "/Users/weirdbeard/Documents/school/aolm_full/data/twain/huckleberry_finn/internet_archive/metadata/"
    output_filepath = "/Users/weirdbeard/Documents/school/aolm_full/experiments/chapter1/huckfinneditions_filenames2fullnames.json"
    
    # Internet Archive
    for filepath in glob.glob(input_directory + "*.json"):

        with open(filepath, "r") as input_file:

            json_data = json.load(input_file)

            filename = os.path.basename(filepath)[0:os.path.basename(filepath).rfind(".")]

            # Ex.
            # "publisher": "New York : C. L. Webster",
            # "publication_date": "1885",
            # "contributor": "University of California Libraries",
            # "copyright-evidence-operator": "alyson-wieczorek",
            # "added_date": "2006-11-27 15:38:29"            
            editions[filename] = {

                "added_date": json_data["added_date"] if "added_date" in json_data else "N/A",
                "contributor": json_data["contributor"] if "contributor" in json_data else "N/A",
                "copyright-evidence-operator": json_data["copyright-evidence-operator"] if "copyright-evidence-operator" in json_data else "N/A",
                "publication_date": json_data["publication_date"] if "publication_date" in json_data else "N/A",
                "publisher": json_data["publisher"] if "publisher" in json_data else "N/A",
                "scan_date": json_data["scan_date"] if "scan_date" in json_data else "N/A"
            }

            editions[filename]["short_name"] = ""

    # Project Gutenberg
    editions["2011-05-03-HuckFinn"] = { "short_name": "gutenberg_2011" }
    editions["2016-08-17-HuckFinn"] = { "short_name": "gutenberg_2016" }
    editions["2021-02-21-HuckFinn"] = { "short_name": "gutenberg_2021" }
    
    with open(output_filepath, "w") as output_file:
        json.dump(editions, output_file)


if "__main__" == __name__:
    main()
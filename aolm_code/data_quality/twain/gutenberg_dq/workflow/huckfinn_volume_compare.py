# Author: Jonathan Armoza
# Created: March 16, 2022
# Purpose: Scripts for comparing different aspects of digital editions of Mark
# Twain's 'The Adventures of Huckleberry Finn'

# Imports

# Standard libraries
import glob
import os

# Local libraries
from utilities.aolm_paths import data_paths, setup_data_paths
from utilities.aolm_utilities import debug_separator
from dq_metric_compare import HuckFinnVolumeComparer

# Global 

# Set


# Primary functions

def compare_gutenberg_editions(p_sourcetext_name, p_json_filepath):

    # 1. Load each edition into memory from its json file
    comparer = HuckFinnVolumeComparer(p_sourcetext_name, p_json_filepath)

    # 2. Get words that are new and common to non-source editions
    # (along with the common word counts)
    new_words_by_edition, common_word_counts_by_edition = comparer.different_words()

    return new_words_by_edition, common_word_counts_by_edition

def main():

    # 0. Setup AOLM data paths
    setup_data_paths()

    # 0. Filepath for json files for Huckleberry Finn editions from Project Gutenberg
    json_filepaths = glob.glob(data_paths["aolm_twain_root"] + \
        "data_quality{0}huckleberry_finn{0}project_gutenberg{0}output{0}*".format(os.sep))
    print(json_filepaths)
    
    # 1. Perform comparisons of the Project Gutenberg editions of Huckleberry Finn
    new_words_by_edition, common_word_counts_by_edition = \
        compare_gutenberg_editions("2021-02-21-HuckFinn_cleaned", json_filepaths)

    print("Different words from source edition")

    # 2. Debug print
    for edition in new_words_by_edition:
        print(debug_separator)
        print(edition)
        print(new_words_by_edition[edition])

    print("Word count differences of in-common words with source edition")
    for edition in common_word_counts_by_edition:
        print(debug_separator)
        print(edition)
        print("Total words: {0}".format(sum(common_word_counts_by_edition[edition].values())))
        print("Total unique words: {0}".format(len(list(common_word_counts_by_edition[edition].keys()))))
        print(common_word_counts_by_edition[edition])           

if "__main__" == __name__:
    main()
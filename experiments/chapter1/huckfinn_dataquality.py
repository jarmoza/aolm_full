# Author: Jonathan Armoza
# Created: July 25, 2024
# Purpose: Measuring data quality for the Huckleberry Finn data set

# List of data quality metrics to consider

# 1. Consistency
# 2. Integrity

# Tasks

# 1. Come up with reasonable interpretations/metrics of consistency and integrity for the Huck Finn corpus
# 2. Understand the state of the Huck Finn corpus
# - Create a document where the folders/files of the Twain corpus are explained and their provenance properly cited
# 3. Consider how metrics will apply to either the raw data downloaded or the demarcated data
# - e.g. Maybe we would prefer to put some dq metrics over the raw data, and for others examining portions of the text
# itself to use the demarcated data
# 4. Consider metadata assessments as dq metrics

# Note: Demarcated data consists of texts that have been uniformly subdivided by using uniform headings
# i.e. Huck Finn being divided by the same chapter name so chapter text can undergo relevant dq metrics


# NOTE: Thoughts/hypotheses and then findings should be written up
# These writings can then be used as an experimental (scientific) means of tweaking the data quality
# metrics, how they are weighted in the data quality framework machine/script


### Experiment 1

# Metadata quality

# Hypothesis

### Experiment 2

# Text quality
# Let's re-read Sebastian Coleman and my notes for data quality metrics that would be applicable for the texts in the collection
# Then implement a few metrics using the text ingestion utility scripts already written

# Hypothesis: Texts should (1) Contain all chapters found in the Ur copy (MTPO)
# and (2) be mostly identical internally chapter by chapter

# Format for experiment functions

# <quality-type>_<work-short-title>_<experiment-short-description>_<experiment-number>

# Imports

# Built-ins
import json
import os
import sys

print(os.getcwd())

# Custom
# sys.path.append(f"..{os.sep}..{os.sep}aolm_code{os.sep}objects")
sys.path.append(f"{os.getcwd()}{os.sep}aolm_code{os.sep}objects")
from mtpo_huckfinn_reader import MTPOHuckFinnReader
from pg_huckfinn_reader import PGHuckFinnReader
from aolm_textutilities import AOLMTextUtilities


# Globals

huckfinn_paths = {

    "hf_json_path": "/Users/user/Documents/school/aolm_full/data/twain/huckleberry_finn/internet_archive/txt/demarcated/complete/json",
    "hf_txt_path": "/Users/user/Documents/school/aolm_full/data/twain/huckleberry_finn/internet_archive/txt/demarcated/complete/txt"
}


# Experiments

def dq_huckfinn_chapterquality_1():

    # 0. Setup

    # A. Read in Ur text
    mtpo_huckfinn_filepath = f"{os.getcwd()}{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}mtpo{os.sep}"
    mtpo_huckfinn_file = "MTDP10000_edited.xml"
    mtpo_reader = MTPOHuckFinnReader(mtpo_huckfinn_filepath + mtpo_huckfinn_file)
    mtpo_reader.read()

    # B. Read in each subject text
    subject_filepath_list = []
    subject_readers = []
    pg_huckfinn_filepath = f"{os.getcwd()}{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}project_gutenberg{os.sep}json{os.sep}"
    pg_huckfinn_file = "2011-05-03-HuckFinn.json"
    pg_reader = PGHuckFinnReader(pg_huckfinn_filepath + pg_huckfinn_file)
    pg_reader.read()    

    # 1. Experiment 2 - Text quality

    # A. Does a text contain all the chapters of the Ur copy of that text?
    print(f"Ur text chapter count: {mtpo_reader.chapter_count}")
    print(f"Subject text chapter count: {pg_reader.chapter_count}")

    # B. What percent of each chapter is identical to its corresponding chapter in the Ur copy of that text?

    # Measure percent line match between Ur text and subject texts

    # I. Chapters to run through
    chapter_count = 43

    # II. Keeps track of line match values for each chapter
    line_match_percents = { index: 0 for index in range(chapter_count) }

    # III. Compare line matches across chapters
    for index in range(chapter_count):

        # a. Get Ur text lines for this chapter
        mtpo_chapter_lines = mtpo_reader.get_chapter(index + 1)
        mtpo_chapter_string = AOLMTextUtilities.create_string_from_lines(mtpo_chapter_lines)
        mtpo_chapter_string = AOLMTextUtilities.clean_string(mtpo_chapter_string)

        # b. Get subject text lines for this chapter
        pg_chapter_lines = pg_reader.get_chapter(index + 1)
        pg_chapter_string = AOLMTextUtilities.create_string_from_lines(pg_chapter_lines)
        pg_chapter_string = AOLMTextUtilities.clean_string(pg_chapter_string)

        line_match_percents[index] = AOLMTextUtilities.percent_line_match(
            mtpo_chapter_string,
            pg_chapter_string
        )

    print(line_match_percents)    

    # C. Given that, what percent of chapters are complete in this text?
    acceptable_completion_percent = 0.99
    passable_chapters = 0
    for chapter_index in line_match_percents:
        if line_match_percents[chapter_index] >= acceptable_completion_percent:
            passable_chapters += 1
    print(f"# of chapters with >= 95% complete: {passable_chapters}")


def main():
    
    dq_huckfinn_chapterquality_1()


if "__main__" == __name__:

    print(f"Current working directory: {os.getcwd()}")

    main()










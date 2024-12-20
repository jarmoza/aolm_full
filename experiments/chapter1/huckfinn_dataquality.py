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


# Custom

# Command line
sys.path.append(f"..{os.sep}..{os.sep}aolm_code{os.sep}objects")
sys.path.append(f"..{os.sep}..{os.sep}aolm_code{os.sep}data_quality{os.sep}core")

# IDE
sys.path.append(f"{os.getcwd()}{os.sep}aolm_code{os.sep}objects")
sys.path.append(f"{os.getcwd()}{os.sep}aolm_code{os.sep}data_quality{os.sep}core")

from aolm_textutilities import AOLMTextUtilities
from dq_metric import DataQualityMetric
from mtpo_huckfinn_reader import MTPOHuckFinnReader
from pg_huckfinn_reader import PGHuckFinnReader


# Globals

huckfinn_paths = {

    "ia_json_path": "/Users/weirdbeard/Documents/school/aolm_full/data/twain/huckleberry_finn/internet_archive/txt/demarcated/complete/json",
    "ia_txt_path": "/Users/weirdbeard/Documents/school/aolm_full/data/twain/huckleberry_finn/internet_archive/txt/demarcated/complete/txt",
    "pg_path": "/Users/weirdbeard/Documents/school/aolm_full/data/twain/huckleberry_finn/project_gutenberg"
}

# Utility functions

def read_project_gutenberg_json():

    pg_huckfinn_filepath = f"{huckfinn_paths["pg_path"]}{os.sep}json{os.sep}"
    subject_filepath_list = [
        pg_huckfinn_filepath + "2011-05-03-HuckFinn.json",
        pg_huckfinn_filepath + "2016-08-17-HuckFinn.json",
        pg_huckfinn_filepath + "2021-02-21-HuckFinn.json"
    ]
    subject_readers = [PGHuckFinnReader(filepath) for filepath in subject_filepath_list]
    for reader in subject_readers:
        reader.read()

    return subject_readers  

def read_project_gutneberg_metadata():

    pg_huckfinn_filepath = f"{huckfinn_paths["pg_path"]}{os.sep}metadata{os.sep}"
    subject_filepath_list = [
        
        pg_huckfinn_filepath + "2011-05-03-HuckFinn_metadata.json",
        pg_huckfinn_filepath + "2016-08-17-HuckFinn_metadata.json",
        pg_huckfinn_filepath + "2021-02-21-HuckFinn_metadata.json"
    ]
    metadata_json = {}
    for subject_filepath in subject_filepath_list:
        with open(subject_filepath, "r") as json_file:
            metadata_json[os.path.basename(subject_filepath)] = json.load(json_file)

    return metadata_json

# Experiments

def dq_huckfinn_chapterquality_1():

    # 0. Setup

    # A. Read in Ur text
    mtpo_huckfinn_filepath = f"{os.getcwd()}{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}mtpo{os.sep}"
    mtpo_huckfinn_file = "MTDP10000_edited.xml"
    mtpo_reader = MTPOHuckFinnReader(mtpo_huckfinn_filepath + mtpo_huckfinn_file)
    mtpo_reader.read()

    # B. Read in each subject text
    pg_huckfinn_filepath = f"{os.getcwd()}{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}project_gutenberg{os.sep}json{os.sep}"
    subject_filepath_list = [
        pg_huckfinn_filepath + "2011-05-03-HuckFinn.json",
        pg_huckfinn_filepath + "2016-08-17-HuckFinn.json",
        pg_huckfinn_filepath + "2021-02-21-HuckFinn.json"
    ]
    subject_readers = [PGHuckFinnReader(filepath) for filepath in subject_filepath_list]
    for reader in subject_readers:
        reader.read()

    # 1. Experiment 2 - Text quality

    # A. Does a text contain all the chapters of the Ur copy of that text?
    print(f"Ur text chapter count: {mtpo_reader.chapter_count}")

    # B. What percent of each chapter is identical to its corresponding chapter in the Ur copy of that text?

    # Measure percent line match between Ur text and subject texts

    # I. Chapters to run through
    chapter_count = 43

    # II. Keeps track of line match values for each chapter
    line_match_percents = { index: 0 for index in range(chapter_count) }

    # III. Read Ur text chapters once for speed
    mtpo_chapter_strings = []
    for index in range(chapter_count):

        # a. Get Ur text lines for this chapter
        mtpo_chapter_lines = mtpo_reader.get_chapter(index + 1)
        mtpo_chapter_string = AOLMTextUtilities.create_string_from_lines(mtpo_chapter_lines)
        mtpo_chapter_string = AOLMTextUtilities.clean_string(mtpo_chapter_string)
        mtpo_chapter_strings.append(mtpo_chapter_string)


    # III. Compare line matches across chapters
    for pg_reader in subject_readers:

        print(f"Subject text {pg_reader.filename} chapter count: {pg_reader.chapter_count}")

        for index in range(chapter_count):

            if index + 1 == 16:
                pass

            # a. Get Ur text lines for this chapter
            mtpo_chapter_string = mtpo_chapter_strings[index]

            # b. Get subject text lines for this chapter
            pg_chapter_lines = pg_reader.get_chapter(index + 1)
            pg_chapter_string = AOLMTextUtilities.create_string_from_lines(pg_chapter_lines)
            pg_chapter_string = AOLMTextUtilities.clean_string(pg_chapter_string)

            line_match_percents[index] = AOLMTextUtilities.percent_line_match(
                mtpo_chapter_string,
                pg_chapter_string
            )

        # print(line_match_percents)    

        # C. Given that, what percent of chapters are complete in this text?
        acceptable_completion_percent = 0.99
        passable_chapters = 0
        for chapter_index in line_match_percents:
            if line_match_percents[chapter_index] >= acceptable_completion_percent:
                passable_chapters += 1
            else:
                print(f"Chapter {chapter_index + 1} is not passable for {pg_reader.filename}")
        print(f"# of chapters with >= 95% complete: {passable_chapters}")

        print("=" * 80)

def dq_huckfinn_pg_datasetcompleteness_metadatasufficiency(p_dqmetric_instance):

    # NOTES
    # “Metadata assessment tests first for existence and completeness
    # (percentage of tables defined, percentage of columns defined; percentage
    # of codefields supported by references data, etc.) and next for the
    # clarity and quality of definitions (clear, comprehensible, unambiguous,
    # grammatically correct, etc.) and consistency of representation (the same
    # field content defined in the same way).” (224)

    # 2. Clarity and quality of definitions (clear, comprehensible, unambiguous,
    # grammatically correct, etc.)

    # Maybe here can be a more qualitative score based on the state of the metadata in the original files,
    # the difficulty it took to extract and shape the metadata, etc.
    # For example: A qualitative score based on a standard of qualitative scoring for this category
    # and that reflects the state of the data and the work required, as mnetioned above

    # 3. Consistency of representation (the same field content defined in the same way)

    metadata_json = p_dqmetric_instance.input
    results = {

        "existence_and_completeness": {},
        "clarity_and_quality": {},
        "consistency_of_representation": {}
    }

    # 1. Existence and Completeness
    # A. Percentage of tables defined
    # B. Percentage of columns defined
    # C. Percentage of codefields supported by reference data

    p_dqmetric_instance.add_explanation(
        "existence_and_completeness",
        "Existence score:\n" +
        "Editions on Project Gutenberg vs # editions in entire dataset (how many editions are on PG compared to everyone else)\n" +
        "Completeness score: Each edition gets a score that is #edition keys / #total unique keys from the overall dataset\n" +
        "These then get tallied into an overall score for the Project Gutenberg site"
    )

    # A. Percentage of tables defined (All works have header metadata)
    results["existence_and_completeness"]["percent_tables_defined"] = 1.0

    # B. Percentage of columns defined
    unkeyed_key = "unkeyed_fields"
    results["existence_and_completeness"]["percent_key_coverage"] = {}

    # I. Get key set for all metadata files
    pg_metadata_keyset = AOLMTextUtilities.get_keyset([metadata_json[filepath] for filepath in metadata_json], [unkeyed_key])
    pg_metadata_keyset.remove(unkeyed_key)

    # II. Calculate percentage coverage each edition has of the total keyset
    for filepath in metadata_json:
        edition_keys = AOLMTextUtilities.get_keyset([metadata_json[filepath]], [unkeyed_key])
        edition_keys.remove(unkeyed_key)
        results["existence_and_completeness"]["percent_key_coverage"][filepath] = 100 * len(edition_keys) / float(len(pg_metadata_keyset))
    
    # 2. Clarity and quality of definitions
    
    p_dqmetric_instance.add_explanation(
        "clarity_and_quality",
        "Number of unkeyed variables / total key count"
    )

    # A. How many fields are unkeyed?
    total_keyset_len = (len(pg_metadata_keyset))
    unkeyed_count_by_edition = {}
    for filepath in metadata_json:
        edition_unkeyed = metadata_json[filepath][unkeyed_key].keys()
        unkeyed_count_by_edition[filepath] = len(edition_unkeyed) / float(total_keyset_len)
        results["clarity_and_quality"][filepath] = len(edition_unkeyed) / float(total_keyset_len)

    # 3. Consistency of representation
    
    p_dqmetric_instance.add_explanation(
        "consistency_of_representation",
        "Tallies number of mismatches across each unique value and then divides that by the total number of values in metadata of all editions"
    )
    
    # A. Get lists of duplicated, unique values
    pg_metadata_valueset = AOLMTextUtilities.get_valueset([metadata_json[filepath] for filepath in metadata_json])
    valuematch_dict = AOLMTextUtilities.levenshtein_listcompare(pg_metadata_valueset)
    
    # B. Determine mismatches as percentage of the total number of values
    # represented in the metadata of all editions
    mismatch_count = 0
    for key in valuematch_dict:
        if len(valuematch_dict[key]) > 0:
            mismatch_count += len(valuematch_dict[key])
    results["consistency_of_representation"] = 100 * mismatch_count / float(len(pg_metadata_valueset))

    return results


def main():

    # NEXT STEP:
    # (1) Tally scores
    # (2) Determine overall metadata data quality score
    # (3) Move on to text data quality experiment 3

    # Mark Twain Project Online (MTPO)
    
    # Project Gutenberg (PG)

    huckfinn_pg_metadata = read_project_gutneberg_metadata()

    # Metadata sufficiency

    huckfinn_pg_metadata_sufficiency = DataQualityMetric(
        "HuckFinnPGMetadata",
        huckfinn_pg_metadata,
        dq_huckfinn_pg_datasetcompleteness_metadatasufficiency
    )

    huckfinn_pg_metadata_sufficiency.compute()

    # dq_huckfinn_chapterquality_1()

    huckfinn_pg_metadata_sufficiency.show_results(p_show_explanations=True)

    # Internet Archive (IA)


if "__main__" == __name__:

    main() 










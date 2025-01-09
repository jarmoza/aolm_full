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
from collections import Counter
from statistics import mean

# Custom

# Command line
sys.path.append(f"..{os.sep}..{os.sep}aolm_code{os.sep}objects")
sys.path.append(f"..{os.sep}..{os.sep}aolm_code{os.sep}data_quality{os.sep}core")

# IDE
sys.path.append(f"{os.getcwd()}{os.sep}aolm_code{os.sep}objects")
sys.path.append(f"{os.getcwd()}{os.sep}aolm_code{os.sep}data_quality{os.sep}core")

import spacy
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

# Mark Twain Project Online abbreviation
MTPO = "mtpo"

# Utility functions

def get_spacy_eng_sm_model():

    return spacy.load("en_core_web_sm")

def read_marktwain_project_online_text():

    # 1. Read in Ur text
    mtpo_huckfinn_filepath = f"{os.getcwd()}{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}mtpo{os.sep}"
    mtpo_huckfinn_file = "MTDP10000_edited.xml"
    mtpo_reader = MTPOHuckFinnReader(mtpo_huckfinn_filepath + mtpo_huckfinn_file)
    mtpo_reader.read()
    
    return mtpo_reader    

def read_project_gutenberg_metadata():

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

def read_project_gutenburg_text():

    huckfinn_text_readers = {}

    # 1. Read in each Project Gutenberg edition of Huckleberry Finn
    pg_huckfinn_filepath = f"{os.getcwd()}{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}project_gutenberg{os.sep}json{os.sep}"
    subject_filepath_list = [
        pg_huckfinn_filepath + "2011-05-03-HuckFinn.json",
        pg_huckfinn_filepath + "2016-08-17-HuckFinn.json",
        pg_huckfinn_filepath + "2021-02-21-HuckFinn.json"
    ]
    for filepath in subject_filepath_list:
        huckfinn_text_readers[os.path.basename(filepath)] = PGHuckFinnReader(filepath)
        huckfinn_text_readers[os.path.basename(filepath)].read()

    return huckfinn_text_readers

# Experiments

# Metric computes

def __compute_dq_huckfinn_pg_datasetcompleteness_metadatasufficiency(p_dqmetric_instance):

    # Experiment 1 - Metadata Quality

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
    results["existence_and_completeness"]["percent_tables_defined"] = 100.0

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
        results["clarity_and_quality"][filepath] = 100 * len(edition_unkeyed) / float(total_keyset_len)

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

def __compute_dq_huckfinn_pg_datasetcompleteness_recordcountstocontrolrecords(p_dqmetric_instance):

    # Experiment 2 - Text Quality
    # DQ Metric Dataset Completeness - Record Counts

    # 0. Setup
    huckfinn_text_readers = p_dqmetric_instance.input
    results = { reader_name: {

            "chapter_count": {},
            "sentence_count": {
                "by_chapter": {}
            },
            "word_count": {
                "by_chapter": {}
            }
        } for reader_name in huckfinn_text_readers if MTPO != reader_name
    }    

    # 1. Chapter count

    # A. Chapter count comparison between MTPO and PG editions

    # Does a text contain all the chapters of the Ur copy of that text?
    print(f"Ur text chapter count: {huckfinn_text_readers[MTPO].chapter_count}")

    # Chapters to run through (43 from Ur copy, MTPO)
    ur_chapter_count = huckfinn_text_readers[MTPO].chapter_count

    # Chapter counts of PG editions
    for reader_name in results:
        if MTPO == reader_name:
            continue
        results[reader_name]["chapter_count"] = 100.0 * huckfinn_text_readers[reader_name].chapter_count / ur_chapter_count

    # 2. Sentence count (using spaCy's sentence model)

    # Measure percent line match between Ur text and subject texts
    line_match_percents = { index: 0 for index in range(ur_chapter_count) }

    # Get sentences from chapter strings via spaCy

    # A. Load up spaCy model
    nlp = get_spacy_eng_sm_model()

    # B. Compare sentences of each chapter of Ur text with each PG edition
    for index in range(1, ur_chapter_count + 1):

        # I. Read the ur chapter
        ur_spacy_chapter = nlp("\n".join(huckfinn_text_readers[MTPO].get_chapter(index)))

        # II. Create a dictionary of unique sentence counts of the ur chapter
        ur_sentence_dict = AOLMTextUtilities.get_sentence_dict_from_spacy_doc(ur_spacy_chapter)

        # III. Compare the ur chapter sentences to those in each PG edition
        for reader_name in huckfinn_text_readers:
            if MTPO == reader_name:
                continue

            pg_spacy_chapter = nlp("\n".join(huckfinn_text_readers[reader_name].get_chapter(index)))
            pg_sentence_dict = AOLMTextUtilities.get_sentence_dict_from_spacy_doc(pg_spacy_chapter)
            
            results[reader_name]["sentence_count"]["by_chapter"][str(index)] = \
                AOLMTextUtilities.dictionaries_percent_equal(ur_sentence_dict, pg_sentence_dict)
            
    # for reader_name in results:
    #     print("=" * 80)
    #     print(f"{reader_name}")
    #     for chapter_index in results[reader_name]["sentence_count"]["by_chapter"]:
    #         print(f"chapter {chapter_index}: {results[reader_name]["sentence_count"]["by_chapter"][chapter_index]}")
    #     print("\n")

    # 3. Sentence count
    for index in range(1, ur_chapter_count + 1):

        # I. Read the ur chapter's words
        ur_chapter = huckfinn_text_readers[MTPO].get_chapter(index)
        ur_words = AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(ur_chapter))
        ur_words = Counter(ur_words)

        # II. Compare the ur chapter words to those in each PG edition
        for reader_name in huckfinn_text_readers:
            if MTPO == reader_name:
                continue

            pg_chapter = huckfinn_text_readers[reader_name].get_chapter(index)
            pg_words = AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(pg_chapter))
            pg_words = Counter(pg_words)
            
            results[reader_name]["word_count"]["by_chapter"][str(index)] = \
                AOLMTextUtilities.dictionaries_percent_equal(ur_words, pg_words)
            
    # for reader_name in results:
    #     print("=" * 80)
    #     print(f"{reader_name}")
    #     for chapter_index in results[reader_name]["word_count"]["by_chapter"]:
    #         print(f"chapter {chapter_index}: {results[reader_name]["word_count"]["by_chapter"][chapter_index]}")
    #     print("\n")    

    # NEXT UP:
    # (1) Review sentence comparison function
    # (2) Finish out text record count dq metric
    # (3) Visualize text record count and metadata suffiency submetrics and write about them

    # # C. Given that, what percent of chapters are complete in this text?
    # acceptable_completion_percent = p_dqmetric_instance.metric_min
    # passable_chapters = 0

    return results

# Metric evaluations

def __eval_dq_huckfinn_pg_datasetcompleteness_metadatasufficiency(p_dqmetric_instance):

    # results = {

    #     "existence_and_completeness": {
    #         "percent_tables_defined": 0,
    #         "percent_key_coverage": {}
    #     },
    #     "clarity_and_quality": {},
    #     "consistency_of_representation": {}
    # }

    results = p_dqmetric_instance.result

    # 1. Calculate evaluations of subsubmetrics
    subsubmetric_evaluations = {
        "existence_and_completeness": {
            "percent_tables_defined": results["existence_and_completeness"]["percent_tables_defined"],
            "percent_key_coverage": mean(results["existence_and_completeness"]["percent_key_coverage"].values())
        },
        "clarity_and_quality": mean(results["clarity_and_quality"].values()),
        "consistency_of_representation": results["consistency_of_representation"]
    }

    # 2. Calculate evaluation of submetrics
    submetric_evaluations = {
        "existence_and_completeness": mean(subsubmetric_evaluations["existence_and_completeness"].values()),
        "clarity_and_quality": subsubmetric_evaluations["clarity_and_quality"],
        "consistency_of_representation": subsubmetric_evaluations["consistency_of_representation"]
    }

    # 3. Metric is weighted mean of submetrics
    metric_evaluation = mean(submetric_evaluations.values())

    return metric_evaluation

def __eval_dq_huckfinn_pg_datasetcompleteness_recordcountstocontrolrecords(p_dqmetric_instance):

    # results = { reader_name: {

    #         "chapter_count": {},
    #         "sentence_count": {
    #             "by_chapter": {}
    #         },
    #         "word_count": {
    #             "by_chapter": {}
    #         }
    #     } for reader_name in huckfinn_text_readers if MTPO != reader_name
    # }

    results = p_dqmetric_instance.result

    # 1. Calculate evaluations of subsubmetrics
    subsubmetric_evaluations = { 
        reader_name: {
            "chapter_count": results[reader_name]["chapter_count"],
            "sentence_count": mean(results[reader_name]["sentence_count"]["by_chapter"].values()),
            "word_count": mean(results[reader_name]["word_count"]["by_chapter"].values())
        }
        for reader_name in results 
    }

    # 2. Calculate evaluation of submetrics
    submetric_evaluations = {

        "chapter_count": mean([subsubmetric_evaluations[reader_name]["chapter_count"] for reader_name in subsubmetric_evaluations if MTPO != reader_name]),
        "sentence_count": mean([subsubmetric_evaluations[reader_name]["sentence_count"] for reader_name in subsubmetric_evaluations if MTPO != reader_name]),
        "word_count": mean([subsubmetric_evaluations[reader_name]["word_count"] for reader_name in subsubmetric_evaluations if MTPO != reader_name]),
    }

    # 3. Metric is weighted mean of submetrics
    metric_evaluation = mean(submetric_evaluations.values())

    return metric_evaluation

# Metric run helper functions

def run_pg_huckfinn_dq_metadatasufficiency():

    # Metadata sufficiency (MTPO vs PG)

    huckfinn_pg_metadata = read_project_gutenberg_metadata()
    # huckfinn_pg_metadata[MTPO] = read_marktwain_project_online_text()
    huckfinn_pg_metadata_sufficiency = DataQualityMetric(
        "HuckFinnPGMetadata",
        huckfinn_pg_metadata,
        __compute_dq_huckfinn_pg_datasetcompleteness_metadatasufficiency,
        __eval_dq_huckfinn_pg_datasetcompleteness_metadatasufficiency
    )
    huckfinn_pg_metadata_sufficiency.run(p_show_explanations=True)

    return huckfinn_pg_metadata_sufficiency

def run_pg_huckfinn_dq_textrecordcounts():

    # Text record counts (MTPO vs PG)

    # 1. Read ur text and subject texts
    huckfinn_textdata = read_project_gutenburg_text()
    huckfinn_textdata[MTPO] = read_marktwain_project_online_text()

    # 2. Create data quality metric
    huckfinn_pg_text_recordcounts = DataQualityMetric(
        "HuckFinnPGText",
        huckfinn_textdata,
        __compute_dq_huckfinn_pg_datasetcompleteness_recordcountstocontrolrecords,
        __eval_dq_huckfinn_pg_datasetcompleteness_recordcountstocontrolrecords
    )
    huckfinn_pg_text_recordcounts.urtext_name = MTPO
    huckfinn_pg_text_recordcounts.metric_min = 0.95

    # 3. Compute metric and save results
    huckfinn_pg_text_recordcounts.compute()

    # 4. Visualize metric with metric min falloff chart

    return huckfinn_pg_text_recordcounts


def main():

    dq_metrics = [
        run_pg_huckfinn_dq_metadatasufficiency(),
        run_pg_huckfinn_dq_textrecordcounts()
    ]

    dq_metric_evaluations = [metric.evaluate() for metric in dq_metrics]
    
    overall_evaluation = mean(dq_metric_evaluations)

    print(f"Overall Project Gutenberg data quality: {overall_evaluation}")


if "__main__" == __name__:

    main() 










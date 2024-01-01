"""
# Author: Jonathan Armoza
# Created: February 28, 2022
# Purpose: Maintains intrinsic data quality metrics and dimensions for
# 'The Adventures of Huckleberry Finn'

===============================================================================
Intrinsic data quality 

May be a measure of the success of matching an iteration (digitized copy,
alternate edition, etc.) of a text to a physical or digital source that is
considered to be the primary/reputable edition

Intrinsic dimensions include accuracy, objectivity, believability, and reputation

Accuracy - how close to the ground truth of a particular edition

Objectivity - how close to the ground truth of the best edition

Believability - how many steps/orders removed from the original

Reputation - Research + ask Peter Gibian
"""

# Imports

# Standard libraries
import json
import os

# Local libraries
from data_quality.core.dq_metric import DataQualityMetric
from data_quality.twain.gutenberg_dq.workflow.huckfinn_dq_metric import HuckFinn_DQMetric
from utilities import aolm_paths

class HuckFinn_InstrinsicDQ(HuckFinn_DQMetric):

    # Constructor

    def __init__(self, p_source_metadata_json, p_compared_metadata_json):

        # 0. List of dimensions
        self.m_dimensions = [

            HuckFinn_InstrinsicDQ.s_accuracy,
            HuckFinn_InstrinsicDQ.s_objectivity,
            HuckFinn_InstrinsicDQ.s_believability,
            HuckFinn_InstrinsicDQ.s_reputation
        ]

        # 0. Intrinsic data quality dimension scores
        self.m_dimension_scores = { self.m_dimensions[index]: 0 for index in range(len(self.m_dimensions)) }

        # 0. Weightings for each dimension for computing the overall score
        self.m_dimension_weights = { self.m_dimensions[index]: 1 for index in range(len(self.m_dimensions)) }

        # 1. Call the base constructor
        super().__init__("HuckFinn_IntrinsicDQ", p_compared_metadata_json)

        # 2. Save the source (ground truth) metadata json
        self.m_source_metadata_json = p_source_metadata_json

    # Properties

    @property
    def source_metadata(self):
        return self.m_source_metadata_json                

    # Dimensions

    @property
    def accuracy(self):
        # How close to ground truth version am I?
        return self.m_dimension_scores[HuckFinn_InstrinsicDQ.s_accuracy]
    @property
    def objectivity(self):
        # Are there are any edits from the editor of this edition?
        # How many are there?
        # How large are they?
        return self.m_dimension_scores[HuckFinn_InstrinsicDQ.s_objectivity]
    @property
    def believability(self):
        # Is it believable that this edition could hue close to the ground truth edition?
        return self.m_dimension_scores[HuckFinn_InstrinsicDQ.s_believability]
    @property
    def reputation(self):
        # Examination of metadata
        # What is the publication history?
        # Publisher? Edition? Date?
        # How far is this edition from the original?
        # Can this be quantified?
        return self.m_dimension_scores[HuckFinn_InstrinsicDQ.s_reputation]

    def compute(self):

        # 1. Compute accuracy score
        self.m_dimension_scores[HuckFinn_InstrinsicDQ.s_accuracy] = self.__compute_accuracy()

        # 2. Compute objectivity score
        self.m_dimension_scores[HuckFinn_InstrinsicDQ.s_objectivity] = self.__compute_objectivity()

        # 3. Compute believability score
        self.m_dimension_scores[HuckFinn_InstrinsicDQ.s_believability] = self.__compute_believability()

        # 4. Compute reputation score
        self.m_dimension_scores[HuckFinn_InstrinsicDQ.s_reputation] = self.__compute_reputation()

        # 5. Compute the overall data quality metric
        self.m_result = self.__compute_overall_score()

    # Dimension scores

    def __compute_accuracy(self):

        # Data quality metric: Comparing overall word counts
        # Goal: Calculate +/- word counts (and, implicitly, missing words)
        
        # 0. HuckFinn metadata key for comparison
        key = "total_word_frequencies"

        # 1. Calculate the total words in each text
        total_words = sum(self.metadata[key].values())
        source_total_words = sum(self.source_metadata[key].values())

        # 2. Create an overall +/- tally of word counts
        word_match_tally = 0
        for word in self.source_metadata[key]:
            
            # A. Check to see if word in source text is in this text
            if word in self.metadata[key]:
                word_match_tally += self.metadata[key][word] - self.source_metadata[key][word]
            # B. If the word is not in this text, subtract the source text frequency from the tally
            else:
                word_match_tally -= self.source_metadata[key][word]

        # 3. Determine the overall intrinsic, percent match metric
        print("Word match tally: {0}".format(word_match_tally))
        print("Source total words: {0}".format(source_total_words))
        percent_match = 100 * (word_match_tally / float(source_total_words))
        print("Percent match: {0}".format(percent_match))
        
        # Let's try the word match tally first
        return percent_match

    def __compute_objectivity(self):
        return 0

    def __compute_believability(self):
        return 0

    def __compute_reputation(self):
        return 0

    def __compute_overall_score(self):

        self.m_result = sum([
            self.m_dimension_scores[dimension] * self.m_dimension_weights[dimension]
            for dimension in self.m_dimensions
        ])

        return self.m_result

    # Static fields
    s_accuracy = "accuracy"
    s_objectivity = "objectivity"
    s_believability = "believability"
    s_reputation = "reputation"


def main():

    # 0. Setup code and data paths
    aolm_paths.setup_paths()

    # 0. IO paths
    root_folder = aolm_paths.data_paths["twain"]["huckleberry_finn"]
    sub_folder = "comparisons{0}word_frequency".format(os.sep)
    input_folder = "{0}{2}{1}input{1}json{1}".format(root_folder, os.sep, sub_folder)
    source_text_filename = "2021-02-21-HuckFinn_cleaned_processed.json"
    text_filename = "adventureshuckle00twaiiala_demarcated_processed.json"
    source_text_filepath = input_folder + source_text_filename
    text_filepath = input_folder + text_filename

    # 1. Read in the source text and compared text metadata files
    with open(source_text_filepath, "r") as input_file:
        source_metadata_json = json.load(input_file)
    with open(text_filepath, "r") as input_file:
        text_metadata_json = json.load(input_file)

    # 2. Compute the metric for intrinsic data quality
    intrinsic_dq = HuckFinn_InstrinsicDQ(
        source_metadata_json,
        text_metadata_json
    )
    intrinsic_dq.compute()

    # 3. Output the metric value
    print("{0} metric between '{1}' and '{2}': {3}".format(
        intrinsic_dq.name,
        source_text_filename,
        text_filename,
        intrinsic_dq.result
    ))


if "__main__" == __name__:
    main()
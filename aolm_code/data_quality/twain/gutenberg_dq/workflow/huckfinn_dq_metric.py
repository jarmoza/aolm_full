# Author: Jonathan Armoza
# Created: February 28, 2022
# Purpose: Maintains the core class for data quality metrics for
# 'The Adventures of Huckleberry Finn'


# Imports =====================================================================

# Standard libraries
from abc import abstractmethod

# Local libraries
from data_quality.core.dq_metric import DataQualityMetric


# Classes =====================================================================

# Primary class

# HuckFinnDQ_Metric: Knows how to ingest HuckFinn metadata
class HuckFinn_DQMetric(DataQualityMetric):

    # Constructor

    def __init__(self, p_name, p_metadata_json):

        # 1. Call the base data quality class constructor
        super().__init__(p_name, p_metadata_json)

    # HuckFunn-specific properties from its metadata
    @property
    def clean_components(self):
        return self.m_input["clean_components"]
    @property
    def components(self):
        return self.m_input["components"]
    @property
    def cumulative_word_counts(self):
        return self.m_input["cumulative_word_counts"]
    @property
    def flat_components(self):
        return self.m_input["flat_components"]
    @property
    def top_words(self):
        return self.m_input["top_words"]
    @property
    def top_word_counts_by_chapter(self):
        return self.m_input["top_word_counts_by_chapter"]
    @property
    def total_word_frequencies(self):
        return self.m_input["total_word_frequencies"]
    @property
    def word_counts(self):
        return self.m_input["word_counts"]

    # Specialized properties

    @property
    def metadata(self):
        return self.m_input


    # Required interface methods
    @abstractmethod
    def compute(self):
        pass

    def output(self):
        return { "metric": self.m_result }
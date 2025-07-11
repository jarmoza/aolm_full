# Author: Jonathan Armoza
# Created: July 7, 2025
# Purpose: Data quality metric that looks to the words only used once in a work

# Imports

# Third party
import numpy as np
import os

# Custom
from aolm_textutilities import AOLMTextUtilities
from dq_metric import DataQualityMetric
from aolm_textreader import AOLMTextReader

# Objects

class DatasetSignature_HapaxLegomenon(DataQualityMetric):

    # Constructor and private methods

    def __init__(self, p_readers=None):

        self.m_readers = p_readers

        self.m_results = {

            # List of all hapax for each work (alphabetized)
            "hapax_legomenon": { reader.filepath: None for reader in self.m_readers },

            # List of all hapax for each work (bucketed by chapter)
            "hapax_by_chapter": { reader.filepath: [] for reader in self.m_readers },

            # Full vocabulary vectors for each work
            "vocab_vectors": { reader.filepath: None for reader in self.m_readers }
        }
        self.m_evaluations = { 

            # Average hapax count across all works
            "metric": None,

            # Hapax counts for each work
            "submetric": { reader.filepath: None for reader in self.m_readers }
        }

    # Public methods

    def compute(self):

        # 1. Compute word vectors for each individual text
        for filepath in self.m_results["vocab_vectors"]:
            self.m_results["vocab_vectors"][filepath] = DatasetSignature_HapaxLegomenon.get_signature(
                filepath)

        # 2. Compute hapax for each text

        # 3. Compute hapax for each chapter


    def evaluate(self):
        pass

    # Static fields and methods

    @staticmethod
    def get_signature(p_source_file):

        # 1. Read in the text file
        with open(p_source_file, "r") as input_file:
            body_text = input_file.read()

        # 2. Create a word vector (in dict form) based off of the vocabulary of the text file
        return AOLMTextUtilities.word_count_from_string(body_text)    


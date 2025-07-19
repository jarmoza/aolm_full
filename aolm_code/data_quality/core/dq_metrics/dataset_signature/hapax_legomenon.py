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

    def __init__(self, p_readers=None, p_hapax_ceiling=1):

        self.m_readers = p_readers

        # Highest amount of uses for a token to be considered a hapax legomenon
        self.m_hapax_ceiling = p_hapax_ceiling

        self.m_results = {

            # List of all hapax for each work (alphabetized)
            "hapax_legomenon": { reader.filepath: None for reader in self.m_readers },

            # List of all hapax for each work (bucketed by chapter)
            "hapax_by_chapter": { reader.filepath: None for reader in self.m_readers },

            # Full vocabulary vectors for each work
            "vocab_vectors": { reader.filepath: None for reader in self.m_readers }
        }
        self.m_evaluations = { 

            # Average hapax count across all works
            "metric": None,

            # Hapax counts for each work
            "submetric": {

                "avg_chapter_hapax": { reader.filepath: 0 for reader in self.m_readers },
                "hapax_totals_by_work": { reader.filepath: 0 for reader in self.m_readers }                
            }
        }

    # Properties
    @property
    def hapax_ceiling(self):
        return self.m_hapax_ceiling
    def reader(self, p_filepath):
        for reader in self.m_readers:
            if p_filepath == reader.filepath:
                return reader
        return None
    @property
    def work_count(self):
        return len(self.m_readers)

    # Public methods

    def compute(self):

        # 1. Compute word vectors for each individual text
        for filepath in self.m_results["vocab_vectors"]:
            self.m_results["vocab_vectors"][filepath] = DatasetSignature_HapaxLegomenon.get_signature_from_file(
                filepath)

        # 2. Compute hapax for each text
        for filepath in self.m_results["vocab_vectors"]:
            self.m_results["hapax_legomenon"][filepath] = \
                DatasetSignature_HapaxLegomenon.get_hapax_legomenon(
                    self.m_results["vocab_vectors"][filepath],
                    self.m_hapax_ceiling
                )
    
        # 3. Compute hapax for each chapter
        for reader in self.m_readers:
            self.m_results["hapax_by_chapter"][reader.filepath] = {}
            for index in range(1, reader.chapter_count + 1):
                chapter_string = "\n".join(reader.get_chapter(index))
                chapter_word_vector = DatasetSignature_HapaxLegomenon.get_signature(chapter_string)
                chapter_hapax = DatasetSignature_HapaxLegomenon.get_hapax_legomenon(
                    chapter_word_vector,
                    self.m_hapax_ceiling
                )
                self.m_results["hapax_by_chapter"][reader.filepath][str(index)] = chapter_hapax

    def evaluate(self):

        # Average chapter hapax count from each work
        for filepath in self.m_results["hapax_by_chapter"]:
            for chapter in self.m_results["hapax_by_chapter"][filepath]:
                self.m_evaluations["submetric"]["avg_chapter_hapax"][filepath] += \
                    sum(self.m_results["hapax_by_chapter"][filepath][chapter].values())
            self.m_evaluations["submetric"]["avg_chapter_hapax"][filepath] /= \
                self.reader(filepath).chapter_count

        # Hapax counts for each work
        for filepath in self.m_evaluations["submetric"]["hapax_totals_by_work"]:
            for hapax in self.m_results["hapax_legomenon"][filepath]:
                self.m_evaluations["submetric"]["hapax_totals_by_work"][filepath] += \
                    self.m_results["hapax_legomenon"][filepath][hapax]

        # Average hapax count across all works
        # (NOTE: Hapax can be as high as hapax_ceiling for each token)
        avg_sum = 0
        for filepath in self.m_evaluations["submetric"]["hapax_totals_by_work"]:
            avg_sum += self.m_evaluations["submetric"]["hapax_totals_by_work"][filepath]
        self.m_evaluations["metric"] = avg_sum / self.work_count

    # Static fields and methods

    @staticmethod
    def get_hapax_legomenon(p_word_vector, p_hapax_ceiling):

        hapax_dict = {}
        for token in p_word_vector:
            if p_word_vector[token] <= p_hapax_ceiling:
                hapax_dict[token] = p_word_vector[token]

        return hapax_dict


    @staticmethod
    def get_signature(p_string):

        # Create a word vector (in dict form) based off of the vocabulary of the text file
        return AOLMTextUtilities.word_count_from_string(p_string)

    @staticmethod
    def get_signature_from_file(p_source_file):

        # 1. Read in the text file
        with open(p_source_file, "r") as input_file:
            body_text = input_file.read()

        # 2. Create a word vector (in dict form) based off of the vocabulary of the text file
        return DatasetSignature_HapaxLegomenon.get_signature(body_text)

    



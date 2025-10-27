# Author: Jonathan Armoza
# Created: July 7, 2025
# Purpose: Data quality metric that looks to the words only used n-times in a work

# Imports

# Third party
import numpy as np
import os

# Custom
from aolm_textutilities import AOLMTextUtilities
from dq_metric import DataQualityMetric
from aolm_textreader import AOLMTextReader

# Objects

class DatasetSignature_Legomena(DataQualityMetric):

    # Constructor and private methods

    def __init__(self, p_readers=None, p_legomena_ceiling=1):

        self.m_readers = p_readers

        # Highest amount of uses for a token to be considered a n-legomena
        self.m_legomena_ceiling = p_legomena_ceiling

        self.m_results = {

            # List of all legomena for each work (alphabetized)
            "legomena": { reader.filepath: None for reader in self.m_readers },

            # List of all legomena for each work (bucketed by chapter)
            "legomena_by_chapter": { reader.filepath: None for reader in self.m_readers },

            # Full vocabulary vectors for each work
            "vocab_vectors": { reader.filepath: None for reader in self.m_readers }
        }
        self.m_evaluations = { 

            # Average legomena count across all works
            "metric": None,

            # Hapax counts for each work
            "submetric": {

                "avg_chapter_legomena": { reader.filepath: 0 for reader in self.m_readers },
                "legomena_totals_by_work": { reader.filepath: 0 for reader in self.m_readers }                
            }
        }

    # Properties
    @property
    def legomena_ceiling(self):
        return self.m_legomena_ceiling
    @property
    def filepaths(self):
        return [reader.filepath for reader in self.m_readers]
    def reader(self, p_filepath):
        for reader in self.m_readers:
            if p_filepath == reader.filepath:
                return reader
        return None
    @property
    def work_count(self):
        return len(self.m_readers)
    
    # Evaluations

    @property
    def avg_legomena_count(self):
        return self.m_evaluations["metric"]
    def avg_chapter_legomena_for_work(self, filepath):
        return self.m_evaluations["submetric"]["avg_chapter_legomena"][filepath]
    def legomena_total_for_work(self, filepath):
        return self.m_evaluations["submetric"]["legomena_totals_by_work"][filepath]
    

    # Public methods

    def compute(self):

        # 1. Compute word vectors for each individual text
        for filepath in self.m_results["vocab_vectors"]:
            self.m_results["vocab_vectors"][filepath] = DatasetSignature_Legomena.get_signature_from_file(
                filepath)

        # 2. Compute legomena for each text
        for filepath in self.m_results["vocab_vectors"]:
            self.m_results["legomena"][filepath] = \
                DatasetSignature_Legomena.get_legomena(
                    self.m_results["vocab_vectors"][filepath],
                    self.m_legomena_ceiling
                )
    
        # 3. Compute legomena for each chapter
        for reader in self.m_readers:
            self.m_results["legomena_by_chapter"][reader.filepath] = {}
            for index in range(1, reader.chapter_count + 1):
                chapter_string = "\n".join(reader.get_chapter(index))
                chapter_word_vector = DatasetSignature_Legomena.get_signature(chapter_string)
                chapter_legomena = DatasetSignature_Legomena.get_legomena(
                    chapter_word_vector,
                    self.m_legomena_ceiling
                )
                self.m_results["legomena_by_chapter"][reader.filepath][str(index)] = chapter_legomena

    def evaluate(self):

        # Average chapter legomena count from each work
        for filepath in self.m_results["legomena_by_chapter"]:
            for chapter in self.m_results["legomena_by_chapter"][filepath]:
                self.m_evaluations["submetric"]["avg_chapter_legomena"][filepath] += \
                    sum(self.m_results["legomena_by_chapter"][filepath][chapter].values())
            self.m_evaluations["submetric"]["avg_chapter_legomena"][filepath] /= \
                self.reader(filepath).chapter_count

        # Legomena counts for each work
        for filepath in self.m_evaluations["submetric"]["legomena_totals_by_work"]:
            for legomena in self.m_results["legomena"][filepath]:
                self.m_evaluations["submetric"]["legomena_totals_by_work"][filepath] += \
                    self.m_results["legomena"][filepath][legomena]

        # Average legomena count across all works
        # (NOTE: Hapax can be as high as legomena_ceiling for each token)
        avg_sum = 0
        for filepath in self.m_evaluations["submetric"]["legomena_totals_by_work"]:
            avg_sum += self.m_evaluations["submetric"]["legomena_totals_by_work"][filepath]
        self.m_evaluations["metric"] = avg_sum / self.work_count

    def to_csv(self, p_output_filepath):

        columns = [

            "filename",
            "legomena_totals_by_work",
            "avg_chapter_legomena"
        ]

        with open(p_output_filepath, "w") as output_file:
            output_file.write(",".join(columns) + "\n")
            for reader in self.m_readers:
                output_file.write(",".join([
                    str(os.path.basename(reader.filepath)),
                    str(self.m_evaluations["submetric"]["legomena_totals_by_work"][reader.filepath]),
                    str(self.m_evaluations["submetric"]["avg_chapter_legomena"][reader.filepath])
                ]) + "\n"
                )

    # Static fields and methods

    s_metric_name = "legomena"

    @staticmethod
    def get_legomena(p_word_vector, p_legomena_ceiling):

        legomena_dict = {}
        for token in p_word_vector:
            if p_word_vector[token] <= p_legomena_ceiling:
                legomena_dict[token] = p_word_vector[token]

        return legomena_dict


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
        return DatasetSignature_Legomena.get_signature(body_text)





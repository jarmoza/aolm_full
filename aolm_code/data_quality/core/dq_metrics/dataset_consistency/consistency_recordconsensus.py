# Author: Jonathan Armoza
# Created: September 3, 2025
# Purpose: Metric for seeing how similar and different a group of editions of
#          the same work are without the aid of an ur edition

# Basis for consensus: the most expansive as agreed upon by a majority of the editions

# Imports

# Built-ins
import os
from collections import Counter
from math import ceil
from statistics import mean

# Custom
from aolm_textutilities import AOLMTextUtilities
from dq_metric import DataQualityMetric

class DatasetConsistency_RecordConsensus(DataQualityMetric):

    # Constructor and private methods

    def __init__(self, p_name, p_input, p_source_id, p_work_title, p_collection_title, p_text_json_filepath):

        super().__init__(p_name, p_input,
                         p_source_id=p_source_id,
                         p_work_title=p_work_title,
                         p_collection_title=p_collection_title,
                         p_path=p_text_json_filepath)
        
    def __compute_consensus(self, p_count_dictionaries):

        # 1. Gather counts of the unique keys in each edition
        key_counts = {}
        for edition in p_count_dictionaries:
            for key in p_count_dictionaries[edition]:
                if key not in key_counts:
                    key_counts[key] = []
                key_counts[key].append(p_count_dictionaries[edition][key])

        # 2. Determine consensus counts for each key
        consensus_key_counts = { key: ceil(mean(key_counts[key])) for key in key_counts }

        return key_counts, consensus_key_counts
    
    def __evaluate_consensus(p_count_dictionaries, p_consensus_key_counts):

        # 1. Determine positive or negative variance of edition key counts from the consensus (mean)
        edition_variances = { edition_name: {} for edition_name in p_count_dictionaries }

        for edition_name in p_count_dictionaries:
            for key in p_count_dictionaries[edition_name]:
                edition_variances[edition_name][key] = ceil(p_count_dictionaries[edition_name][key] - p_consensus_key_counts[key])

        return edition_variances

    # Properties
    @property
    def output(self):
        return self.__build_output_line__()
    @property
    def eval_output(self):
        return self.__build_eval_output_line__()

    # Public methods

    def compute(self):

        # 0. Setup

        # Idea is this metric is used per collection of editions

        # Compute 
        # (1) Tallies chapter counts,
        # (2) Calculates consensus for chapter count (ceiling of mean)
        # (3) Tallies sentence counts by chapter,
        # (4) Calculates consensus for unique sentences (all unique sentences shared by each chapter and mean frequency)
        # (5) Tallies word counts by chapter
        # (6) Calculates consensus for unique words per chapter (existence and mean frequency)

        # A. Calculate most number of chapters in all editions
        max_chapter_count = 0
        for reader_name in self.m_input:
            if self.m_input[reader_name].chapter_count > max_chapter_count:
                max_chapter_count = self.m_input[reader_name].chapter_count

        # B. Reset results
        self.m_results = {
            
            reader_name: {

                "chapter_count": 0,
                "sentence_count": {
                    "by_chapter": {}
                },
                "word_count": {
                    "by_chapter": {}
                }
            } for reader_name in self.m_input
        }
        self.m_results["consensus_chapter_count"] = 0
        self.m_results["consensus_sentence_counts"] = { str(index): 0 for index in range(1, max_chapter_count + 1) }
        self.m_results["consensus_word_counts"] = { str(index): 0 for index in range(1, max_chapter_count + 1) }

        # C. Load up spaCy model with the given name
        super().load_spacymodel()

        # 1. Chapter consensus

        # A. Gather chapter counts
        for reader_name in self.m_results:
            self.m_results[reader_name]["chapter_count"] = self.m_input[reader_name].chapter_count

        # B. Measure consensus chapter count for compute() purposes
        self.m_results["consensus_chapter_count"] = ceil(mean([self.m_results[reader_name]["chapter_count"] for reader_name in self.m_results]))

        # 2. Unique sentence consensus (using spaCy's sentence model)

        # A. Gather a set of sentence dictionaries for unique sentences of each chapter of each edition
        for index in range(1, self.m_results["consensus_chapter_count"] + 1):

            for reader_name in self.m_input:

                # Get sentences from chapter strings via spaCy
                compared_spacy_chapter = self.m_spacymodel("\n".join(self.m_input[reader_name].get_chapter(index)))
                compared_sentence_dict = AOLMTextUtilities.get_sentence_dict_from_spacy_doc(compared_spacy_chapter)

                self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)] = compared_sentence_dict

        # B. Determine a consensus count of the unique sentences per chapter across the editions
        for index in range(1, self.m_results["consensus_chapter_count"] + 1):

            # I. Add unique sentences to a chapter sentence set
            chapter_sentence_sets = {} 
            for reader_name in self.m_results:
                chapter_sentence_sets[reader_name] = set(list(self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)].keys()))

            # II. Get intersection of all sentence sets
            consensus_sentence_set = set.intersection(*list(chapter_sentence_sets.values()))

            # III. Determine the minimum frequency of each unique sentence in the chapter (typically should be 1)
            for sentence in consensus_sentence_set:
                frequency_list = []
                for reader_name in self.m_results:
                    frequency_list.append(self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)][sentence])
                self.m_results["consensus_sentence_counts"][str(index)][sentence] = min(frequency_list)

        # C. Gather a set of word dictionaries for unique words of each chapter of each edition
        for index in range(1, self.m_results["consensus_chapter_count"] + 1):

            for reader_name in self.m_input:

                compared_chapter = self.m_input[reader_name].get_chapter(index)
                compared_words = AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(compared_chapter))
                compared_words = Counter(compared_words)

                self.m_results[reader_name]["word_count"]["by_chapter"] = compared_words

        # D. Determine a consensus count of the unique words per chapter across the editions
        for index in range(1, self.m_results["consensus_chapter_count"] + 1):

            # I. Add unique words to a chapter word set
            chapter_word_sets = {} 
            for reader_name in self.m_results:
                chapter_word_sets[reader_name] = set(list(self.m_results[reader_name]["word_count"]["by_chapter"][str(index)].keys()))

            # II. Get intersection of all word sets
            consensus_word_set = set.intersection(*list(chapter_word_sets.values()))

            # III. Determine the minimum frequency of each unique word in the chapter
            for word in consensus_word_set:
                frequency_list = []
                for reader_name in self.m_results:
                    frequency_list.append(self.m_results[reader_name]["word_count"]["by_chapter"][str(index)][word])
                self.m_results["consensus_word_counts"][str(index)][word] = min(frequency_list)
                
        return self.m_results    

    def evaluate(self):

        # Evaluate 
        # Subsubmetric
        # (1) Calculates variance from chapter count mean for edition
        # (2) Calculates variance from unique sentence consensus of each chapter of each edition
        # (3) Calculates variance from unique word consensus of each chapter of each edition
        # Submetric
        # (4) Calculates mean variance of each edition
        # Metric
        # (5) Calculates mean of all edition variances

        # self.m_results = {
            
        #     reader_name: {

        #         "chapter_count": 0,
        #         "sentence_count": {
        #             "by_chapter": {}
        #         },
        #         "word_count": {
        #             "by_chapter": {}
        #         }
        #     } for reader_name in self.m_input
        # }
        # self.m_results["consensus_chapter_count"] = 0
        # self.m_results["consensus_sentence_counts"] = {}
        # self.m_results["consensus_word_counts"] = {}       

        self.m_evaluations = {}

        # NOTE: Consensus counts in results from compute may need to be split apart by reader_name/chapter in order to make sense below

        # 1. Calculate evaluations of subsubmetrics
        self.m_evaluations["subsubmetric"] = {

            reader_name: {
                
                "variance_from_sentence_consensus__by_chapter": { str(index): self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)][sentence] - self.m_results["consensus_sentence_counts"][str(index)][sentence] for index in range(1, self.m_results[reader_name]["chapter_count"] + 1) for sentence in self.m_results["consensus_sentence_counts"][str(index)] },
                "variance_from_word_consensus__by_chapter": { str(index): self.m_results[reader_name]["word_count"]["by_chapter"][str(index)][word] - self.m_results["consensus_word_counts"][str(index)][word] for index in range(1, self.m_results[reader_name]["chapter_count"] + 1) for word in self.m_results["consensus_word_counts"][str(index)] }
            }
            for reader_name in self.m_results
        }

        self.m_evaluations["submetric"] = {

            reader_name: {

                "variance_from_chapter_consensus__by_edition": self.m_input[reader_name].chapter_count - self.m_results["consensus_chapter_count"],
                "mean_variance_from_sentence_consensus__by_edition": mean(list(self.m_evaluations["subsubmetric"][reader_name]["variance_from_sentence_consensus__by_chapter"].values())),
                "mean_variance_from_word_consensus__by_edition": mean(list(self.m_evaluations["subsubmetric"][reader_name]["variance_from_word_consensus__by_chapter"].values()))

            }
            for reader_name in self.m_results
        }

        self.m_evaluations["metric"] = {

            "mean_variance_from_chapter_consensus": mean([self.m_evaluations["submetric"][reader_name]["variance_from_chapter_consensus__by_edition"] for reader_name in self.m_results]),
            "mean_of_mean_variance_from_sentence_consensus__by_edition": mean([self.m_evaluations["submetric"][reader_name]["mean_variance_from_sentence_consensus__by_edition"] for reader_name in self.m_results]),
            "mean_of_mean_variance_from_word_consensus__by_edition": mean([self.m_evaluations["submetric"][reader_name]["mean_variance_from_word_consensus__by_edition"] for reader_name in self.m_results])
        }

        return self.metric_evaluation
    
    s_metric_name = "consistency_recordconsensus"
    

def main():
    pass

if "__main__" == __name__:
    main()
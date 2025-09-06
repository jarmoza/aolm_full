# Author: Jonathan Armoza
# Created: September 3, 2025
# Purpose: Metric for seeing how similar and different a group of editions of
#          the same work are without the aid of an ur edition
#          NOTE: The typical usage scenario for this metric is per collection of editions

# Basis for consensus: the most expansive as agreed upon by a majority of the editions (Default: 50%)

# Imports

# Built-ins
import os
import sys
from collections import Counter
from math import ceil
from statistics import mean, median

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Custom
import aolm_data_reading
from aolm_textutilities import AOLMTextUtilities
from aolm_utilities import print_debug_header
from dq_metric import DataQualityMetric


class DatasetConsistency_RecordConsensus(DataQualityMetric):

    # Constructor and private methods

    def __init__(self, p_name, p_input, p_source_id, p_work_title, p_collection_title, p_text_json_filepath):

        super().__init__(p_name, p_input,
                         p_source_id=p_source_id,
                         p_work_title=p_work_title,
                         p_collection_title=p_collection_title,
                         p_path=p_text_json_filepath)
        
        self.m_consistency_threshold = DatasetConsistency_RecordConsensus.s_consistency_threshold

    # Properties
    @property
    def consistency_threshold(self):
        return self.m_consistency_threshold
    @consistency_threshold.setter
    def consistency_threshold(self, p_new_threshold):
        self.m_consistency_threshold = p_new_threshold
    @property
    def edition_count(self):
        return len(self.m_input)
    @property
    def output(self):
        return self.__build_output_line__()
    @property
    def eval_output(self):
        return self.__build_eval_output_line__()

    # Public methods

    def compute(self):

        # Compute 
        # (1) Tallies chapter counts,
        # (2) Calculates consensus for chapter count (ceiling of mean)
        # (3) Tallies sentence counts by chapter,
        # (4) Calculates consensus for unique sentences (all unique sentences shared by each chapter and mean frequency)
        # (5) Tallies word counts by chapter
        # (6) Calculates consensus for unique words per chapter (existence and mean frequency)

        # 0. Setup

        # A. Calculate most number of chapters in all editions
        max_chapter_count = 0
        for reader_name in self.m_input:
            if self.m_input[reader_name].chapter_count > max_chapter_count:
                max_chapter_count = self.m_input[reader_name].chapter_count

        # B. Sentence and word consensus threshold
        # NOTE: If self.m_consistency_threshold == 0.5 this is equivalent to consensus of
        # if sentence_or_word_presence_counter[sentence_or_word] > floor(self.edition_count/2)]
        # Or, in other words present in at least 50% of input editions
        consensus_threshold = int(self.edition_count * self.m_consistency_threshold)

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
        self.m_results["consensus_sentence_counts"] = { str(index): {} for index in range(1, max_chapter_count + 1) }
        self.m_results["consensus_word_counts"] = { str(index): {} for index in range(1, max_chapter_count + 1) }

        # C. Load up spaCy model with the given name
        super().load_spacymodel()

        # 1. Chapter consensus

        # A. Gather chapter counts
        for reader_name in self.m_input:
            self.m_results[reader_name]["chapter_count"] = self.m_input[reader_name].chapter_count

        # B. Measure consensus chapter count for compute() purposes - Most common chapter count as consensus
        self.m_results["consensus_chapter_count"] = Counter([self.m_results[reader_name]["chapter_count"] for reader_name in self.m_input]).most_common(1)[0][0]

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
            for reader_name in self.m_input:
                chapter_sentence_sets[reader_name] = set(list(self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)].keys()))

            # II. Get a relaxed intersection of all sentence sets - sentences that appear in at least half of the editions' chapter
            all_sentence_set = set([sentence for sentence_set in chapter_sentence_sets.values() for sentence in sentence_set])
            sentence_presence_counter = { sentence: 0 for sentence in all_sentence_set }
            for sentence in sentence_presence_counter:
                for reader_name in self.m_input:
                    if sentence in chapter_sentence_sets[reader_name]:
                        sentence_presence_counter[sentence] += 1
            consensus_sentence_set = [sentence for sentence in sentence_presence_counter if sentence_presence_counter[sentence] > consensus_threshold]
            
            # Strict intersection for consensus set
            # consensus_sentence_set = set.intersection(*list(chapter_sentence_sets.values()))

            # III. Determine the median frequency of each unique sentence in the chapter (typically should be 1)
            for sentence in consensus_sentence_set:
                frequency_list = []
                for reader_name in self.m_input:
                    if sentence in self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)]:
                        frequency_list.append(self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)][sentence])
                self.m_results["consensus_sentence_counts"][str(index)][sentence] = median(frequency_list)

        # C. Gather a set of word dictionaries for unique words of each chapter of each edition
        for index in range(1, self.m_results["consensus_chapter_count"] + 1):

            for reader_name in self.m_input:

                compared_chapter = self.m_input[reader_name].get_chapter(index)
                compared_words = AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(compared_chapter))
                compared_words = Counter(compared_words)

                self.m_results[reader_name]["word_count"]["by_chapter"][str(index)] = compared_words

        # D. Determine a consensus count of the unique words per chapter across the editions
        for index in range(1, self.m_results["consensus_chapter_count"] + 1):

            # I. Add unique words to a chapter word set
            chapter_word_sets = {} 
            for reader_name in self.m_input:
                chapter_word_sets[reader_name] = set(list(self.m_results[reader_name]["word_count"]["by_chapter"][str(index)].keys()))

            # II. Get a relaxed intersection of all word sets - words that appear in at least half of the editions' chapter
            all_word_set = set([word for word_set in chapter_word_sets.values() for word in word_set])
            word_presence_counter = { word: 0 for word in all_word_set }
            for word in word_presence_counter:
                for reader_name in self.m_input:
                    if word in chapter_word_sets[reader_name]:
                        word_presence_counter[word] += 1
            consensus_word_set = [word for word in word_presence_counter if word_presence_counter[word] > consensus_threshold]

            # Strict interesection for consensus set
            # consensus_word_set = set.intersection(*list(chapter_word_sets.values()))

            # III. Determine the median frequency of each unique word in the chapter
            for word in consensus_word_set:
                frequency_list = []
                for reader_name in self.m_input:
                    if word in self.m_results[reader_name]["word_count"]["by_chapter"][str(index)]:
                        frequency_list.append(self.m_results[reader_name]["word_count"]["by_chapter"][str(index)][word])
                self.m_results["consensus_word_counts"][str(index)][word] = median(frequency_list)
                
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

        # 0. Setup

        self.m_evaluations = {}

        # A. Calculate most number of chapters in all editions
        max_chapter_count = 0
        for reader_name in self.m_input:
            if self.m_input[reader_name].chapter_count > max_chapter_count:
                max_chapter_count = self.m_input[reader_name].chapter_count

        # NOTE: Consensus counts in results from compute may need to be split apart by reader_name/chapter in order to make sense below

        # 1. Subsubsubsubmetrics - Variance of each chapter unit (sentence, word) frequency from consensus unit frequency
        self.m_evaluations["subsubsubsubmetric"] = {

            reader_name: {
                
                "variance_from_sentence_consensus__by_chapter": { str(index): {} for index in range(1, max_chapter_count + 1) },
                "variance_from_word_consensus__by_chapter": { str(index): {} for index in range(1, max_chapter_count + 1) },
            }
            for reader_name in self.m_input
        }
        for reader_name in self.m_input:
            for index in range(1, self.m_results[reader_name]["chapter_count"] + 1):
                for sentence in self.m_results["consensus_sentence_counts"][str(index)]:
                    if sentence in self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)]:
                        self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_sentence_consensus__by_chapter"][str(index)][sentence] = \
                            self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)][sentence] - self.m_results["consensus_sentence_counts"][str(index)][sentence]  
                for word in self.m_results["consensus_word_counts"][str(index)]:
                    if word in self.m_results[reader_name]["word_count"]["by_chapter"][str(index)]:
                        self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_word_consensus__by_chapter"][str(index)][word] = \
                            self.m_results[reader_name]["word_count"]["by_chapter"][str(index)][word] - self.m_results["consensus_word_counts"][str(index)][word]
                    
        # 2. Subsubsubmetrics - Mean of variances of sentences/words for each chapter in each edition
        self.m_evaluations["subsubsubmetric"] = {

            "mean_variance_from_sentence_consensus__by_chapter": {
                reader_name: {
                    str(index): mean(list(self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_sentence_consensus__by_chapter"][str(index)].values())) if len(list(self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_sentence_consensus__by_chapter"][str(index)].values())) else 0
                        for index in range(1, max_chapter_count + 1)
                } for reader_name in self.m_input
            },

            "mean_variance_from_word_consensus__by_chapter": {
                reader_name: {
                    str(index): mean(list(self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_word_consensus__by_chapter"][str(index)].values()))  if len(list(self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_word_consensus__by_chapter"][str(index)].values())) else 0
                        for index in range(1, max_chapter_count + 1)
                } for reader_name in self.m_input
            }
        }

        # 3. Subsubmetrics - Variance of edition chapter count from consensus chapter count, and mean unit variances for each edition
        self.m_evaluations["subsubmetric"] = {

            reader_name: {

                "variance_from_chapter_consensus__by_edition": self.m_input[reader_name].chapter_count - self.m_results["consensus_chapter_count"],
                "mean_variance_from_sentence_consensus__by_edition": mean(list(self.m_evaluations["subsubsubmetric"]["mean_variance_from_sentence_consensus__by_chapter"][reader_name].values())),
                "mean_variance_from_word_consensus__by_edition": mean(list(self.m_evaluations["subsubsubmetric"]["mean_variance_from_word_consensus__by_chapter"][reader_name].values()))
            }
            for reader_name in self.m_input
        }

        # 4. Submetric - Mean of chapter variance of all editions, Mean of mean unit variances of all editions
        self.m_evaluations["submetric"] = {

            "mean_of_variance_from_chapter_consensus__by_edition": mean([self.m_evaluations["subsubmetric"][reader_name]["variance_from_chapter_consensus__by_edition"] for reader_name in self.m_input]),
            "mean_of_mean_variance_from_sentence_consensus__by_edition": mean([self.m_evaluations["subsubmetric"][reader_name]["mean_variance_from_sentence_consensus__by_edition"] for reader_name in self.m_input]),
            "mean_of_mean_variance_from_word_consensus__by_edition": mean([self.m_evaluations["subsubmetric"][reader_name]["mean_variance_from_word_consensus__by_edition"] for reader_name in self.m_input])
        }

        # 5. Metric - Mean of all three submetrics (mostly to derive a single data quality percentage, each submetric is evenly weighted here)
        self.m_evaluations["metric"] = mean(list(self.m_evaluations["submetric"].values()))

        return self.metric_evaluation
    
    # Static fields and methods
    
    # Default threshold for relaxed consensus is presence in at least half of input texts
    s_consistency_threshold = 0.5

    s_metric_name = "consistency_recordconsensus"


def main():

    # Test case: Internet Archive editions of 'Adventures of Huckleberry Finn'

    COLLECTION_ID = aolm_data_reading.IA
    COLLECTION_FULL_NAME = aolm_data_reading.huckfinn_source_fullnames[COLLECTION_ID]
    EDITION_PATH = aolm_data_reading.huckfinn_directories[COLLECTION_ID]["txt"]
    WORK_TITLE = "Adventures of Huckleberry Finn"
    
    # 1. Read in all Huckleberry finn editions from Internet Archive
    print_debug_header(f"Reading {COLLECTION_FULL_NAME} editions of {WORK_TITLE}...")
    huckfinn_textdata = { COLLECTION_ID: aolm_data_reading.read_huckfinn_text(COLLECTION_ID) }

    # 2. Compute metric
    print_debug_header(f"Computing record consensus metric for collection...")
    huckfinn_recordconsensus = DatasetConsistency_RecordConsensus(
        f"HuckFinn_{COLLECTION_ID}_Consistency_RecordConsensus",
        huckfinn_textdata[COLLECTION_ID],
        COLLECTION_ID,
        WORK_TITLE,
        aolm_data_reading.huckfinn_source_fullnames[COLLECTION_ID],
        EDITION_PATH)
    huckfinn_recordconsensus.consistency_threshold = 0.5
    huckfinn_recordconsensus.compute()
    
    # 3. Evaluate the results
    print_debug_header("Evaluating metric results...")
    huckfinn_recordconsensus.evaluate()

    print(f"Metric: {100 * huckfinn_recordconsensus.metric_evaluation}%")
    print(f"Submetrics: {huckfinn_recordconsensus.m_evaluations["submetric"]}")


if "__main__" == __name__:
    main()
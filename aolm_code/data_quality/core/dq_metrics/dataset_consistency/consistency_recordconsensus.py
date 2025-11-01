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

# Globals

EXPERIMENT_PATH = ROOT_DIR + f"{os.sep}experiments{os.sep}outputs{os.sep}"


class DatasetConsistency_RecordConsensus(DataQualityMetric):

    # Constructor and private methods

    def __init__(self, p_name, p_input, p_source_id, p_work_title, p_collection_title, p_text_json_filepath):

        super().__init__(p_name, p_input,
                         p_source_id=p_source_id,
                         p_work_title=p_work_title,
                         p_collection_title=p_collection_title,
                         p_path=p_text_json_filepath)
        
        self.m_consistency_threshold = DatasetConsistency_RecordConsensus.s_consistency_threshold      

        self.m_weight_mean_of_variance_from_chapter_consensus__by_edition = DatasetConsistency_RecordConsensus.s_weight_mean_of_variance_from_chapter_consensus__by_edition
        self.m_weight_mean_of_mean_variance_from_sentence_consensus__by_edition = DatasetConsistency_RecordConsensus.s_weight_mean_of_mean_variance_from_sentence_consensus__by_edition
        self.m_mean_of_mean_variance_from_word_consensus__by_edition = DatasetConsistency_RecordConsensus.s_weight_mean_of_mean_variance_from_word_consensus__by_edition


    def __build_eval_output_line__(self):

        # self.m_evaluations["subsubsubsubmetric"]
        # edition_name,chapter,variance_from_sentence_consensus__by_chapter,variance_from_word_consensus__by_chapter

        header = "edition_name,chapter,variance_from_sentence_consensus__by_chapter,variance_from_word_consensus__by_chapter"
        output_lines = [f"{header}\n"]

        max_chapter_count = 0
        for reader_name in self.m_input:
            if self.m_input[reader_name].chapter_count > max_chapter_count:
                max_chapter_count = self.m_input[reader_name].chapter_count        

        for reader_name in self.m_input:
            for index in range(1, max_chapter_count + 1):
                
                edition_name = reader_name
                chapter = str(index)
                # sentence_variances = self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_sentence_consensus__by_chapter"][str(index)]
                # word_variances = self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_word_consensus__by_chapter"][str(index)]

                # avg_sentence_variance = 0 if not len(sentence_variances) else mean(sentence_variances.values())
                # avg_word_variance = 0 if not len(word_variances) else mean(word_variances.values())

                # output_lines.append(
                #     f"{edition_name},{chapter},{avg_sentence_variance},{avg_word_variance}\n"
                # )                

                mean_sentence_variance = self.m_evaluations["subsubsubmetric"]["mean_variance_from_sentence_consensus__by_chapter"][edition_name][chapter]
                mean_word_variance = self.m_evaluations["subsubsubmetric"]["mean_variance_from_word_consensus__by_chapter"][edition_name][chapter]

                output_lines.append(
                    f"{edition_name},{chapter},{mean_sentence_variance},{mean_word_variance}\n"
                )                

        return output_lines

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
    
    @property
    def chapter_submetric_weight(self):
        return self.m_weight_mean_of_variance_from_chapter_consensus__by_edition
    @chapter_submetric_weight.setter
    def chapter_submetric_weight(self, p_new_weight):
        self.m_weight_mean_of_variance_from_chapter_consensus__by_edition = p_new_weight
    @property
    def sentence_submetric_weight(self):
        return self.m_weight_mean_of_mean_variance_from_sentence_consensus__by_edition
    @sentence_submetric_weight.setter
    def sentence_submetric_weight(self, p_new_weight):
        self.m_weight_mean_of_mean_variance_from_sentence_consensus__by_edition = p_new_weight
    @property
    def word_submetric_weight(self):
        return self.m_weight_mean_of_mean_variance_from_word_consensus__by_edition
    @word_submetric_weight.setter
    def word_submetric_weight(self, p_new_weight):
        self.m_weight_mean_of_mean_variance_from_word_consensus__by_edition = p_new_weight

    # Public methods

    def compute(self):

        # Compute 
        # (1) Tallies chapter counts,
        # (2) Calculates consensus for chapter count (ceiling of mean)
        # (3) Tallies sentence counts by chapter,
        # (4) Calculates consensus for unique sentences (all unique sentences shared by each chapter and mean frequency)
        # (5) Tallies word counts by chapter
        # (6) Calculates consensus for unique words per chapter (existence and mean frequency)

        import numpy as np

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
        # New NOTE: Threshold is dynamically calculated below now based on active edition count
        # consensus_threshold = int(self.edition_count * self.m_consistency_threshold)

        # B. Reset results
        self.m_results = {
            
            reader_name: {

                "chapter_count": 0,
                "sentence_count": {
                    "by_chapter": { str(i): np.nan for i in range(1, max_chapter_count + 1) }
                },
                "word_count": {
                    "by_chapter": { str(i): np.nan for i in range(1, max_chapter_count + 1) }
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
        print("===========================")
        print(f"CONSENSUS CHAPTER COUNT: {self.m_results['consensus_chapter_count']}")
        cons_chapt_dict = { reader_name: self.m_results[reader_name]["chapter_count"] for reader_name in self.m_input }
        print(f"Chapter counts: {cons_chapt_dict}")
        print("===========================")

        # 2. Unique sentence consensus (using spaCy's sentence model)
        for index in range(1, self.m_results["consensus_chapter_count"] + 1):

            # A. Missing chapter safeguards

            # Determine active editions for this chapter
            active_editions = [reader_name for reader_name in self.m_input if self.m_input[reader_name].get_chapter(index)]
            if not active_editions:
                
                # No edition has this chapter; mark consensus as None and skip
                self.m_results["consensus_sentence_counts"][str(index)] = None
                self.m_results["consensus_word_counts"][str(index)] = None
                continue

            # Adjust threshold to active editions only
            effective_threshold = ceil(len(active_editions) * self.m_consistency_threshold)            

            # B. Gather a set of sentence dictionaries for unique sentences of each active edition
            for reader_name in self.m_input:             

                # Get sentences from chapter strings via spaCy
                compared_chapter = self.m_input[reader_name].get_chapter(index)
                compared_spacy_chapter = self.m_spacymodel("\n".join(compared_chapter))
                compared_sentence_dict = AOLMTextUtilities.get_sentence_dict_from_spacy_doc(compared_spacy_chapter)

                self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)] = compared_sentence_dict

            # C. Determine a consensus count of the unique sentences for this chapter

            # I. Add unique sentences to a chapter sentence set
            chapter_sentence_sets = {} 
            for reader_name in active_editions:
                chapter_sentence_sets[reader_name] = set(list(self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)].keys()))

            # II. Get a relaxed intersection of all sentence sets - sentences that appear in at least half of the editions' chapter
            all_sentence_set = set([sentence for sentence_set in chapter_sentence_sets.values() for sentence in sentence_set])
            sentence_presence_counter = { sentence: 0 for sentence in all_sentence_set }
            for sentence in sentence_presence_counter:
                for reader_name in active_editions:
                    if sentence in chapter_sentence_sets[reader_name]:
                        sentence_presence_counter[sentence] += 1
            consensus_sentence_set = [sentence for sentence in sentence_presence_counter if sentence_presence_counter[sentence] >= effective_threshold]
            
            # Strict intersection for consensus set
            # consensus_sentence_set = set.intersection(*list(chapter_sentence_sets.values()))

            # D. Determine the median frequency of each unique sentence in the chapter (typically should be 1)
            for sentence in consensus_sentence_set:
                frequency_list = [self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)][sentence]
                          for reader_name in active_editions if sentence in self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)]]
                if frequency_list:
                    self.m_results["consensus_sentence_counts"][str(index)][sentence] = float(median(frequency_list))
                else:
                    # This should not happen, but mark as None for safety
                    self.m_results["consensus_sentence_counts"][str(index)][sentence] = np.nan

        # 3. Unique word consensus
        for index in range(1, self.m_results["consensus_chapter_count"] + 1):

            # A. Missing chapter safeguards

            # Determine active editions for this chapter
            active_editions = [reader_name for reader_name in self.m_input if self.m_input[reader_name].get_chapter(index)]
            if not active_editions:
                continue

            # Adjust threshold to active editions only
            effective_threshold = ceil(len(active_editions) * self.m_consistency_threshold)            

            # B. Gather a set of word dictionaries for unique words of each chapter of each edition
            for reader_name in active_editions:

                compared_chapter = self.m_input[reader_name].get_chapter(index)
                compared_words = AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(compared_chapter))
                compared_words = [AOLMTextUtilities.clean_string(word) for word in compared_words]

                self.m_results[reader_name]["word_count"]["by_chapter"][str(index)] = Counter(compared_words)

            # C. Determine a consensus count of the unique words per chapter across the editions

            # I. Add unique words to a chapter word set
            chapter_word_sets = {} 
            for reader_name in active_editions:
                chapter_word_sets[reader_name] = set(list(self.m_results[reader_name]["word_count"]["by_chapter"][str(index)].keys()))

            # II. Get a relaxed intersection of all word sets - words that appear in at least half of the editions' chapter
            all_word_set = set([word for word_set in chapter_word_sets.values() for word in word_set])
            word_presence_counter = { word: 0 for word in all_word_set }
            for word in word_presence_counter:
                for reader_name in active_editions:
                    if word in chapter_word_sets[reader_name]:
                        word_presence_counter[word] += 1
            consensus_word_set = [word for word in word_presence_counter if word_presence_counter[word] >= effective_threshold]

            # Strict interesection for consensus set
            # consensus_word_set = set.intersection(*list(chapter_word_sets.values()))

            # III. Determine the median frequency of each unique word in the chapter
            for word in consensus_word_set:
                frequency_list = [self.m_results[reader_name]["word_count"]["by_chapter"][str(index)][word]
                    for reader_name in active_editions if word in self.m_results[reader_name]["word_count"]["by_chapter"][str(index)]]
                if frequency_list:
                    self.m_results["consensus_word_counts"][str(index)][word] = float(median(frequency_list))
                else:
                    self.m_results["consensus_word_counts"][str(index)][word] = np.nan
       
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

        import numpy as np

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

            if "dli.ernet.235649-HuckFinn" in reader_name:
                x = 0
            
            for index in range(1, max_chapter_count + 1):

                consensus_sentences = self.m_results["consensus_sentence_counts"].get(str(index))
                consensus_words = self.m_results["consensus_word_counts"].get(str(index))

                # Skip missing chapters entirely
                if consensus_sentences is None and consensus_words is None:
                    continue

                # Sentence variance
                if consensus_sentences is not None:
                    chapter_dict = self.m_results[reader_name]["sentence_count"]["by_chapter"].get(str(index))
                    if isinstance(chapter_dict, dict):
                        for sentence, consensus_count in consensus_sentences.items():
                            actual_count = chapter_dict.get(sentence)
                            if actual_count is not None:
                                self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_sentence_consensus__by_chapter"][str(index)][sentence] = \
                                    actual_count - consensus_count
                            else:
                                self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_sentence_consensus__by_chapter"][str(index)][sentence] = np.nan
                else:
                    # Chapter is missing (np.nan), mark all consensus sentences as NaN
                    for sentence in consensus_sentences:
                        self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_sentence_consensus__by_chapter"][str(index)][sentence] = np.nan

                # Word variance
                if consensus_words is not None:
                    chapter_dict = self.m_results[reader_name]["word_count"]["by_chapter"].get(str(index))
                    if isinstance(chapter_dict, dict):
                        for word, consensus_count in consensus_words.items():
                            actual_count = chapter_dict.get(word)
                            if actual_count is not None:
                                self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_word_consensus__by_chapter"][str(index)][word] = \
                                    actual_count - consensus_count
                            else:
                                self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_word_consensus__by_chapter"][str(index)][word] = np.nan
                else:
                    # Chapter is missing (np.nan), mark all consensus words as NaN
                    for word in consensus_words:
                        self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_word_consensus__by_chapter"][str(index)][word] = np.nan


                    
        # 2. Subsubsubmetrics - Mean of variances of sentences/words for each chapter in each edition
        self.m_evaluations["subsubsubmetric"] = {

            "mean_variance_from_sentence_consensus__by_chapter": {
                reader_name: {
                    str(index): np.nanmean(list(self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_sentence_consensus__by_chapter"][str(index)].values()))
                        for index in range(1, max_chapter_count + 1)
                } for reader_name in self.m_input
            },

            "mean_variance_from_word_consensus__by_chapter": {
                reader_name: {
                    str(index): np.nanmean(list(self.m_evaluations["subsubsubsubmetric"][reader_name]["variance_from_word_consensus__by_chapter"][str(index)].values()))
                        for index in range(1, max_chapter_count + 1)
                } for reader_name in self.m_input
            }
        }

        # 3. Subsubmetrics - Variance of edition chapter count from consensus chapter count, and mean unit variances for each edition
        self.m_evaluations["subsubmetric"] = {

            reader_name: {

                "variance_from_chapter_consensus__by_edition": self.m_input[reader_name].chapter_count - self.m_results["consensus_chapter_count"],
                "mean_variance_from_sentence_consensus__by_edition": np.nanmean(list(self.m_evaluations["subsubsubmetric"]["mean_variance_from_sentence_consensus__by_chapter"][reader_name].values())),
                "mean_variance_from_word_consensus__by_edition": np.nanmean(list(self.m_evaluations["subsubsubmetric"]["mean_variance_from_word_consensus__by_chapter"][reader_name].values()))
            }
            for reader_name in self.m_input
        }

        # 4. Submetric - Mean of chapter variance of all editions, Mean of mean unit variances of all editions
        self.m_evaluations["submetric"] = {

            "mean_of_variance_from_chapter_consensus__by_edition": np.nanmean([self.m_evaluations["subsubmetric"][reader_name]["variance_from_chapter_consensus__by_edition"] for reader_name in self.m_input]),
            "mean_of_mean_variance_from_sentence_consensus__by_edition": np.nanmean([self.m_evaluations["subsubmetric"][reader_name]["mean_variance_from_sentence_consensus__by_edition"] for reader_name in self.m_input]),
            "mean_of_mean_variance_from_word_consensus__by_edition": np.nanmean([self.m_evaluations["subsubmetric"][reader_name]["mean_variance_from_word_consensus__by_edition"] for reader_name in self.m_input]),

            # NOTE: Chapter coverage is more about completeness than consensus. It remains a separate submetric
            "coverage": { reader_name: self.m_input[reader_name].chapter_count / self.m_results["consensus_chapter_count"] for reader_name in self.m_input }            
        }

        # A. Calculate the average chapter coverage
        self.m_evaluations["submetric"]["mean_coverage"] = np.nanmean(
            list(self.m_evaluations["submetric"]["coverage"].values())
        )

        # 5. Metric - Mean of all three submetrics (mostly to derive a single data quality percentage, each submetric is evenly weighted here)
        # NOTE: Absolute value because variances can be negative
        self.m_evaluations["metric"] = abs(np.nanmean([
            
            self.m_evaluations["submetric"]["mean_of_variance_from_chapter_consensus__by_edition"],
            self.m_evaluations["submetric"]["mean_of_mean_variance_from_sentence_consensus__by_edition"],
            self.m_evaluations["submetric"]["mean_of_mean_variance_from_word_consensus__by_edition"]
            
        ]))

        return self.metric_evaluation   
    
    # Static fields and methods
    
    # Default threshold for relaxed consensus is presence in at least half of input texts [0,1]
    s_consistency_threshold = 0.5

    # Default weights for determining the metric value from the submetrics
    s_weight_mean_of_variance_from_chapter_consensus__by_edition = 0.3,
    s_weight_mean_of_mean_variance_from_sentence_consensus__by_edition = 0.25
    s_weight_mean_of_mean_variance_from_word_consensus__by_edition = 0.45 

    s_metric_name = "consistency_recordconsensus"


# Test script helpers

def get_edition_shortname_from_metadata(p_text_json_filename):

    import json

    short_name = p_text_json_filename

    with open("/Users/weirdbeard/Documents/school/aolm_full/experiments/chapter1/huckfinneditions_filenames2fullnames.json", "r") as input_file:
        json_data = json.load(input_file)

    for key in json_data:
        if key in p_text_json_filename:
            short_name = json_data[key]["short_name"]
            break

    return short_name

def get_publication_year(p_edition_short_name):

    publication_year = ""

    if "gutenberg" in p_edition_short_name:
        publication_year = p_edition_short_name[p_edition_short_name.rfind("_") + 1:]
    else:
        for index in range(0, len(p_edition_short_name)):
            if p_edition_short_name[index].isdigit():
                publication_year = p_edition_short_name[index:index + p_edition_short_name[index:].find("_")]
                break

    return publication_year


# Test script visualization

def plot_heatmap(p_chart_title, p_metric_name, p_data):

    import numpy as np
    import matplotlib.pyplot as plt    

    # Editions of the novel (sorted by publication year)
    editions = list(p_data.keys())
    editions = [(get_publication_year(edition_short_name), edition_short_name) for edition_short_name in editions]
    editions.sort(key=lambda x: x[0])
    editions = [edition_tuple[1] for edition_tuple in editions]
    n_editions = len(editions)
    n_chapters = len(p_data[editions[0]])

    # Fill in data
    data = np.zeros((n_editions, n_chapters))
    for index in range(n_editions):
        for index2 in range(n_chapters):
            data[index, index2] = p_data[editions[index]][index2]

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(data, aspect='auto')

    # Set axis labels
    ax.set_xticks(np.arange(n_chapters))
    ax.set_xticklabels(np.arange(1, n_chapters + 1))
    ax.set_yticks(np.arange(n_editions))
    ax.set_yticklabels(editions)

    # Rotate x-axis labels for readability
    plt.setp(ax.get_xticklabels(), rotation=90, ha="center")

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(p_metric_name)

    ax.set_title(p_chart_title)
    ax.set_xlabel("Chapter")
    ax.set_ylabel("Edition")

    plt.tight_layout()
    plt.show()

def plot_results(p_results_filepath, p_ur_chapter_count, p_count_type, p_count_column):

    import csv

    # 1. Store all edition record count to control records results for sentences and words by chapter
    editions = {}
    with open(p_results_filepath, "r") as results_file:
    
        csv_reader = csv.DictReader(results_file)

        for row in csv_reader:

            # Skip header
            if "edition_name" == row["edition_name"]:
                continue

            # edition_name,chapter_name,count_type,count
            edition_name = get_edition_shortname_from_metadata(row["edition_name"])
            chapter_name = row["chapter"]
            count_type = p_count_type
            count = float(row[p_count_column])

            if edition_name not in editions:
                editions[edition_name] = {
                    "sentences": [0] * p_ur_chapter_count,
                    "words": [0] * p_ur_chapter_count
                }

            editions[edition_name][count_type][int(chapter_name) - 1] = count

        # 2. Plot a 2D heatmap of the chapters of each edition by sentence data quality
        if "sentences" == p_count_type:
            plot_heatmap(
                "Mean Sentence Variance by Chapter in Internet Archive Editions of 'Adventures of Huckleberry Finn'",
                "Record Consistency data quality",
                { edition_name: editions[edition_name]["sentences"] for edition_name in editions }
            )
        elif "words" == p_count_type:  
            plot_heatmap(
                "Mean Word Varianbce by Chapter in Internet Archive Editions of 'Adventures of Huckleberry Finn'",
                "Record consistency data quality",
                { edition_name: editions[edition_name]["words"] for edition_name in editions }
            )


# Main script

def main():

    plot_data = True
    if plot_data:

        plot_results(EXPERIMENT_PATH + "huckfinn_ia_subx4metric.csv", 43, "words", "variance_from_word_consensus__by_chapter")
        # plot_results(EXPERIMENT_PATH + "huckfinn_ia_subx4metric.csv", 43, "sentences", "variance_from_sentence_consensus__by_chapter")

        return

    # Test case: Internet Archive editions of 'Adventures of Huckleberry Finn'

    COLLECTION_ID = aolm_data_reading.PG
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

    # 4. Output the metric evaluations
    print(f"Metric: {100 * huckfinn_recordconsensus.metric_evaluation}%")
    print(f"Submetrics: {huckfinn_recordconsensus.m_evaluations["submetric"]}")

    output_lines = huckfinn_recordconsensus.__build_eval_output_line__()
    with open(EXPERIMENT_PATH + "huckfinn_ia_subx4metric.csv", "w") as output_file:
        for line in output_lines:
            output_file.write(line)    


if "__main__" == __name__:
    main()
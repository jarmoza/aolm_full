# Author: Jonathan Armoza
# Created: January 11, 2025
# Purpose: Data quality metric child class for Dataset completeness - Record
#          count to Control Record metrics

# Imports

# Built-ins
from collections import Counter
from statistics import mean

# Custom
from aolm_textutilities import AOLMTextUtilities
from dq_metric import DataQualityMetric

class DatasetCompleteness_RecordCountsToControlRecords(DataQualityMetric):

    def __init__(self, p_name, p_input):

        super().__init__(p_name, p_input)

    def compute(self):

        # Experiment 2 - Text Quality
        # DQ Metric Dataset Completeness - Record Counts

        # 0. Setup
        self.m_results = {
            
            reader_name: {

                "chapter_count": {},
                "sentence_count": {
                    "by_chapter": {}
                },
                "word_count": {
                    "by_chapter": {}
                }
            } for reader_name in self.m_input if self.m_urtext_name != reader_name
        }    

        # 1. Chapter count

        # A. Chapter count comparison between self.m_urtext_name and compared editions

        # Does a text contain all the chapters of the Ur copy of that text?
        # print(f"Ur text chapter count: {self.m_input[self.m_urtext_name].chapter_count}")

        # Chapters to run through (43 from Ur copy, self.m_urtext_name)
        ur_chapter_count = self.m_input[self.m_urtext_name].chapter_count

        # Chapter counts of compared editions
        for reader_name in self.m_results:
            if self.m_urtext_name == reader_name:
                continue
            self.m_results[reader_name]["chapter_count"] = 100.0 * self.m_input[reader_name].chapter_count / ur_chapter_count

        # 2. Sentence count (using spaCy's sentence model)

        # Get sentences from chapter strings via spaCy

        # A. Load up spaCy model with the given name
        super().load_spacymodel()

        # B. Compare sentences of each chapter of Ur text with each compared edition
        for index in range(1, ur_chapter_count + 1):

            # I. Read the ur chapter
            ur_spacy_chapter = self.m_spacymodel("\n".join(self.m_input[self.m_urtext_name].get_chapter(index)))

            # II. Create a dictionary of unique sentence counts of the ur chapter
            ur_sentence_dict = AOLMTextUtilities.get_sentence_dict_from_spacy_doc(ur_spacy_chapter)

            # III. Compare the ur chapter sentences to those in each compared edition
            for reader_name in self.m_input:
                if self.m_urtext_name == reader_name:
                    continue

                compared_spacy_chapter = self.m_spacymodel("\n".join(self.m_input[reader_name].get_chapter(index)))
                compared_sentence_dict = AOLMTextUtilities.get_sentence_dict_from_spacy_doc(compared_spacy_chapter)
                
                self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)] = \
                    AOLMTextUtilities.dictionaries_percent_equal(ur_sentence_dict, compared_sentence_dict)

        # 3. Sentence count
        for index in range(1, ur_chapter_count + 1):

            # I. Read the ur chapter's words
            ur_chapter = self.m_input[self.m_urtext_name].get_chapter(index)
            ur_words = AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(ur_chapter))
            ur_words = Counter(ur_words)

            # II. Compare the ur chapter words to those in each compared edition
            for reader_name in self.m_input:
                if self.m_urtext_name == reader_name:
                    continue

                compared_chapter = self.m_input[reader_name].get_chapter(index)
                compared_words = AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(compared_chapter))
                compared_words = Counter(compared_words)
                
                self.m_results[reader_name]["word_count"]["by_chapter"][str(index)] = \
                    AOLMTextUtilities.dictionaries_percent_equal(ur_words, compared_words)

        return self.m_results

    def evaluate(self, p_edition=None):

        # 1. Calculate evaluations of subsubmetrics
        self.m_evaluations["subsubmetric"] = { 
            reader_name: {
                "chapter_count": self.m_results[reader_name]["chapter_count"],
                "sentence_count": mean(self.m_results[reader_name]["sentence_count"]["by_chapter"].values()),
                "word_count": mean(self.m_results[reader_name]["word_count"]["by_chapter"].values())
            }
            for reader_name in self.m_results 
        }

        # 2. Calculate evaluation of submetrics
        self.m_evaluations["submetric"] = {

            "chapter_count": mean([self.m_evaluations["subsubmetric"][reader_name]["chapter_count"] for reader_name in self.m_evaluations["subsubmetric"] if self.m_urtext_name != reader_name]),
            "sentence_count": mean([self.m_evaluations["subsubmetric"][reader_name]["sentence_count"] for reader_name in self.m_evaluations["subsubmetric"] if self.m_urtext_name != reader_name]),
            "word_count": mean([self.m_evaluations["subsubmetric"][reader_name]["word_count"] for reader_name in self.m_evaluations["subsubmetric"] if self.m_urtext_name != reader_name]),
        }

        # 3. Metric is weighted mean of submetrics
        self.m_evaluations["metric"] = mean(self.m_evaluations["submetric"].values())

        return self.metric_evaluation
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

        # A. Chapter count comparison between self.m_urtext_name and PG editions

        # Does a text contain all the chapters of the Ur copy of that text?
        print(f"Ur text chapter count: {self.m_input[self.m_urtext_name].chapter_count}")

        # Chapters to run through (43 from Ur copy, self.m_urtext_name)
        ur_chapter_count = self.m_input[self.m_urtext_name].chapter_count

        # Chapter counts of PG editions
        for reader_name in self.m_results:
            if self.m_urtext_name == reader_name:
                continue
            self.m_results[reader_name]["chapter_count"] = 100.0 * self.m_input[reader_name].chapter_count / ur_chapter_count

        # 2. Sentence count (using spaCy's sentence model)

        # Get sentences from chapter strings via spaCy

        # A. Load up spaCy model with the given name
        self.__load_spacymodel()

        # B. Compare sentences of each chapter of Ur text with each PG edition
        for index in range(1, ur_chapter_count + 1):

            # I. Read the ur chapter
            ur_spacy_chapter = self.m_spacymodel("\n".join(self.m_input[self.m_urtext_name].get_chapter(index)))

            # II. Create a dictionary of unique sentence counts of the ur chapter
            ur_sentence_dict = AOLMTextUtilities.get_sentence_dict_from_spacy_doc(ur_spacy_chapter)

            # III. Compare the ur chapter sentences to those in each PG edition
            for reader_name in self.m_input:
                if self.m_urtext_name == reader_name:
                    continue

                pg_spacy_chapter = self.m_spacymodel("\n".join(self.m_input[reader_name].get_chapter(index)))
                pg_sentence_dict = AOLMTextUtilities.get_sentence_dict_from_spacy_doc(pg_spacy_chapter)
                
                self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)] = \
                    AOLMTextUtilities.dictionaries_percent_equal(ur_sentence_dict, pg_sentence_dict)
                
        # for reader_name in self.m_results:
        #     print("=" * 80)
        #     print(f"{reader_name}")
        #     for chapter_index in self.m_results[reader_name]["sentence_count"]["by_chapter"]:
        #         print(f"chapter {chapter_index}: {self.m_results[reader_name]["sentence_count"]["by_chapter"][chapter_index]}")
        #     print("\n")

        # 3. Sentence count
        for index in range(1, ur_chapter_count + 1):

            # I. Read the ur chapter's words
            ur_chapter = self.m_input[self.m_urtext_name].get_chapter(index)
            ur_words = AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(ur_chapter))
            ur_words = Counter(ur_words)

            # II. Compare the ur chapter words to those in each PG edition
            for reader_name in self.m_input:
                if self.m_urtext_name == reader_name:
                    continue

                pg_chapter = self.m_input[reader_name].get_chapter(index)
                pg_words = AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(pg_chapter))
                pg_words = Counter(pg_words)
                
                self.m_results[reader_name]["word_count"]["by_chapter"][str(index)] = \
                    AOLMTextUtilities.dictionaries_percent_equal(ur_words, pg_words)
                
        # for reader_name in self.m_results:
        #     print("=" * 80)
        #     print(f"{reader_name}")
        #     for chapter_index in self.m_results[reader_name]["word_count"]["by_chapter"]:
        #         print(f"chapter {chapter_index}: {self.m_results[reader_name]["word_count"]["by_chapter"][chapter_index]}")
        #     print("\n")    

        # NEXT UP:
        # (1) Review sentence comparison function
        # (2) Finish out text record count dq metric
        # (3) Visualize text record count and metadata suffiency submetrics and write about them

        # # C. Given that, what percent of chapters are complete in this text?
        # acceptable_completion_percent = p_dqmetric_instance.metric_min
        # passable_chapters = 0

        return self.m_results

    def evaluate(self, p_edition=None):

        # self.m_results = { 
        #     reader_name: {
        #         "chapter_count": {},
        #         "sentence_count": {
        #             "by_chapter": {}
        #         },
        #         "word_count": {
        #             "by_chapter": {}
        #         }
        #     } for reader_name in huckfinn_text_readers if MTPO != reader_name
        # }

        # 1. Calculate evaluations of subsubmetrics
        self.subsubmetric_evaluations = { 
            reader_name: {
                "chapter_count": self.m_results[reader_name]["chapter_count"],
                "sentence_count": mean(self.m_results[reader_name]["sentence_count"]["by_chapter"].values()),
                "word_count": mean(self.m_results[reader_name]["word_count"]["by_chapter"].values())
            }
            for reader_name in self.m_results 
        }

        # 2. Calculate evaluation of submetrics
        self.submetric_evaluations = {

            "chapter_count": mean([self.subsubmetric_evaluations[reader_name]["chapter_count"] for reader_name in self.subsubmetric_evaluations if self.m_urtext_name != reader_name]),
            "sentence_count": mean([self.subsubmetric_evaluations[reader_name]["sentence_count"] for reader_name in self.subsubmetric_evaluations if self.m_urtext_name != reader_name]),
            "word_count": mean([self.subsubmetric_evaluations[reader_name]["word_count"] for reader_name in self.subsubmetric_evaluations if self.m_urtext_name != reader_name]),
        }

        # 3. Metric is weighted mean of submetrics
        self.metric_evaluation = mean(self.submetric_evaluations.values())

        return self.metric_evaluation
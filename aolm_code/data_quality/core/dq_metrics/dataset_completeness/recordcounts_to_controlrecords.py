# Author: Jonathan Armoza
# Created: January 11, 2025
# Purpose: Data quality metric child class for Dataset completeness - Record
#          count to Control Record metrics

# Imports

# Built-ins
import os
from collections import Counter
from statistics import mean

# Custom
from aolm_textutilities import AOLMTextUtilities
from dq_metric import DataQualityMetric

class DatasetCompleteness_RecordCountsToControlRecords(DataQualityMetric):

    def __init__(self, p_name, p_input, p_source_id, p_work_title, p_collection_title, p_text_json_filepath, p_baseline_source_id):

        super().__init__(p_name, p_input,
                         p_source_id=p_source_id,
                         p_work_title=p_work_title,
                         p_collection_title=p_collection_title,
                         p_path=p_text_json_filepath,
                         p_baseline_source_id=p_baseline_source_id)
        
    def __build_eval_output_line__(self, p_return_dict=False):

        key_value_map = { key: None for key in DataQualityMetric.s_build_output_line_keys }

        # 1. Record counts to control records-specific evaluation keys
        key_value_map.update(self.m_evaluations)

        # 2. Base data quality metric evaluation keys
        key_value_map["source"] = self.m_source_id
        key_value_map["work_title"] = self.m_work_title
        key_value_map["path"] = self.m_path
        key_value_map["edition_title"] = os.path.basename(os.path.splitext(self.m_path)[0]) if len(os.path.basename(self.m_path)) else self.m_source_id
        key_value_map["collection_title"] = self.m_collection_title
        key_value_map["compared_against"] = self.baseline_source_id
        key_value_map["filename"] = os.path.basename(self.m_path)
        key_value_map["filepath"] = self.m_path
        key_value_map["metric"] = DatasetCompleteness_RecordCountsToControlRecords.s_metric_name
        key_value_map["value"] = self.m_evaluations["metric"]

    def __build_output_line__(self):

        key_value_map = {
            
            "source": self.m_source_id,
            "work_title": self.m_work_title,
            "path": self.m_path,
            "edition_title": os.path.basename(os.path.splitext(self.m_path)[0]) if len(os.path.basename(self.m_path)) else self.m_source_id,
            "metric": DatasetCompleteness_RecordCountsToControlRecords.s_metric_name,
            "value": self.m_evaluations["metric"],
            "compared_against": self.baseline_source_id,
            "filename": os.path.basename(self.m_path),
            "filepath": self.m_path
        }

        line_dict = { key: key_value_map.get(key, None) for key in DataQualityMetric.s_build_output_line_keys }
        line_str_array = [line_dict[key] for key in DataQualityMetric.s_build_output_line_keys]

        return ",".join(map(str, line_str_array)) + "\n"
    
    @property
    def output(self):
        return self.__build_output_line__()
    @property
    def eval_output(self):
        return self.__build_eval_output_line__()
    @property
    def eval_output_header(self):
        
        # Base column names for DatasetCompleteness_RecordCountsToControlRecords
        column_names = list(DataQualityMetric.s_build_output_line_keys)
        column_names.extend(DatasetCompleteness_RecordCountsToControlRecords.s_eval_output_line_keys)

        # Column names for this metric instance        
        # for work_title in self.m_results:
        #     column_names.append(f"subsubmetric_{work_title}__chapter_count")
        #     column_names.append(f"subsubmetric_{work_title}__sentence_count")
        #     column_names.append(f"subsubmetric_{work_title}__word_count")
        if 1 == len(self.m_results):
            column_names.append(f"subsubmetric__chapter_count")
            column_names.append(f"subsubmetric__sentence_count")
            column_names.append(f"subsubmetric__word_count")


        return ",".join(column_names) + "\n"


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

        # 3. Word count
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
    
    # Static fields and methods

    s_eval_output_line_keys = [
        "source",
        "work_title",
        "path",
        "edition_title",
        "compared_against",
        "filename",
        "filepath",
        "metric",
        "submetric__chapter_count",
        "submetric__sentence_count",
        "submetric__word_count"
    ]

    s_metric_name = "record_counts_to_control"

    # @staticmethod
    # def write_eval_output_header(p_output_file):
    #     p_output_file.write(",".join(DatasetCompleteness_RecordCountsToControlRecords.s_eval_output_line_keys) + "\n")
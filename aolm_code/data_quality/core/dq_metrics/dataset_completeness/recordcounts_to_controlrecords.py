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
        
    def __build_eval_output_line__(self):

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

        return key_value_map

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
    
    def __build_results_full_count_lines__(self, p_include_header):

        results_header = ",".join(["edition_name", "chapter_name",  "count_type", "percent"])
        results_lines = [results_header] if p_include_header else []        

        # Results chapter by chapter here for sentences and words
        for reader_name in self.m_results:
            for chapter_name in self.m_results[reader_name]["sentence_count"]["by_chapter"]:
                sc_line = ",".join([reader_name, chapter_name, "sentences", str(self.m_results[reader_name]["sentence_count"]["by_chapter"][chapter_name])  ])
                results_lines.append(sc_line)
            for chapter_name in self.m_results[reader_name]["word_count"]["by_chapter"]:
                wc_line = ",".join([reader_name, chapter_name, "words", str(self.m_results[reader_name]["word_count"]["by_chapter"][chapter_name])])
                results_lines.append(wc_line)            

        return results_lines

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

    def results_full_counts(self, p_include_header=False):
        return self.__build_results_full_count_lines__(p_include_header)
    
    def compute(self):

        # 0. Setup

        # A. Reset results
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

        # B. Load up spaCy model with the given name
        super().load_spacymodel()

        # 1. Chapter count comparison between ur text and compared editions
        # e.g. Does an edition of a text contain all the chapters of the ur copy of that text?

        # A. Chapters to run through (N chapters from ur copy, self.m_urtext_name)
        ur_chapter_count = self.m_input[self.m_urtext_name].chapter_count

        # B. Chapter counts of compared editions
        for reader_name in self.m_results:
            if self.m_urtext_name == reader_name:
                continue
            self.m_results[reader_name]["chapter_count"] = 100.0 * self.m_input[reader_name].chapter_count / ur_chapter_count

        # 2. Sentence count (using spaCy's sentence model) and word count

        # Get sentences from chapter strings via spaCy

        # A. Compare sentences and words of each chapter of Ur text with each compared edition
        for index in range(1, ur_chapter_count + 1):

            # I. Read the ur chapter
            ur_chapter = self.m_input[self.m_urtext_name].get_chapter(index)
            ur_spacy_chapter = self.m_spacymodel("\n".join(ur_chapter))

            # II. Create a dictionary of unique sentence counts of the ur chapter
            ur_sentence_dict = AOLMTextUtilities.get_sentence_dict_from_spacy_doc(ur_spacy_chapter)

            # III. Compare the ur chapter sentences to those in each compared edition
            for reader_name in self.m_input:
                if self.m_urtext_name == reader_name:
                    continue

                # a. Missing chapter safeguard
                compared_chapter = self.m_input[reader_name].get_chapter(index)

                # if 16 == index:
                #     self.output_chapter_comp_to_file(ur_chapter, self.m_urtext_name,
                #                                      compared_chapter, reader_name)

                if not compared_chapter:
                    # Penalize missing chapter
                    self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)] = 0.0
                    self.m_results[reader_name]["word_count"]["by_chapter"][str(index)] = 0.0
                    continue
                
                # b. Sentence comparison
                compared_spacy_chapter = self.m_spacymodel("\n".join(compared_chapter))
                compared_sentence_dict = AOLMTextUtilities.get_sentence_dict_from_spacy_doc(compared_spacy_chapter)
                self.m_results[reader_name]["sentence_count"]["by_chapter"][str(index)] = \
                    AOLMTextUtilities.dictionaries_percent_equal(ur_sentence_dict, compared_sentence_dict)
                
                # c. Word comparison
                ur_words = Counter(AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(ur_chapter)))
                compared_words = Counter(AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(compared_chapter)))
                self.m_results[reader_name]["word_count"]["by_chapter"][str(index)] = \
                    AOLMTextUtilities.dictionaries_percent_equal(ur_words, compared_words)
                
        return self.m_results

    def evaluate(self, p_edition=None):

        # 1. Calculate proportional weights for sentence and word counts for each chapter

        # NOTE: Each chapter of the ur text gets a weight determined by its portion of the
        # overall count of units from the overall book, either sentences or words. Then when
        # the percent completeness of a chapter is determined, that percent is multiplied by
        # that ur text chapter weight

        # A. Chapters to run through (N chapters from ur copy, self.m_urtext_name)
        ur_chapter_count = self.m_input[self.m_urtext_name].chapter_count

        # B. Tally unique sentences and words in each chapter of the ur edition
        ur_sentence_counts = {}
        ur_word_counts = {}        
        for index in range(1, ur_chapter_count + 1):

            # I. Read the ur chapter
            ur_chapter = self.m_input[self.m_urtext_name].get_chapter(index)
            ur_spacy_chapter = self.m_spacymodel("\n".join(ur_chapter))

            # II. Save the number of sentences for this chapter
            ur_sentence_counter = AOLMTextUtilities.get_sentence_dict_from_spacy_doc(ur_spacy_chapter)
            ur_sentence_counts[str(index)] = sum(ur_sentence_counter.values())

            # III. Create a dictionary of unique word counts of the ur chapter
            ur_word_counter = Counter(AOLMTextUtilities.get_words_from_string(AOLMTextUtilities.create_string_from_lines(ur_chapter)))
            ur_word_counts[str(index)] = sum(ur_word_counter.values())

        # C. Determine proportional chapter weights for sentences and words
        ur_total_sentence_count = sum(ur_sentence_counts.values())
        ur_total_word_count = sum(ur_word_counts.values())
        ur_sentence_weights = {}
        ur_word_weights = {}
        for index in range(1, ur_chapter_count + 1):

            ch_number = str(index)
            ur_sentence_weights[ch_number] = ur_sentence_counts[ch_number] / ur_total_sentence_count
            ur_word_weights[ch_number] = ur_word_counts[ch_number] / ur_total_word_count        

        # 2. Calculate evaluations of subsubmetrics (weighted per-edition scores)
        self.m_evaluations["subsubmetric"] = {
             
            reader_name: {
                "chapter_count": self.m_results[reader_name]["chapter_count"],

                # Weighted means
                "sentence_count": sum([ur_sentence_weights[str(index)] * self.m_results[reader_name]["sentence_count"]["by_chapter"].get(str(index), 0.0) \
                                        for index in range(1, ur_chapter_count + 1)]),
                # "sentence_count": mean(self.m_results[reader_name]["sentence_count"]["by_chapter"].values()),

                "word_count": sum([ur_word_weights[str(index)] * self.m_results[reader_name]["word_count"]["by_chapter"].get(str(index), 0.0) \
                                        for index in range(1, ur_chapter_count + 1)])
                # "word_count": mean(self.m_results[reader_name]["word_count"]["by_chapter"].values())
            }
            for reader_name in self.m_results 
        }

        # 3. Calculate evaluation of submetrics (average across editions)
        self.m_evaluations["submetric"] = {

            "chapter_count": mean([self.m_evaluations["subsubmetric"][reader_name]["chapter_count"] for reader_name in self.m_evaluations["subsubmetric"] if self.m_urtext_name != reader_name]),
            "sentence_count": mean([self.m_evaluations["subsubmetric"][reader_name]["sentence_count"] for reader_name in self.m_evaluations["subsubmetric"] if self.m_urtext_name != reader_name]),
            "word_count": mean([self.m_evaluations["subsubmetric"][reader_name]["word_count"] for reader_name in self.m_evaluations["subsubmetric"] if self.m_urtext_name != reader_name]),
        }

        # 4. Coverage (proportion of ur chapters present)
        self.m_evaluations["submetric"]["coverage"] = {
            reader_name: sum(1 for index in range(1, ur_chapter_count + 1)
                if self.m_results[reader_name]["sentence_count"]["by_chapter"].get(str(index), 0.0) > 0.0
                ) / ur_chapter_count
            for reader_name in self.m_results
        }        

        # 4. Metric is weighted mean of submetrics
        self.m_evaluations["metric"] = mean([self.m_evaluations["submetric"][key] for key in ["chapter_count", "sentence_count", "word_count"]])

        return self.metric_evaluation
    
    def output_chapter_comp_to_file(self, p_first_chapter, p_first_chapter_name, p_second_chapter, p_second_chapter_name):

        import json 

        json_data = {
            p_first_chapter_name: p_first_chapter,
            p_second_chapter_name: p_second_chapter
        }
        output_filepath = "/Users/weirdbeard/Documents/school/aolm_full/experiments/outputs/ch16_mtpo_ia_comparison.json"
    
        with open(output_filepath, "w") as output_file:
            json.dump(json_data, output_file, indent=4, ensure_ascii=False)

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
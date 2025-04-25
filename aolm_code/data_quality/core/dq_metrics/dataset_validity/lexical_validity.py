# Author: Jonathan Armoza
# Created: March 21, 2025
# Purpose: Data quality metric child class for Dataset validity over a text's lexicon

# submetrics for lexical validity

# Imports

# Built-ins
import csv
import json
import os
import sys
from datetime import datetime
from statistics import mean

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Third party
import spacy
from nltk.corpus import wordnet
import nltk

# Custom
import aolm_data_reading
from aolm_textutilities import AOLMTextUtilities
from dq_metric import DataQualityMetric


# Globals

# Constants
COHA = aolm_data_reading.COHA
PG = aolm_data_reading.PG
WORK_TITLE = "Adventures of Huckleberry Finn"

# NOTE: Use of this file entails loading spaCy and WordNet models
# NOTE: You must first run "python -m spacy download en_core_web_lg"

# Load spaCy's large English model
spacy_nlp = spacy.load("en_core_web_lg")

# Download WordNet if not already downloaded
nltk.download("wordnet")


# Objects

class DatasetValidity_LexicalValidity(DataQualityMetric):

    def __init__(self, p_name, p_input, p_source_id, p_work_title, p_collection_title, p_text_json_filepath, p_lexicon):

        super().__init__(p_name, p_input,
                         p_source_id=p_source_id,
                         p_work_title=p_work_title,
                         p_collection_title=p_collection_title,
                         p_path=p_text_json_filepath)
        
        # Lexicon used to test validity is read externally
        self.m_lexicon = p_lexicon

    def __build_eval_output_line__(self):

        key_value_map = { key: None for key in DataQualityMetric.s_build_output_line_keys }
        
        # 1. Lexical validity-specific evaluation keys
        key_value_map.update(self.m_evaluations)

        # 2. Base data quality metric evaluation keys
        key_value_map["source"] = self.m_source_id
        key_value_map["work_title"] = self.m_work_title
        key_value_map["edition_title"] = [os.path.splitext(file)[0] for file in os.listdir(self.m_path) if file.endswith(".json")]
        key_value_map["collection_title"] = self.m_collection_title
        key_value_map["metric"] = DatasetValidity_LexicalValidity.s_metric_name
        key_value_map["value"] = self.m_evaluations["metric"]
        key_value_map["compared_against"] = self.baseline_source_id
        key_value_map["filepath"] = self.m_path

        return key_value_map

    def __build_output_line__(self):

        key_value_map = {
            
            "source": self.m_source_id,
            "work_title": self.m_work_title,
            "edition_title": os.path.basename(os.path.splitext(self.m_path)[0]) if len(os.path.basename(self.m_path)) else self.m_source_id,
            "metric": DatasetValidity_LexicalValidity.s_metric_name,
            "value": self.m_evaluations["metric"], # This is wrong
            "compared_against": self.baseline_source_id,
            "filename": os.path.basename(self.m_path),
            "filepath": self.m_path
        }

        line_dict = { key: key_value_map.get(key, None) for key in DataQualityMetric.s_build_output_line_keys }
        line_str_array = [line_dict[key] for key in DataQualityMetric.s_build_output_line_keys]

        return ",".join(map(str, line_str_array)) + "\n"        
    
    # Properties

    @property
    def eval_output(self):
        return self.__build_eval_output_line__()
    @property
    def output(self):
        return self.__build_output_line__()

    def compute(self, p_use_reader_body=False):
        
        # Experiment 3 - Lexical Validity
        # DQ Metric Dataset Validity - Lexicon

        # 0. Setup
        self.m_results = {
            
            reader_name: {

                "edition_chapter_validity": {},
                "edition_work_validity": 0
            } for reader_name in self.m_input
        }

        # NOTE: Check out why one of the DNI editions is not getting lexical validity score for its chapters

        # 1. Calculate chapter lexical validities for each edition
        for reader_name in self.m_input:

            reader = self.m_input[reader_name]

            # A. Chapter lexical validities
            for index in range(1, reader.chapter_count + 1):

                # If chapter is in reader
                if reader.has_chapter(index):

                    # A. Get chapter as string
                    chapter_text = AOLMTextUtilities.create_string_from_lines(reader.get_chapter(index))

                    # B. Calculate the lexical validity of this chapter
                    self.m_results[reader_name]["edition_chapter_validity"][str(index)] = \
                        DatasetValidity_LexicalValidity.lexical_validity(chapter_text, self.m_lexicon)

            # B. Get total lexical validity of work
            if p_use_reader_body:
                full_text = reader.body
            else:
                full_text = [AOLMTextUtilities.create_string_from_lines(chapter_lines) for chapter_lines in reader.aolm_text.body.values()]
            full_text = "\n".join(full_text)
            self.m_results[reader_name]["edition_work_validity"] = \
                DatasetValidity_LexicalValidity.lexical_validity(full_text, self.m_lexicon)

    def evaluate(self):

        # Average lexical validity by chapter will be calculated in evaluate()

        # 1. Calculate evaluations of subsubmetrics
        self.m_evaluations["subsubmetric"] = { 

            reader_name: {

                "edition_chapter_validity_bychapter": [self.m_results[reader_name]["edition_chapter_validity"][index] for index in self.m_results[reader_name]["edition_chapter_validity"]],
                "edition_chapter_validity": mean([self.m_results[reader_name]["edition_chapter_validity"][index] for index in self.m_results[reader_name]["edition_chapter_validity"]]),
                "edition_work_validity": self.m_results[reader_name]["edition_work_validity"]
            }
            for reader_name in self.m_results 
        }

        # 2. Calculate evaluation of submetrics
        self.m_evaluations["submetric"] = {

            "collection_chapter_validity": mean([self.m_evaluations["subsubmetric"][reader_name]["edition_chapter_validity"] for reader_name in self.m_evaluations["subsubmetric"]]),
            "collection_work_validity": mean([self.m_evaluations["subsubmetric"][reader_name]["edition_work_validity"] for reader_name in self.m_evaluations["subsubmetric"]])
        }

        # 3. Metric is weighted mean of submetrics
        # NOTE: Should this be a weighted mean for chapter/work validity?
        self.m_evaluations["metric"] = mean(self.m_evaluations["submetric"].values())

        return self.metric_evaluation
    
    def output_results(self, p_output_filepath):

        # Output evaluation details

        print(f"Outputting results to: {p_output_filepath}")

        with open(p_output_filepath, "w") as eval_output_file:
            json.dump(self.eval_output, eval_output_file, indent=4)            


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
        "submetric__collection_chapter_validity",
        "submetric__collection_work_validity",
    ]     

    s_metric_name = "lexical_validity"

    @staticmethod
    def lexical_validity(p_original_text, p_lexicon, p_check_wordnet=True):

        # 1. Tokenize and process the text with spaCy
        global spacy_nlp
        doc = spacy_nlp(p_original_text)

        # 2. Filter out out-of-vocabulary words

        # A. Filter out words flagged as out-of-vocabulary by spaCy
        oov_words = { token.text for token in doc if token.is_alpha and token.is_oov }

        # B. Validate spaCy's out-of-vocabulary words against WordNet if requested
        if p_check_wordnet:
            oov_words = { word for word in oov_words if not wordnet.synsets(word) }

        # C. Validate against custom lexicon
        oov_words = { word for word in oov_words if word.lower() not in p_lexicon }

        # 3. Calculate lexical validity given percent of in-vocabulary words in original text

        # A. Calculate percent of out-of-vocabulary words
        unique_words = { token.text for token in doc if token.is_alpha }
        percent_oov = len(oov_words) / len(unique_words)

        # B. Lexical validity is percent of unique words that are in-vocabulary
        lexical_validity = 100 * (1.0 - percent_oov)

        return lexical_validity        


# Utility functions

def read_coha(p_coha_filepath):

     # Increase the CSV field size limit to accommodate COHA
    csv.field_size_limit(sys.maxsize)

    # coha_lexicon_columns = ["wID", "wordCS", "word", "lemma", "PoS"]
    lexicon_set = set()

    with open(p_coha_filepath, "r", encoding="ISO-8859-1") as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter="\t")
        rows = [row for row in reader if COHA.WORD_ID.value in row and row[COHA.WORD_ID.value].isnumeric()]
        for row in rows:
            if row[COHA.WORD.value]:
                lexicon_set.add(row[COHA.WORD.value].lower())
            if row[COHA.LEMMA.value]:
                lexicon_set.add(row[COHA.LEMMA.value].lower())

    return lexicon_set


# Main script

def main():

    # 0. Test setup

    # A. Load Corpus of Historical American English lexicon
    lexicon_filepath = "/Users/weirdbeard/Documents/school/aolm_full/data/lexicon/coha/lexicon.txt"
    coha_lexicon = read_coha(lexicon_filepath)
    
    # B. Read the editions to be examined
    pg_huckfinn_texts = aolm_data_reading.read_huckfinn_text(PG)

    # 1. Compute the data quality metrics and evaluate them
    validity_metric = DatasetValidity_LexicalValidity(
        f"HuckFinn_{PG}_LexicalValidity",
        pg_huckfinn_texts,
        PG,
        WORK_TITLE,
        aolm_data_reading.huckfinn_source_fullnames[PG],
        aolm_data_reading.huckfinn_directories[PG]["txt"],
        coha_lexicon
    )
    validity_metric.compute()
    lexical_validity_value = validity_metric.evaluate()

    # 2. Output results
    
    print(f"Overall lexical Validity of PG Huck Finn editions: {lexical_validity_value}")
    print(f"{"=" * 80}")
    print(validity_metric.output)
    print(f"{"=" * 80}")
    print(validity_metric.eval_output)

    output_directory = "/Users/weirdbeard/Documents/school/aolm_full/experiments/outputs/"
    script_run_time = datetime.now().strftime("%d%m%Y_%H%M%S")
    output_filepath = f"{output_directory}{DatasetValidity_LexicalValidity.s_metric_name}_eval_out_{script_run_time}.json"
    validity_metric.output_results(output_filepath)


if "__main__" == __name__:

    main()
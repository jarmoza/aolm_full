# Author: Jonathan Armoza
# Created: March 21, 2025
# Purpose: Data quality metric child class for Dataset validity over a text's lexicon

# submetrics for lexical validity

# Imports

# Built-ins
import csv
import os
import sys
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

# NOTE: Use of this file entails loading spaCy and WordNet models
# NOTE: You must run "python -m spacy download en_core_web_lg"

# Load spaCy's large English model
spacy_nlp = spacy.load("en_core_web_lg")

# Download WordNet if not already downloaded
nltk.download("wordnet")


class DatasetValidity_LexicalValidity(DataQualityMetric):

    def __init__(self, p_name, p_input, p_source_id, p_work_title, p_text_json_filepath, p_lexicon):

        super().__init__(p_name, p_input,
                         p_source_id=p_source_id,
                         p_work_title=p_work_title,
                         p_path=p_text_json_filepath)
        
        # Lexicon used to test validity is read externally
        self.m_lexicon = p_lexicon
    
    def compute(self):
        
        # Experiment 3 - Lexical Validity
        # DQ Metric Dataset Validity - Lexicon

        # 0. Setup
        self.m_results = {
            
            reader_name: {

                "chapter_validity": {},
                "work_validity": 0
            } for reader_name in self.m_input
        }

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
                    self.m_results[reader_name]["chapter_validity"][str(index)] = \
                        DatasetValidity_LexicalValidity.lexical_validity(chapter_text, self.m_lexicon)

            # B. Get total lexical validity of work
            # NEXT: Figure out how to get all lines from text here
            full_text = [AOLMTextUtilities.create_string_from_lines(chapter_lines) for chapter_lines in reader.aolm_text.body.values()]
            full_text = "\n".join(full_text)
            self.m_results[reader_name]["work_validity"] = \
                DatasetValidity_LexicalValidity.lexical_validity(full_text, self.m_lexicon)

    def evaluate(self):   

        # Average lexical validity by chapter will be calculated in evaluate()

        # 1. Calculate evaluations of subsubmetrics
        self.m_evaluations["subsubmetric"] = { 

            reader_name: {

                "chapter_validity": mean([self.m_results[reader_name]["chapter_validity"][index] for index in self.m_results[reader_name]["chapter_validity"]]),
                "work_validity": self.m_results[reader_name]["work_validity"]
            }
            for reader_name in self.m_results 
        }

        # 2. Calculate evaluation of submetrics
        self.m_evaluations["submetric"] = {

            "chapter_validity": mean([self.m_evaluations["subsubmetric"][reader_name]["chapter_validity"] for reader_name in self.m_evaluations["subsubmetric"]]),
            "work_validity": mean([self.m_evaluations["subsubmetric"][reader_name]["work_validity"] for reader_name in self.m_evaluations["subsubmetric"]])
        }

        # 3. Metric is weighted mean of submetrics
        # NOTE: Should this be a weighted mean for chapter/work validity?
        self.m_evaluations["metric"] = mean(self.m_evaluations["submetric"].values())

        return self.metric_evaluation

    # Static fields and methods

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
        lexical_validity = 1.0 - percent_oov

        return lexical_validity        


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


def main():

    # 0. Test setup

    # A. Load Corpus of Historical American English lexicon
    lexicon_filepath = "/Users/weirdbeard/Documents/school/aolm_full/data/lexicon/coha/lexicon.txt"
    coha_lexicon = read_coha(lexicon_filepath)
    
    # B. Read the editions to be examined
    PG = aolm_data_reading.PG
    text_filepath = aolm_data_reading.huckfinn_directories[PG]["txt"]
    # pg_huckfinn_texts = aolm_data_reading.read_huckfinn_text(PG, [aolm_data_reading.huckfinn_edition_names[PG][0]])
    pg_huckfinn_texts = aolm_data_reading.read_huckfinn_text(PG)

    # C. Compute the data quality metrics and evaluate them
    WORK_TITLE = "Adventures of Huckleberry Finn"
    validity_metric = DatasetValidity_LexicalValidity(
        f"HuckFinn_{PG}_LexicalValidity",
        pg_huckfinn_texts,
        PG,
        WORK_TITLE,
        text_filepath,
        coha_lexicon
    )
    validity_metric.compute()
    lexical_validity_value = validity_metric.evaluate()

    print(f"Lexical Validity of PG Huck Finn editions: {lexical_validity_value}")

if "__main__" == __name__:

    main()
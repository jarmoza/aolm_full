# Author: Jonathan Armoza
# Created: September 17, 2024
# Purpose: Contains methods to manipulate strings

# Imports

# Built-ins
from collections import Counter
from functools import reduce 
from math import ceil
import os
import re
from statistics import mean
import string
import unicodedata # Removing diacritics from characters

# Third party
import nltk
from Levenshtein import distance
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# Globals
# global debug_separator
# debug_separator = "=" * 80

# Classes

class AOLMTextUtilities:

    def __init__(self, p_aolm_text=None):

        self.m_text = p_aolm_text

    @staticmethod
    def clean_string(p_original_string, p_remove_internal_punctuation=False):

        # 1. Strip whitespace, lowercase, and replace \n and \t with ' '
        new_str = p_original_string.strip().lower().replace("\n", " ").replace("\t", " ")

        # 2. Remove all accents
        new_str = AOLMTextUtilities.remove_diacritics(new_str)

        # 3. Split by spaces and remove single 'n' characters
        new_str_parts = [part for part in new_str.split() if part != "n"]

        # 4. Remove punctuation from each word
        if p_remove_internal_punctuation:
            new_str_parts = ["".join(char for char in part if char.isalnum() or char.isspace()) for part in new_str_parts]
        else:
            new_str_parts = [AOLMTextUtilities.remove_punctuation(part, p_remove_internal_punctuation).strip() for part in new_str_parts]

        # 5. Replace multiple spaces with a single space
        new_str = " ".join(new_str_parts)

        return new_str

    @staticmethod
    def count_words_and_plot(p_text_filepath, p_top_words=10):

        nltk.download("punkt")

        # 1. Read in text file
        text_data = {}
        with open(p_text_filepath, "r") as input_file:
            text_data[os.path.basename(p_text_filepath)] = input_file.readlines()

        # 2. Clean and tokenize each text in the json file
        token_dict = {}
        for text in text_data:
            token_dict[text] = nltk.word_tokenize("\n".join(text_data[text]))

        # 3. Plot the counts of each given text
        number_cols = 2
        number_rows = ceil(len(text_data) / number_cols)
        i = 1
        j = 1

        print(f"number_cols: {number_cols}")
        print(f"number_rows: {number_rows}")

        # A. Create the plotly figure
        fig = make_subplots(rows=number_rows, cols=number_cols)

        # B. Create a plot for each text's word frequencies
        for text in text_data:

            # I. Create an ordered dictionary of the word frequencies
            # word_frequencies = OrderedDict(Counter(token_dict[text]))
            word_frequencies = Counter(token_dict[text])
            sorted_wordfreq_tuples = sorted(word_frequencies.items(), key=lambda item: item[1], reverse=True)

            # II. Create a new bar plot based on the text's word frequencies
            fig.add_trace(
                go.Bar(x=[word_tuple[0] for word_tuple in sorted_wordfreq_tuples[0:p_top_words]],
                    y=[word_tuple[1] for word_tuple in sorted_wordfreq_tuples[0:p_top_words]]),
                row=i, col=j
            )

            # III. Increment rows and columns indices
            j += 1
            if j > 2:
                i += 1
                j = 1
    
        # C. Show the plot
        fig.show()

    # NOTE: Expected arguments are dict of form {key: count}
    @staticmethod
    def dictionaries_percent_equal(p_source_dict, p_compared_dict):

        # 0. Percent will be based on the number of keys in the source dictionary
        num_source_keys = len(p_source_dict.keys())

        # How it works
        # We start with 'total_percent' at 100.0% and deduct down
        # Each key of the source dict is considering to be X% where X is 100 / num_source_keys [percent_per_source_key]
        # (A) If a source key is not in the compared dict then X is deducted from total_percent
        # (B) If source key is in compared dict then calculate percent of compared tally in source tally;
        # deduct anything less than 100% from total_percent
        # NOTE: Obviously there is the scenario where compared tally is greater than source tally, but we do not want to add to total percent
        # as this could misconstrue the meaning of the final value of total_percent

        total_percent = 100.0
        percent_per_source_key = 100.0 / num_source_keys

        for source_key in p_source_dict:

            # (A) If a source key is not in the compared dict then X is deducted from total_percent
            if source_key not in p_compared_dict:
                total_percent -= percent_per_source_key
            # (B) If source key is in compared dict then calculate percent of compared tally in source tally;
            # deduct anything less than 100% from total_percent
            else:
                compared_tally_percent = 100.0 * p_compared_dict[source_key] / p_source_dict[source_key]
                if compared_tally_percent < 100.0:
                    total_percent -= (100.0 - compared_tally_percent) * (percent_per_source_key / 100.0)

        return total_percent

    @staticmethod
    def create_string_from_lines(p_text_lines):

        final_text_lines = [line.strip() for line in p_text_lines if len(line.strip()) > 0]

        return " ".join(final_text_lines)

    @staticmethod    
    def find_matches(p_text, p_re_substring):
        
        # Define the regex pattern
        pattern = re.compile(p_re_substring)

        # Find all matches in the text
        matches = pattern.findall(p_text)

        return matches    

    @staticmethod
    def get_keyset(p_dictionary_list, p_secondlevel_keys=[]):

        # Gather keys (and keys of second level keys if given)
        all_keys = []
        for dictionary in p_dictionary_list:
            all_keys.extend(list(dictionary.keys()))
            if len(p_secondlevel_keys):
                for key in p_secondlevel_keys:
                    if key in dictionary:
                        all_keys.extend(list(dictionary[key].keys()))

        # all_keys = reduce(lambda a, b: a+b, [list(dictionary.keys()) for dictionary in p_dictionary_list])

        return list(set(all_keys))

    @staticmethod
    def get_sentence_dict_from_spacy_doc(p_spacy_doc):

        unique_sentences = {}
        if p_spacy_doc:
            for sent in p_spacy_doc.sents:
                cleaned_sent = AOLMTextUtilities.clean_string(sent.text, p_remove_internal_punctuation=True)
                if cleaned_sent not in unique_sentences:
                    unique_sentences[cleaned_sent] = 0
                unique_sentences[cleaned_sent] += 1
        return unique_sentences

    @staticmethod
    def get_words_from_string(p_string):
        return p_string.strip().split()
    
    @staticmethod
    def get_valueset(p_dictionary_list):

        def NestedDictValues(d):
            for v in d.values():
                if isinstance(v, dict):
                    yield from NestedDictValues(v)
                else:
                    yield v

        # Gather values (and values of second level values if given)
        all_values = []

        for dictionary in p_dictionary_list:

            flattened_values = NestedDictValues(dictionary)
            for value in flattened_values:
                if type(value) is list:
                    for list_member in value:
                        all_values.append(list_member)
                else:
                    all_values.append(value)

            # for value in dictionary.values():
            #     if type(value) is str:
            #         all_values.append(value)
            #     elif type(value) is dict:
            #         all_values.extend(value.values())

        return all_values

    @staticmethod
    def levenshtein_listcompare(p_stringset, p_acceptable_distance_denom=2.0):

        stringmatch_dict = {}

        for key in p_stringset:
            stringmatch_dict[key] = []
            for key2 in p_stringset:

                # Get the Levenshtein distance between keys
                comp_distance = distance(key, key2)

                # Determine the minimum acceptable distance based on 'key' length
                min_key_distance = len(key) / p_acceptable_distance_denom

                if comp_distance > 0 and comp_distance <= min_key_distance:
                    stringmatch_dict[key].append(key2)

        return stringmatch_dict

    # Source: https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    @staticmethod
    def remove_diacritics(p_original_string):

        new_str = []
        for char in p_original_string:
            # Gets the base character of char, by "removing" any
            # diacritics like accents or curls and strokes and the like.

            try:
                desc = unicodedata.name(char)
                cutoff = desc.find(" WITH ")
                if cutoff != -1:
                    desc = desc[:cutoff]
                    try:
                        char = unicodedata.lookup(desc)
                    except KeyError:
                        continue  # removing "WITH ..." produced an invalid name
                new_str.append(char)
            except:
                continue

        return "".join(new_str)

    @staticmethod
    def remove_punctuation(p_original_string, p_remove_internal_punctuation=False):

        # 1. Remove punctuation from the given string

        # A. Remove all punctuation, external and internal
        if p_remove_internal_punctuation:

            new_str_parts = []

            for char in p_original_string:
                if char in string.punctuation:
                    continue
                new_str_parts.append(char)
            return "".join(new_str_parts)
        # B. Remove external punctuation only
        else:

            # A. Find first alphanumeric character
            first_index = -1
            for index in range(len(p_original_string)):
                if p_original_string[index].isalnum():
                    first_index = index
                    break

            # B. Find last alphanumeric character
            last_index = -1
            for index in reversed(range(len(p_original_string))):
                if p_original_string[index].isalnum():
                    last_index = index
                    break

            return p_original_string[first_index:last_index + 1]
            # return p_original_string[first_index:last_index]

        return p_original_string

    @staticmethod
    def roman_numeral_from_decimal(p_decimal_number):

        # Conversion code from https://www.geeksforgeeks.org/python-program-to-convert-integer-to-roman/
        # on 10/30/2024

        number = p_decimal_number
        num = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000]
        sym = ["I", "IV", "V", "IX", "X", "XL", "L", "XC", "C", "CD", "D", "CM", "M"]
        i = 12
        finished_numeral = []
     
        while number:
            div = number // num[i]
            number %= num[i]
 
            while div:
                finished_numeral.append(sym[i])
                div -= 1
            i -= 1        

        return "".join(finished_numeral)

    # from /aolm_code/data_quality/dickinson/core
    @staticmethod
    def percent_line_match(p_original_line, p_compared_line, p_prepared_line=False):

        line_words = None
        compared_line_words = None

        # 0. Make sure we are comparing lists of words
        # NOTE: If this is a prepared line it is an array sized 2,
        # array[0] is the line, array[1] is the array of the line's words
        if p_prepared_line:
            line_words = p_original_line[1]
            compared_line_words = p_compared_line[1]
        else:
            line_words = p_original_line.strip().split(" ")
            compared_line_words = p_compared_line.strip().split(" ")

        # Save word counts of each line
        line_word_count = len(line_words)
        compared_line_word_count = len(compared_line_words)

        # NEW LINE MATCH ALGORITHM

        # Tally instances of unique words in each line
        line_words_counter = Counter(line_words)
        compared_line_words_counter = Counter(compared_line_words)

        # Tallies in the compared line determine the percent of line match
        return compared_line_words_counter.total() / float(line_word_count)

        # OLD LINE MATCH ALGORITHM

        # # 1. Try to find an initial word match
        # match_index = -1
        # for index in range(line_word_count):
        #     if index < compared_line_word_count and line_words[index] == compared_line_words[index]:
        #         match_index = index
        #         break

        # # If no beginning to matching sequence found, return 0% similarity
        # if -1 == match_index:
        #     return 0

        # # 2. Count all word matches that follow the initial word match
        # matches = 0
        # for index in range(match_index, line_word_count):
        #     if index < compared_line_word_count and line_words[index] == compared_line_words[index]:
        #         matches += 1

        # # Return percentage match (re: the above match rules) of compared line with original line
        # return float(matches) / float(line_word_count)

    @staticmethod
    def weighted_mean_from_dict(p_dict):

        return mean([p_dict[key] * 1.0 / len(p_dict.keys()) for key in p_dict])
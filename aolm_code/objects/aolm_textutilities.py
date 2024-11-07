# Author: Jonathan Armoza
# Created: September 17, 2024
# Purpose: Contains methods to manipulate strings

# Imports

# Built-ins
from collections import Counter
from math import ceil
import os
import re
import string

# Third party
import nltk
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# Globals

# Classes

class AOLMTextUtilities:

    def __init__(self, p_aolm_text=None):

        self.m_text = p_aolm_text

    @staticmethod
    def clean_line(p_line):

        # Lowercase
        clean_line = p_line.lower()

        # Clean remaining tags
        clean_line = re.sub(r"<[^>]*>", " ", clean_line)

        # Clean any other non-alphanumeric character
        clean_line = "".join([char for char in clean_line if char not in string.punctuation])

        # Clean multi-spaces
        clean_line = " ".join([word for word in clean_line.split() if "" != word])

        return clean_line

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

    @staticmethod
    def create_string_from_lines(p_text_lines):

        final_text_lines = [line.strip() for line in p_text_lines if len(line.strip()) > 0]

        return " ".join(final_text_lines)

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

        # 1. Try to find an initial word match
        match_index = -1
        for index in range(line_word_count):
            if index < compared_line_word_count and line_words[index] == compared_line_words[index]:
                match_index = index
                break

        # If no beginning to matching sequence found, return 0% similarity
        if -1 == match_index:
            return 0

        # 2. Count all word matches that follow the initial word match
        matches = 0
        for index in range(match_index, line_word_count):
            if index < compared_line_word_count and line_words[index] == compared_line_words[index]:
                matches += 1

        # Return percentage match (re: the above match rules) of compared line with original line
        return float(matches) / float(line_word_count)
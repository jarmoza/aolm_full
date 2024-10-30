# Author: Jonathan Armoza
# Created: September 17, 2024
# Purpose: Contains methods to manipulate strings

# Imports

# Built-ins
from collections import Counter
from math import ceil
import os

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
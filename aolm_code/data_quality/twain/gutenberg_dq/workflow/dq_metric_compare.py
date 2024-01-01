# Module for comparison of data quality metrics between texts


# Imports 

# Standard libraries
from asyncio.constants import DEBUG_STACK_DEPTH
from distutils.log import debug
import json
import os

# Third party libraries
import enchant
spellchecker = enchant.Dict("en_US")

# Local libraries
from data_quality.core.stylometry_methods import BurrowsDelta, Text
from huckfinn_frequency_rates import WordFrequencyTracker
from utilities.aolm_utilities import debug_separator, format_path
from utilities import aolm_paths
aolm_paths.setup_paths()

class CuratedText:

    def __init__(self, p_id, p_data):

        self.m_id = p_id
        self.m_data = p_data

# This class should contain prototypes for basic comparisons between
# a. Two texts
# b. One text and many texts
class TextMetricComparer:

    # Constructor and private methods

    def __init__(self, p_sourcetext_name, p_texts={}):

        # 1. Save a reference to the texts to be used for comparison
        self.m_texts = p_texts

        # 2. Save info on the ground truth or 'source' text
        self.m_sourcetext_name = p_sourcetext_name

        self.m_sourcetext = self.m_texts[self.m_sourcetext_name]

    # Properties

    @property
    def source_text(self):
        return self.m_texts[self.m_sourcetext_name]
    @property
    def source_textname(self):
        return self.m_sourcetext_name
    @property
    def texts(self):
        return self.m_texts

    # Static methods

    @staticmethod
    def output_stats(p_description, p_list, p_filepath):

        with open(p_filepath, "w") as output_file:
            for line in p_list:
                output_file.write(line)

        

    @staticmethod
    def print_stats(p_description, p_list):

        print(debug_separator)
        print(p_description)
        for item in p_list:
            print(p_list)    


# Modules for comparing digital editions of 'The Adventures of Huckleberry'
# taken from 'Project Gutenberg' and 'The Internet Archive' that have been 
# curated and ingested into custom json format containing header, front matter,
# body and its chapters, and footer. This custom json format also includes metrics
# taken and stored about each volume's body contents
class HuckFinnVolumeComparer(TextMetricComparer):

    # Constructor

    def __init__(self, p_sourcetext_name, p_textjson_filepaths):

        # 1. Read in the json data and metadata for each volume
        #    and save a reference to them
        super().__init__(p_sourcetext_name, self.__read_json(p_textjson_filepaths))

    # Private methods

    def __read_json(self, p_textjson_filepaths):

        volumes_json = {}
        for filepath in p_textjson_filepaths:
            filename_noext = os.path.splitext(os.path.basename(filepath))[0]
            with open(filepath, "r") as json_file:
                volumes_json[filename_noext] = json.load(json_file)
        return volumes_json

    # Public methods

    # Word frequency methods for individual texts
    def text_total_words(self, p_text_id):

        return sum(self.m_texts[p_text_id]["total_word_frequencies"].values())

    # Number of identifiable English words according to PyEnchant
    def text_total_english_words(self, p_text_id):
        
        word_list = self.m_texts[p_text_id]["total_word_frequencies"].keys()
        word_count = len(word_list)
        non_english_words = 0

        for word in word_list:
            if not spellchecker.check(word):
                non_english_words += 1

        print(debug_separator)
        print(p_text_id)
        print("Non-English words: {0}/{1}".format(non_english_words, word_count))
        print("Percentages: {0}% non-English words".format(100 * float(non_english_words) / word_count))


    # Word frequency comparison methods

    # total_word_frequencies

    def common_words(self):

        # 1. Get the set of words in the source text
        common_wordset = set(self.source_text["total_word_frequencies"].keys())

        # 2. Create a super-intersection among all the texts
        for textname in self.m_texts:
            if textname == self.source_textname:
                continue
            common_wordset = common_wordset.intersection(self.m_texts[textname]["total_word_frequencies"])

        return list(common_wordset)

    def different_words(self):

        last_chapter_name = "HUCKLEBERRYFINN_BODY_CHAPTER THE LAST"

        # 1. Get words of source text
        source_words = self.m_texts[self.source_textname]["cumulative_word_counts"][last_chapter_name].keys()

        # 2. Create lists for each compared text
        other_edition_words = {}
        for text_id in self.m_texts:
            if text_id != self.source_textname:
                other_edition_words[text_id] = self.m_texts[text_id]["cumulative_word_counts"][last_chapter_name].keys()

        # 3. Find words that are in each compared text but not in the source text
        # and add those words to their respective lists
        other_edition_new_words = {}
        for text_id in other_edition_words:
            other_edition_new_words[text_id] = list(set(other_edition_words[text_id]) - set(source_words))

        # 4. Find words source text has in common with each compared text
        other_edition_common_words = {}
        for text_id in other_edition_words:
            other_edition_common_words[text_id] = list(set(other_edition_words[text_id]).intersection(set(source_words)))

        # 5. Find the difference in counts of those common words between the source
        # text and compared text (compared's counts above or below source text, +/-)
        other_edition_common_word_counts = {}
        for text_id in other_edition_words:
            other_edition_common_word_counts[text_id] = {}
            for word in other_edition_common_words[text_id]:
                other_edition_common_word_counts[text_id][word] = \
                    self.m_texts[text_id]["cumulative_word_counts"][last_chapter_name][word] - \
                        self.m_texts[self.source_textname]["cumulative_word_counts"][last_chapter_name][word]

        # A. Clean words that have no difference between source and other editions
        for text_id in other_edition_common_word_counts:
            other_edition_common_word_counts[text_id] = { word: other_edition_common_word_counts[text_id][word] \
                for word in other_edition_common_word_counts[text_id] \
                    if other_edition_common_word_counts[text_id][word] > 0 }
            

        return [other_edition_new_words, other_edition_common_word_counts]

    def unique_words(self):
        return None

    def most_frequent_words(self, p_tf_idf=False):
        return None

    def hapax_legomena(self):
        return None

    def word_vector_distances(self, p_tf_idf=False):
        return None

    def burrows_deltas(self):
        return None

    # Other public methods

    def interesting_stats(self, p_output_folder):

        # 0. Quick key
        twf = "total_word_frequencies"
        output_list = []

        # 1. Output statistics

        # =====================================================================

        # A. Total words for each text compared to the ground truth text

        # I. Output setup
        output_list = []
        output_description = "Total word count for each text"

        # II. Get ground truth text word count
        source_word_count = self.text_total_words(self.source_textname)
        
        # III. Build output string comparing each text's word count and the ground truth text's word count
        for text in self.m_texts:

            # a. Word count of this text
            text_word_count = self.text_total_words(text)

            # b. Delta in word count between this text and ground truth text
            word_count_difference = text_word_count - source_word_count

            # c. Build and save output string
            plus_minus_str = "+" if (word_count_difference > 0) else ""
            output_list.append("{0}: {1} ({2}{3})".format(
                text,
                text_word_count,
                plus_minus_str,
                word_count_difference))

        # IV. Print out the statistics
        TextMetricComparer.print_stats(output_description, output_list)

        # B. Number of fake vs real words
        for text in self.m_texts:
            self.text_total_english_words(text)

        if True:
            return

        # =====================================================================

        # C. Most frequent words averaged across all
        
        # I. Output setup
        output_list = []
        output_description = "Most frequent words averaged"

        # II. Gather word frequencies for each for each text
        word_freqs = {}
        for text in self.m_texts:
            for word in self.m_texts[text][twf]:
                if word not in word_freqs:
                    word_freqs[word] = []
                word_freqs[word].append(self.m_texts[text][twf][word])

        # III. Average all the word frequencies for each word for each text
        word_freq_avgs = {}
        for word in word_freqs:
            word_freq_avgs[word] = sum(word_freqs[word]) / float(len(word_freqs[word]))

        # IV. Build csv lines
        
        # a. Word frequencies
        output_list = ["{0},{1}\n".format(word, word_freq_avgs[word]) for word in word_freq_avgs]

        # b. Header
        output_list.insert(0, "word,average\n")

        # V. Output the word frequency averages in a csv file
        TextMetricComparer.output_stats(output_description, output_list, p_output_folder + "most_freq_words_avg.csv")

def main():

    # 0. Paths
    input_folder = "{0}{1}comparisons{1}word_frequency{1}input{1}json{1}".format(
        aolm_paths.data_paths["twain"]["huckleberry_finn"], os.sep)
    output_folder = "{0}{1}comparisons{1}word_frequency{1}output{1}".format(
        aolm_paths.data_paths["twain"]["huckleberry_finn"], os.sep)
    stopwords_filepath = aolm_paths.data_paths["aolm_general"]["voyant_stopwords"]

    # 0. Ground truth text
    source_text_filename = "2021-02-21-HuckFinn_cleaned_processed"
    
    # 1. Read in all texts
    tracker = WordFrequencyTracker(input_folder, source_text_filename, stopwords_filepath, p_process=False)

    # 2. Create a comparer object
    json_filepaths = [input_folder + filename + ".json" for filename in tracker.texts]
    comparer = HuckFinnVolumeComparer(source_text_filename, json_filepaths)

    # 3. Isolate ground truth text
    source_text = comparer.source_text

    # 4. Show some interesting statistics about the texts
    comparer.interesting_stats(output_folder)

    # 5. Perform comparisons

    # # A. Common words
    # common_words = comparer.common_words()
    # print(common_words)

    # # B. Unique words
    # unique_words = comparer.unique_words()

    # # C. Most frequent words
    # most_frequent_words = comparer.most_frequent_words()

    # # D. Hapax Legomena
    # hapax_legomena = comparer.hapax_legomena()

    # # E. Word vector distance
    # word_vector_distances = comparer.word_vector_distances()

    # # F. TF-IDF most frequent words
    # tfidf_most_frequent_words = comparer.most_frequent_words(p_tf_idf=True)

    # # G. TF-IDF word vector distance
    # tfidf_word_vector_distances = comparer.word_vector_distances(p_tf_idf=True)

    # # H. Burrows Delta
    # burrows_deltas = comparer.burrows_deltas()

if "__main__" == __name__:
    main()


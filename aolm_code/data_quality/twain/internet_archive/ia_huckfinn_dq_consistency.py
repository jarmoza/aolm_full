# Author: Jonathan Armoza
# Created: September 5, 2024
# Purpose: Contains data quality metrics for consistency throughout Mark Twain's 'Adventures of Huckleberry Finn'

# Sketch
# Consistency for the book consists of taking chapter-level consistency measures and then determining a consistency score
# based on the overall consistency of the chapters in the book

# Consistency measure #1: Tally frequency of unique words per chapter
# Input several Internet Archive editions of Huckleberry Finn
# NOTE: Missing chapters receive a consistency score of 0
# NOTE: In order to produce good measurements, editions of Huckleberry Finn from Internet Archive will have their chapters
# consistently demarcated for exact word tallying and chapter comparison
# NOTE: Source edition will be the plain text version of Huckleberry Finn via Mark Twain Project Online
# Output: Consistency scores, one for each chapter, and then a consistency score based on all chapters

# Imports

# Custom
from dq_metrics import DataQualityMetric


# Classes

class ChapterConsistency(DataQualityMetric):

    def __init__(self, p_source_text, p_text_collection):

        self.m_source_text = p_source_text
        self.m_source_freq_dist = p_source_text.freq_dist
        self.m_texts = p_text_collection
        self.m_freq_dists = None

        # Metrics
        self.m_chapter_scores = { text.id: [0] * len(text.chapters) for text in p_collection }

    # Private methods

    def __compare_chapter_freq_dists(self, p_chapter_a, p_chapter_b):

        # 1. Get total chapter word count for source text

        # 2. Get weights for each word (what percentage is the word's tally for the source text out of all words in its respective chapter

        # 3. Measure a score for each word in each chapter of the comparison text(s) where
        # score = word_weight * (tallyofword_in_comp_text / tallyofword_in_source_text)

        # 4. Calculate chapter scores by averaging (correctly weighted because of #3) word scores for this chapter

        # 5. Return chapter score

        pass

    # Public methods

    def measure(self):

        # Tally word frequencies for each chapter in each text
        self.m_freq_dists = { text.id: [chapter.freq_dist for chapter in text.chapters] for text in p_text_collection }

        # Get chapter scores for each text

        # Calculate overall score for each text

        # Return chapter consistency score for each text in the given collection for comparison


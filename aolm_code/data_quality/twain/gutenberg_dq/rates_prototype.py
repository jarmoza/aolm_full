# Author: Jonathan Armoza
# Created: November 13, 2021
# Purpose: Demonstrate measurement and visualization of data quality metric measurements
# as a rate (e.g. a function of time) over the course of 'text-time' in a text
# The idea here is to demonstrate the simplest example of data quality for humanities

# Example #1: Word frequency distribution by chapter

# Steps
# 1: Ingest text by chapter
# 2: Calculate word frequencies for each chapter
# 3: Create cumulative word frequencies for each chapter
# 4: Visualize the change in word frequencies of the top N words by chapter
# 5: Measure the rate of change of each of those top N words by chapter
# 6: Visualize the rate of change of each of those top N words by chapter
# 7: Perform steps 1-6 on a text variant (different edition, different publisher, etc.)
# 8: Compare the change in word frequencies and the rate of change across text variants
# 9: Write about observations

# Requirements
# 1: A document class
# 2: A Text class that contains documents
# 3: Document functionality that tallies word frequencies
# 4: Text functionality that tallies cumulative word frequencies across documents
# 5: A Visualization class that takes word frequency counts and plots them by chapter
# 6: Text functionality that measures the rate of change for word frequencies across documents
# 7: Visualization functionality that plots the rate of change of word frequencies
# 8: A TextCollection class
# 9: TextCollection functionality that compares word frequencies, cumulative word frequencies,
#    and rates of change in word frequency

# Text(s) for example
# 1: Versions of Mark Twain's Huckleberry Finn on Project Gutenberg

# Idea
# Create a datalad for text versions used in The Art of Literary Modeling


# Steps
# 1: Ingest text by chapter
from huckfinn_gutenberg_dq import HuckleberryFinn
from huckfinn_gutenberg_dq import file_components as huckfinn_headers
from huckfinn_gutenberg_dq import paths

huckfinn = HuckleberryFinn(paths["input"] + paths["2021-02-21"], huckfinn_headers)

print(huckfinn.chapters)

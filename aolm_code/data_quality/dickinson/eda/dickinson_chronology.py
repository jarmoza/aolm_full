# Project Outline

# Author: Jonathan Armoza
# Title: Art of Literary Modeling, Chapter 2: Model Quality
# Creation Date: August 6, 2019
# Premise: Over the course of the 20th century, scholars produced rough manuscript orderings and 
# 		   creation chronologies for Emily Dickinson's poems, letters, packets, and fascicle books.
# 		   Several efforts were conducted to mixed success and acceptance of the chronologies and
# 		   their criteria.
#
# Proposal: Utilizing the style and other linguistic aspects of Dickinson's writings, manuscript
# 			metadata (paper type, watermarks,...) these chronologies for poems, letters, packets,
# 			and fascicle books of multiple scholars (Johnson, Franklin, Nell Smith, and others)
# 			can be proofed via machine learning models. To measure/understand how and if such a
# 			model successfully learns the Dickinson data collection, multiple models will be used.
#			Qualities utilized by statisticians, computer scientists, and machine learning practitioners
#			will be considered alongside qualities considered by (nineteenth-century American)
# 			literary scholars. The products and analysis from this study will form the basis for a general
# 			modeling quality framework for digital humanists.

import os

# import spacy
from dickinson_poem import DickinsonPoem


# Models

# SVM
# LSTM
# spaCy BERT
# spaCy XLNET
# NMF
# Chronological LDA

# Statistical Model Metrics

# Humanities Model Metrics

# Model Comparison Class

def main():

	dissertation_folder = os.getcwd() + os.sep + "../../../"
	tei_folder = dissertation_folder + "datasets/dickinson/poems/tei/"
	txt_folder = dissertation_folder + "datasets/dickinson/poems/txt/"

	# Check publication dates of all poems
	# DickinsonPoem.show_poems_by_publication_date(tei_folder)

	# Check manuscript IDs of all poems
	# DickinsonPoem.show_poems_by_collection_id(tei_folder)

	# Match collection IDs and publication statements
	# DickinsonPoem.show_poems_by_publication_info(tei_folder)

	# DickinsonPoem.show_collection_titles(tei_folder, "FD")

	DickinsonPoem.compare_collection_titles(tei_folder, "F", "J")

	# Create txt files of all 1998 Variorum poems
	# DickinsonPoem.gather_poems(tei_folder, txt_folder,
	# 						   p_publication_date="1998", p_collection_id="FA", p_similarity_comparison=False)

	# nlp = spacy.load('en_core_web_sm')
	# doc = nlp(u'Apple is looking at buying U.K. startup for $1 billion')

	# for token in doc:
	#     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
	#             token.shape_, token.is_alpha, token.is_stop)

if "__main__" == __name__:
	main()
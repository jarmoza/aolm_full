# Imports

# Built-ins

import glob
import os

# Third party
from nltk.stem import WordNetLemmatizer
import numpy as np
import editdistance # https://github.com/aflc/editdistance
from tqdm import tqdm # Visualizes percent done of processes on the terminal


# Local
from dickinson_poem import DickinsonPoem

# Paths for outputs of this script
paths = {

	# Path to Dickinson tei files
	"tei_path": os.getcwd() + "{0}..{0}tei{0}".format(os.sep),

	# Path to tag html output files
	"html_path": os.getcwd() + "{0}..{0}stats{0}html{0}".format(os.sep),

	# Root path to split corpus folders
	"split_corpus_path": os.getcwd() + "{0}..{0}curated{0}split{0}".format(os.sep),

	# Path to list of Levenshtein edit distances between poem titles
	"title_distance_path": os.getcwd() + "{0}..{0}stats{0}title_distances{0}".format(os.sep),

	# Path where output files from xml analysis are placed
	"output_path": os.getcwd() + "{0}output{0}".format(os.sep)
}

# 1. Ingest all poems as poem objects
poems = []
for tei_filepath in glob.glob(paths["tei_path"] + "*"):
	poems.append(DickinsonPoem(tei_filepath))

# 2. Create a lexicon of the words
lexicon = {}
for poem in poems:
	for word in poem.lexicon:
		if word not in lexicon:
			lexicon[word] = 0
		lexicon[word] += poem.bow[word]

# print(lexicon)

# 3. Output lexicon to csv file
# with open(paths["output_path"] + "dickinson_lexicon.csv", "w") as output_file:
# 	output_file.write("word,count\n")
# 	for word in lexicon:
# 		output_file.write("\"{0}\",{1}\n".format(word,lexicon[word]))

# 4. Compare words that are nearly identical (small edit distance)
def levenshtein(p_sequence1, p_sequence2):
    
    size_x = len(p_sequence1) + 1
    size_y = len(p_sequence2) + 1
    matrix = np.zeros((size_x, size_y))
    
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            
            if p_sequence1[x - 1] == p_sequence2[y - 1]:
                matrix [x,y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1],
                    matrix[x, y - 1] + 1)
            else:
                matrix [x,y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1] + 1,
                    matrix[x, y - 1] + 1)

    return (matrix[size_x - 1, size_y - 1])

# with open(paths["output_path"] + "levenshtein_map.csv", "w") as output_file:

# 	output_file.write("word,close_words\n")

# 	lexicon_words = list(lexicon.keys())

# 	# Clear out duplicates by lemma
# 	lemmatizer = WordNetLemmatizer() 
# 	lemmatized_words = []
# 	word_to_lem_dict = {}
# 	for word in lexicon_words:
# 		lemword = lemmatizer.lemmatize(word)
# 		word_to_lem_dict[word] = lemword
# 		if lemword not in lemmatized_words:
# 			lemmatized_words.append(lemword)

# 	for index in tqdm(range(1, len(lemmatized_words))):

# 		word = lemmatized_words[index]
# 		distribution_list = []

# 		# Looking for edit distances of < 1/5 word length, but at least 1
# 		onefifth_len = len(word) / 5.0
# 		if onefifth_len < 1.0:
# 			onefifth_len = 1

# 		# Store all words of edit distance < 1/5 length of the word
# 		for word2 in lexicon_words:
# 			if word2 != word:
# 				if word == word_to_lem_dict[word2] or \
# 					editdistance.eval(word, word2) < onefifth_len:
# 					distribution_list.append(word2)

# 		# Only output word if there is more than just itself in the edit distance list
# 		if len(distribution_list) > 1 and word != distribution_list[0]:
# 			output_file.write("{0},{1}\n".format(word, ",".join(distribution_list)))
		

# 5. Create a distributional accounting for each word based on the number of variants of that word
word_distribution_map = {}
with open(paths["output_path"] + "levenshtein_map.csv", "r") as input_file:
	lines = input_file.readlines()
	for index in range(1, len(lines)):
		line_parts = lines[index].strip().split(",")
		word_distribution_map[line_parts[0]] = len(line_parts[1:])

# 6. Determine a consistency rating for each word in the corpus
# Per word consistency is a function of average word-lemma-edit distribution

# Get average distribution
avg_distribution = float(sum(word_distribution_map.values())) / len(word_distribution_map.keys())
print("Average distribution value: {0}".format(avg_distribution))

# Determine consistency ratings for each word
word_consistency_ratings = {}
for word in word_distribution_map:
	word_consistency_ratings[word] = word_distribution_map[word] / avg_distribution

# Output word consistency ratings
with open(paths["output_path"] + "word_consistencies.csv", "w") as output_file:
	output_file.write("word,rating\n")
	for word in word_consistency_ratings:
		output_file.write("{0},{1}\n".format(word, word_consistency_ratings[word]))

# 7. Determine a summary word consistency rating for the entire corpus
avg_consistency_rating = float(sum(word_consistency_ratings.values())) / len(word_consistency_ratings.keys())
print("Corpus-word consistency rating: {0}".format(avg_consistency_rating))
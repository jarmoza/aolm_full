import nltk
import sys
from utilities.aolm_utilities import remove_stopwords

def main(p_string_to_clean):

	new_tokens = remove_stopwords(nltk.word_tokenize(p_string_to_clean))

	print("\n\n")
	print(" ".join(new_tokens))

if "__main__" == __name__:
	main(sys.argv[1])
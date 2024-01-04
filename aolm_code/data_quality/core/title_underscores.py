# Author: Jonathan Armoza
# Updated: January 4, 2023
# Purpose: Takes title string from the terminal and replaces all spaces with underscore characters

# Imports

# Built-ins
import string
import sys


# Main script

def main(p_title_words):

    # 1. Create a string of passed in title words separated by spaces
    first_pass = " ".join(p_title_words).lower().strip()    

    # 2. Punctuation is also translated as a space
    replace_punctuation = string.punctuation.maketrans(string.punctuation, ' ' * len(string.punctuation))
    second_pass = first_pass.translate(replace_punctuation)
    
    # 3. Replace all spaces with underscores
    third_pass = second_pass.replace(" ", "_")

    print(third_pass)

if "__main__" == __name__:
    main(sys.argv[1:])
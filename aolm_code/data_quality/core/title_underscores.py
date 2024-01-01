import string
import sys


first_pass = " ".join(sys.argv[1:]).lower().strip()

replace_punctuation = string.punctuation.maketrans(string.punctuation, ' ' * len(string.punctuation))
second_pass = first_pass.translate(replace_punctuation).replace(" ", "_")

print(second_pass)
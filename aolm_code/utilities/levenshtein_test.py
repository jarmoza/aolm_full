# Imports

# Built-in
from datetime import datetime

# Third party
import numpy as np
import editdistance # https://github.com/aflc/editdistance


# Functions

def levenshtein(p_sequence1, p_sequence2):
    
    size_x = len(p_sequence1) + 1
    size_y = len(p_sequence2) + 1
    matrix = np.zeros ((size_x, size_y))
    
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            
            if p_sequence1[x - 1] == p_sequence2[y-1]:
                matrix [x,y] = min(
                    matrix[x - 1, y] + 1,
                    matrix[x - 1, y - 1],
                    matrix[x, y - 1] + 1)
            else:
                matrix [x,y] = min(
                    matrix[x - 1,y] + 1,
                    matrix[x - 1,y - 1] + 1,
                    matrix[x,y - 1] + 1)

    return (matrix[size_x - 1, size_y - 1])

def time_and_run(function, *args):

    # Run begins here
    start_time = datetime.now()

    function(*args)

    # Run finishes here
    complete_time = datetime.now() - start_time
    print('\'{0}\' time to completion: {1:.10f}'.format(function.__name__, complete_time.total_seconds()))


# Sandbox

string_one = "bob"
string_two = "borob"

time_and_run(editdistance.eval, string_one, string_two)

time_and_run(levenshtein, string_one, string_two)
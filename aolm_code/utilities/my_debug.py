# Author: Jonathan Armoza
# Created: 
# Purpose: Debug printing functionality utilizing terminal size and colors

# Imports

# Built-ins
from os import get_terminal_size


# Globals

debug_character = "#"
debug_divider = debug_character * get_terminal_size().columns

# Terminal colors

class bcolors:

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Library functionality

def debug_print(p_string, p_text_color=bcolors.OKGREEN, p_divider_color=bcolors.OKBLUE):

    print(f"{p_divider_color}{debug_divider}{bcolors.ENDC}" + \
          f"{p_text_color}{p_string}{bcolors.ENDC}\n")

# Test script

def main():

    print("{0}I'm a header{1}".format(bcolors.HEADER, bcolors.ENDC))
    print("{0}I'm blue okay{1}".format(bcolors.OKBLUE, bcolors.ENDC))
    print("{0}I'm green okay{1}".format(bcolors.OKGREEN, bcolors.ENDC))
    print("{0}I'm a warning{1}".format(bcolors.WARNING, bcolors.ENDC))
    print("{0}I'm a failure{1}".format(bcolors.FAIL, bcolors.ENDC))
    print("{0}I'm bold{1}".format(bcolors.BOLD, bcolors.ENDC))
    print("{0}I'm underlined{1}".format(bcolors.UNDERLINE, bcolors.ENDC))
    
    debug_print("This is a test debug print")


if "__main__" == __name__:

    main()


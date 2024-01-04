# Author: Jonathan Armoza
# Created: ca. 2013-2024
# Purpose: Compilation of all Emily Dickinson poem-related code
# into useful classes and functions

# Imports

# Built-ins
import glob
import os
import re
import string
from itertools import chain

# Third party
from bs4 import BeautifulSoup
from tqdm import tqdm

# Custom

# Includes logging and loop progress debug functionality
from my_logging import logging

# Comment out to enable debug messages
# logging.disable(logging.DEBUG)

# Author: Jonathan Armoza
# Created: November 4, 2024
# Purpose: Read Project Gutenberg's versions of The Adventures of Huckleberry Finn

# Imports

# Built-ins
import json
import os

# Third party
from bs4 import BeautifulSoup, NavigableString

# Custom
from aolm_textutilities import AOLMTextUtilities
from aolm_textreader import AOLMTextReader, READER_FILETYPE_JSON


# Classes

class PGHuckFinnReader(AOLMTextReader):
    
    def __init__(self, p_filepath):

        super().__init__(p_filepath, READER_FILETYPE_JSON)

    def get_chapter(self, p_chapter_number):
        
        roman_numeral = AOLMTextUtilities.roman_numeral_from_decimal(p_chapter_number)
        body_id = f"{self.m_json["keys"]["output"]["body"]}CHAPTER {roman_numeral}."

        return self.m_json["components"]["body"][body_id]

    def read(self):

        with open(self.filepath, "r") as json_file:

            # A. Save raw file contents
            self.m_aolm_text.m_raw_file_contents = json_file.read()

            # B. Parse the TEI xml
            self.m_json = json.loads(self.m_aolm_text.m_raw_file_contents)

            # C. Separate metadata and body text tags
            self.m_aolm_text.m_metadata = self.m_json["components"]["header"]
            self.m_front = self.m_json["components"]["frontmatter"]
            self.m_aolm_text.m_body = self.m_json["components"]["body"]
            self.m_back = self.m_json["components"]["footer"]


# Test script

def main():

    test_filepath = f"{os.getcwd()}{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}project_gutenberg{os.sep}json{os.sep}"
    
    test_file = "2011-05-03-HuckFinn.json"
    reader = PGHuckFinnReader(test_filepath + test_file)
    reader.read()
    print(reader.get_chapter(1))

if "__main__" == __name__:
    
    main()

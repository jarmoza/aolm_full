# Author: Jonathan Armoza
# Created: October 24, 2024
# Purpose: Reads files from Mark Twain Project Online

# Imports

# Built-ins
import os

# Third party
from bs4 import BeautifulSoup, NavigableString

# Custom
from aolm_textreader import AOLMTextReader, READER_FILETYPE_TEI


# Classes

class MTPOReader(AOLMTextReader):

    def __init__(self, p_filepath):

        super().__init__(p_filepath, READER_FILETYPE_TEI)

        self.m_raw_file_contents = None
        self.m_tei_soup = None

    def read(self):

        with open(self.filepath, "r") as tei_file:

            # A. Save raw file contents
            self.m_raw_file_contents = tei_file.read()

            # B. Parse the TEI xml
            self.m_tei_soup = BeautifulSoup(self.m_raw_file_contents, "lxml")

    def print(self):

        paragraphs = self.m_tei_soup.find_all("p")

        for paragraph in paragraphs:
            for child in paragraph.children:
                if type(child) is NavigableString:
                    if len(child.strip()) > 0:
                        print(child.strip())

        # print(self.m_tei_soup.get_text())

def main():

    test_filepath = f"{os.getcwd()}{os.sep}..{os.sep}..{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}mtpo{os.sep}"
    # test_file = "MTDP10000.xml"
    test_file = "chapter_example.xml"
    reader = MTPOReader(test_filepath + test_file)
    reader.read()
    reader.print()


if "__main__" == __name__:
    main()

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

        self.m_tei_soup = None

    def read(self):

        with open(self.filepath, "r") as tei_file:

            # A. Save raw file contents
            self.m_aolm_text.m_raw_file_contents = tei_file.read()

            # B. Parse the TEI xml
            self.m_tei_soup = BeautifulSoup(self.m_aolm_text.m_raw_file_contents, "html.parser")

            # C. Separate metadata and body text tags
            self.m_aolm_text.m_metadata = self.m_tei_soup.find("teiHeader")
            self.m_front = self.m_tei_soup.find("text").front
            self.m_aolm_text.m_body = self.m_tei_soup.find("text").body
            self.m_back = self.m_tei_soup.find("text").back

    def print(self):

        paragraphs = self.m_tei_soup.find_all("p")

        for paragraph in paragraphs:
            for child in paragraph.children:
                if type(child) is NavigableString:
                    if len(child.strip()) > 0:
                        print(child.strip())

        # print(self.m_tei_soup.get_text())

def main():

    # Add the project root to sys.path
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    import sys
    sys.path.append(ROOT_DIR)
    from definitions import add_lib_paths
    add_lib_paths(sys)
    import aolm_data_reading

    test_filepath = aolm_data_reading.huckfinn_directories[aolm_data_reading.MTPO]["txt"]
    test_file = "MTDP10000_edited.xml"

    # test_filepath = f"{os.getcwd()}{os.sep}..{os.sep}..{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}mtpo{os.sep}"
    # test_file = "chapter_example.xml"

    # /Users/weirdbeard/Documents/school/aolm_full/data/twain/huckleberry_finn/mtpo/MTDP10000_edited.xml

    reader = MTPOReader(test_filepath + test_file)
    reader.read()

    reader.print()


if "__main__" == __name__:
    main()

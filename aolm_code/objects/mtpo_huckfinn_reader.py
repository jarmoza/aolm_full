# Author: Jonathan Armoza
# Created: October 30, 2024
# Purpose: Reads the Mark Twain Project Online's TEI version of The Adventures
#          of Huckleberry Finn

# Imports

# Built-ins
import os

# Third party
from bs4 import BeautifulSoup, NavigableString

# Custom
from aolm_textutilities import AOLMTextUtilities
from aolm_textreader import AOLMTextReader, READER_FILETYPE_TEI


# Classes

class MTPOHuckFinnReader(AOLMTextReader):

    # Constructor and private methods
    
    def __init__(self, p_filepath):

        super().__init__(p_filepath, READER_FILETYPE_TEI)

        self.m_tei_soup = None

    # Properties

    @property
    def chapter_count(self):
        return len(self.m_aolm_text.m_body.find_all("div1", attrs={"type": "chapter"}))

    @property
    def soup(self):
        return self.m_tei_soup

    # Methods

    def get_chapter(self, p_chapter_number):

        """
        <div1 type="chapter" xml:id="la0238">
        <pb n="1" xml:id="pb0001"/>
        <head rend="toc">Chapter I.</head>
        <figure rend="ch-init" xml:id="y00101">
        """

        chapters = self.m_aolm_text.m_body.find_all("div1", attrs={"type": "chapter"})
        found_chapter = None
        for chapter in chapters:
            if f"Chapter {AOLMTextUtilities.roman_numeral_from_decimal(p_chapter_number)}." == chapter.head.string:
                found_chapter = chapter
                break
        
        text_lines = []
        if found_chapter:
            
            paragraphs = found_chapter.find_all("p")
            
            for paragraph in paragraphs:
                for child in paragraph.children:
                    if type(child) is NavigableString:
                        if len(child.strip()) > 0:
                            text_lines.append(child.strip())

        return text_lines

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
def main():

    test_filepath = f"{os.getcwd()}{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}mtpo{os.sep}"
    
    test_file = "MTDP10000_edited.xml"
    # test_file = "chapter_example.xml"
    reader = MTPOHuckFinnReader(test_filepath + test_file)
    reader.read()
    print(reader.get_chapter(1))


if "__main__" == __name__:
    main()
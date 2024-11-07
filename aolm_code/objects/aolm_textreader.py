# Author: Jonathan Armoza
# Created: September 16, 2024
# Purpose: Function-based, factory class for reading (produces AOLMText objects)

# Imports

# Built-ins
from collections import Counter
import os

# Custom
from aolm_text import AOLMText


# Globals

# Supported file types
READER_FILETYPE_AOLM = "aolm"
READER_FILETYPE_HATHI = "hathi"
READER_FILETYPE_JSON = "json"
READER_FILETYPE_TEI = "tei"
READER_FILETYPE_TXT = "txt"


# Classes

class AOLMTextReader:

    # Constructor

    def __init__(self, p_filepath, p_filetype=READER_FILETYPE_TXT):

        # Text reader contains a text object based on the file parameters
        self.m_aolm_text = AOLMText(p_filepath, p_filetype)

    # Private methods

    def __hydrate_aolm_file(self):
        pass

    def __hydrate_hathi_file(self):
        pass

    def __read_file_as_json(self):
        pass

    def __read_file_as_tei(self):
        pass

    def __read_file_as_txt(self):

        # Read in the text line by line
        with open(self.m_filepath, "r") as text_file:
            self.m_text_lines = text_file.readlines()

    # Properties

    @property
    def body(self):
        return self.m_aolm_text.body

    # Public methods

    def read(self):

        # 1. Open the text file for reading
        if os.path.exists(self.m_filepath):

            if READER_FILETYPE_AOLM is self.m_filetype:
                self.__hydrate_aolm_file()
            elif READER_FILETYPE_HATHI is self.m_filetype:
                self.__hydrate_hathi_file()
            elif READER_FILETYPE_JSON is self.m_filetype:
                self.__read_file_as_json()
            elif READER_FILETYPE_TEI is self.m_filetype:
                self.__read_file_as_tei()
            elif READER_FILETYPE_TXT is self.m_filetype:
                self.__read_file_as_txt()
            else:
                raise Exception(f"File type {self.m_filetype} not supported.")
        else:
            raise FileNotFoundError(f"Cannot find file {self.m_filepath}")

    # Properties

    @property
    def text_as_lines(self):
        return self.m_text_lines
    @property
    def text_as_string(self):
        return "\n".join(self.m_text_lines)
    @property
    def aolm_text(self):
        return self.m_aolm_text
    @property
    def filepath(self):
        return self.m_aolm_text.filepath
    @property
    def filetype(self):
        return self.m_aolm_text.filetype
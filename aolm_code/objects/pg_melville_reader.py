# Author: Jonathan Armoza
# Created: July 10, 2025
# Purpose: Defines AOLM Text Reader to read Project Gutenberg (PG) versions of
#          Herman Melville's novels

# Imports

# Built-ins
import glob
import json
import os
import re
import sys

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Custom
from aolm_data_reading import melville_source_directory
from aolm_textutilities import AOLMTextUtilities
from aolm_textreader import AOLMTextReader, READER_FILETYPE_JSON


# Classes

class PGMelvilleIngestion:

    # Constructor and private methods

    def __init__(self, p_filepath):

        self.m_filepath = p_filepath
        with open(self.m_filepath, "r", encoding="utf-8") as input_file:
            self.m_raw_text = input_file.readlines()

        self.m_chapters = self.__read_chapters()

    def __read_chapters(self):

        chapter_pattern = re.compile(r"^(CHAPTER\s+[IVXLCDM]+\.)(?!\S)", re.IGNORECASE)
        chapters = {}
        current_chapter = None
        current_content = []

        for line in self.m_raw_text:

            line = line.rstrip()

            match = chapter_pattern.match(line)
            if match:
                # Save the current chapter before starting a new one
                if current_chapter:
                    chapters[current_chapter] = current_content
                current_chapter = match.group(1).upper()
                current_content = [line]
            else:
                if current_chapter:
                    current_content.append(line)

        # Save the last chapter
        if current_chapter:
            chapters[current_chapter] = current_content

        return chapters
    
    # Public methods

    def output_as_json_file(self, p_json_filepath):

        output_json = {
            "components": {
                "body": self.m_chapters
            }
        }

        with open(p_json_filepath, "w", encoding="utf-8") as output_file:
            json.dump(output_json, output_file, ensure_ascii=False)


class PGMelvilleReader(AOLMTextReader):

    # Constructor and private methods
    
    def __init__(self, p_filepath):

        super().__init__(p_filepath, READER_FILETYPE_JSON)
        self.read()

    # Properties

    @property
    def chapter_count(self):
        return len(self.m_json["components"]["body"])
    @property
    def json(self):
        return self.m_json

    # Public methods

    def get_chapter(self, p_chapter_number):
        
        roman_numeral = AOLMTextUtilities.roman_numeral_from_decimal(p_chapter_number)
        body_id = f"CHAPTER {roman_numeral}."

        return self.m_json["components"]["body"][body_id] if body_id in self.m_json["components"]["body"] else []
    
    def has_chapter(self, p_chapter_number):

        roman_numeral = AOLMTextUtilities.roman_numeral_from_decimal(p_chapter_number)

        body_id = f"CHAPTER {roman_numeral}."     

        return body_id in self.m_json["components"]["body"]

    def read(self):

        with open(self.filepath, "r") as json_file:

            # A. Save raw file contents
            self.m_aolm_text.m_raw_file_contents = json_file.read()

            # B. Parse the TEI xml
            self.m_json = json.loads(self.m_aolm_text.m_raw_file_contents)

            # C. Separate metadata and body text tags
            self.m_aolm_text.m_body = self.m_json["components"]["body"]


# Test script

def main():

    ingest_mode = False

    if ingest_mode:
        
        # Produce JSON
        
        for input_filepath in glob.glob(melville_source_directory["collected"] + "*.txt"):

            ingestor = PGMelvilleIngestion(input_filepath)
            ingestor.output_as_json_file(melville_source_directory["novels_json"] + os.path.splitext(os.path.basename(input_filepath))[0] + ".json")
    else:

        # Test reading a JSON file as a reader object

        test_file = "confidence_man_2022_body_text.json"
        reader = PGMelvilleReader(melville_source_directory["novels_json"] + test_file)
        reader.read()
        print(reader.get_chapter(1))

if "__main__" == __name__:
    
    main()

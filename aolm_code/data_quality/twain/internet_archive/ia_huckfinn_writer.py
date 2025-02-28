# Author: Jonathan Armoza
# Created: January 17, 2025
# Purpose: Reads a text file and produces a demarcated json for the text

# Imports

# Built-ins
import json
import os
import re
import sys

# Add the project root to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.append(ROOT_DIR)
from definitions import add_lib_paths
add_lib_paths(sys)

# Custom
from aolm_textreader import AOLMTextReader
from aolm_textutilities import AOLMTextUtilities


# Classes

class IAHuckFinnWriter:

    # Constructor

    def __init__(self, p_text_filepath, p_json_filepath):

        self.m_text_filepath = p_text_filepath
        self.m_json_filepath = p_json_filepath

        self.m_textreader = AOLMTextReader(self.m_text_filepath)
        self.m_textreader.read()
        with open(self.m_json_filepath, "r") as input_file:
            self.m_json_template = json.load(input_file)

    # Public methods

    def populate_json_components(self, p_chapter_prefix="", p_page_skiplines=[]):

        components_json = {}

        for component in self.m_json_template["keys"]["order"]:

            # If component has subcomponents it will be dict with subcomponents, each an array of lines
            if "subcomponents" in self.m_json_template["keys"]["input"][component] and \
                self.m_json_template["keys"]["input"][component]["subcomponents"] == "True":

                components_json[component] = {}

                startline = self.m_json_template["keys"]["input"][component]["startline"].strip()
                endline = self.m_json_template["keys"]["input"][component]["endline"].strip()
                capturing = False
                current_chapter = None
                frontmatter_endline_seen = False
                frontmatter_endline = self.m_json_template["keys"]["input"]["frontmatter"]["endline"]

                for line in self.m_textreader.text_as_lines:

                    if frontmatter_endline.strip() == line.strip():
                        frontmatter_endline_seen = True
                    if not frontmatter_endline_seen:
                        continue

                    # 1. Read until we find startline
                    if startline == line.strip():
                        capturing = True

                    if capturing:
                        # 2. Read chapters - new chapter each time a "CHAPTER" prefix line is found
                        if line.strip().startswith("CHAPTER"):
                            current_chapter = p_chapter_prefix + line.strip()
                            components_json[component][current_chapter] = []
                            continue

                        found_skipline = False
                        for skipline in p_page_skiplines:
                            if len(AOLMTextUtilities.find_matches(line.strip(), skipline)):
                                found_skipline = True
                                break
                        if found_skipline:
                            continue

                        if current_chapter:
                            components_json[component][current_chapter].append(line.strip())

                        # 3. Stop saving once endline is found
                        if endline == line.strip():
                            capturing = False
                            break
            
            # Else, components is just an array of lines
            else:

                # Save from startline to endline as this component
                startline = self.m_json_template["keys"]["input"][component]["startline"].strip()
                endline = self.m_json_template["keys"]["input"][component]["endline"].strip()
                capturing = False
                captured_lines = []

                for line in self.m_textreader.text_as_lines:
                    if startline == line.strip():
                        capturing = True
                    if capturing:
                        captured_lines.append(line.strip())
                    if endline == line.strip():
                        capturing = False
                        break

                    components_json[component] = captured_lines           

        # Reread original json file
        with open(self.m_json_filepath, "r") as input_file:
            self.m_json_template = json.load(input_file)
        
        # Add new components json to json from file and write to disk
        self.m_json_template["components"] = components_json
        with open(self.m_json_filepath, "w") as output_file:
            json.dump(self.m_json_template, output_file)

        # with open(os.path.dirname(self.m_json_filepath) + os.sep + "temp.json", "w") as output_file:
        #     json.dump(self.m_json_template, output_file)



# Test script

def main():

    huckfinn_txt_file = "/Users/weirdbeard/Documents/school/aolm_full/data/twain/huckleberry_finn/internet_archive/txt/demarcated/incomplete/txt/235649-The Adventures Of Huckleberry Finn (1918)_djvu.txt"
    huckfinn_json_template = "/Users/weirdbeard/Documents/school/aolm_full/data/twain/huckleberry_finn/internet_archive/txt/demarcated/incomplete/json/235649-The Adventures Of Huckleberry Finn (1918)_incomplete-HuckFinn.json"

    page_headings_to_skip = [

        r".* Huckleberry Finn .*",
        r".* Huckleberry Finn",
        r"Huckleberry Finn .*",
        r"Huckleberry Finn"
    ]
    
    hf_json_writer = IAHuckFinnWriter(huckfinn_txt_file, huckfinn_json_template)
    hf_json_writer.populate_json_components(p_chapter_prefix="HUCKLEBERRYFINN_BODY_", p_page_skiplines=page_headings_to_skip)

if "__main__" == __name__:
    main()

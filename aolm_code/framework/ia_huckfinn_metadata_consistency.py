# Author: Jonathan Armoza
# Created: July 30, 2024
# Purpose: Examines integrity of Huck Finn Internet Archive editions metadata

# Imports

# Built-ins
import glob
import json
import os


# Classes

class InternetArchiveMetadata_Assessment:

    def __init__(self, p_metadata_folder):

        self.m_source_folder = p_metadata_folder
        self.m_metadata_map = {}

        # Read in all json data
        for filepath in glob.glob(f"{self.m_source_folder}{os.sep}*.json"):
            with open(filepath, "r") as input_file:
                self.m_metadata_map[os.path.basename(filepath)] = json.load(input_file)

        # Super set of json file keys
        self.m_allkeys = list(set([key for filename in self.m_metadata_map for key in self.m_metadata_map[filename] ]))

        # Data quality scores
        self.m_collection_score = 0
        self.m_file_scores = { filename: 0 for filename in self.m_metadata_map }

    @property
    def collection_score(self):
        return self.m_collection_score
    def file_score(self, p_filename):
        return self.m_file_scores[p_filename]
    @property
    def filenames(self):
        return list(self.m_metadata_map.keys())
    @property
    def shared_tags(self):
        key_lists = [list(self.m_metadata_map[filename]) for filename in self.m_metadata_map]
        return set().union(*key_lists)
    @property
    def text_count(self):
        return len(self.m_metadata_map.keys())


    def make_assessment(self):

        number_of_keys = len(self.m_allkeys)

        for filename in self.m_metadata_map:
            self.m_file_scores[filename] = self.consistency_metric(filename)
        self.m_collection_score = sum(self.m_file_scores.values()) / len(self.m_file_scores)
        
    def consistency_metric(self, p_filename):

        # Score is percentage of keys present in this metadata file out of all keys in the collection of files
        return 100.0 * len(self.m_metadata_map[p_filename].keys()) / len(self.m_allkeys)

    def integrity_metric(self):

        shared_tags = self.shared_tags

        # Create a map of all tag values for all shared tags
        tag_values = {tag: [] for tag in shared_tags}
        for tag in shared_tags:
            for filename in self.m_metadata_map:
                if tag in self.m_metadata_map[filename]:
                    tag_values[tag].append(self.m_metadata_map[filename][tag])
            print("=" * 80)
            print(tag_values[tag])
            tag_values[tag] = list(set(tag_values[tag]))

        # Integrity score per tag
        integrity_scores = {tag: 100.0 * len(tag_values[tag]) / self.text_count for tag in tag_values}

        # Return average tag integrity score as integrity metric for this text collection
        return sum(integrity_scores.values()) / len(tag_values.keys()) 


# Main script

def main():

    ia_metadata_folder = f"{os.getcwd()}{os.sep}..{os.sep}..{os.sep}data{os.sep}twain{os.sep}huckleberry_finn{os.sep}internet_archive{os.sep}metadata"
    ia_assessment_obj = InternetArchiveMetadata_Assessment(ia_metadata_folder)

    sorted_shared_tags = list(ia_assessment_obj.shared_tags)
    sorted_shared_tags.sort()
    for tag in sorted_shared_tags:
        print(tag)

    ia_assessment_obj.make_assessment()

    for filename in ia_assessment_obj.filenames:
        print(f"{filename}: {ia_assessment_obj.file_score(filename)}")
    print(f"Collection score: {ia_assessment_obj.collection_score}")

    print(f"Tag integrity metric: {ia_assessment_obj.integrity_metric()}")

if "__main__" == __name__:
    main()

    
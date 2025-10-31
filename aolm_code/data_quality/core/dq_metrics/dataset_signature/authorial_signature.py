# Author: Jonathan Armoza
# Created: May 19, 2025
# Purpose: Data quality metric that looks to the relative linguistic signature of texts

# Imports

# Third party
import numpy as np
import os

# Custom
from aolm_textutilities import AOLMTextUtilities
from dq_metric import DataQualityMetric

# Objects

class DatasetSignature_AuthorialSignature(DataQualityMetric):

    # Constructor and private methods

    def __init__(self, p_source_files):
    
        self.m_source_files = p_source_files

        self.m_results = {

            "authorial_signature": {},
            "vocab_vectors": { source_file: None for source_file in self.m_source_files }
        }
        self.m_evaluations = { 

            "metric": None,
            "submetric": { "least_like": None, "most_like": None }
        }

        self.m_sort_signature_distances = False

    # Public methods

    def compute(self):

        # 1. Compute word vectors for each individual text
        for source_file in self.m_results["vocab_vectors"]:
            self.m_results["vocab_vectors"][source_file] = DatasetSignature_AuthorialSignature.get_signature(source_file)

        # 2. Compute the author signature word vector
        for source_file in self.m_results["vocab_vectors"]:
            for word in self.m_results["vocab_vectors"][source_file]:
                self.m_results["authorial_signature"].setdefault(word, 0)
                self.m_results["authorial_signature"][word] += self.m_results["vocab_vectors"][source_file][word]
        for word in self.m_results["authorial_signature"]:
            self.m_results["authorial_signature"][word] = self.m_results["authorial_signature"][word] / len(self.m_source_files)

    def evaluate(self):

        # 1. Primary evaluation of this metric is the overall average word vector of all source files
        self.m_evaluations["metric"] = self.m_results["authorial_signature"]

        # 2. Submetrics are those source files (and their distances) closest and furthest to the authorial signature vector
        self.m_evaluations["submetric"]["least_like"] = DatasetSignature_AuthorialSignature.get_superlative_distance(self.m_results["authorial_signature"], self.m_source_files)
        self.m_evaluations["submetric"]["most_like"] = DatasetSignature_AuthorialSignature.get_superlative_distance(self.m_results["authorial_signature"], self.m_source_files, p_lowest=True)

        self.m_evaluations["submetric"]["signature_distances"] = \
            DatasetSignature_AuthorialSignature.get_signature_distances(
                self.m_results["authorial_signature"],
                self.m_source_files,
                self.m_sort_signature_distances
            )
    
    # Properties

    @property
    def least_like_author_signature(self):
        return self.m_evaluations["submetric"]["least_like"]
    @property
    def most_like_author_signature(self):
        return self.m_evaluations["submetric"]["most_like"]    
    @property
    def signature(self):
        return self.m_results["authorial_signature"]
    @property
    def signature_distances(self):
        return self.m_evaluations["submetric"]["signature_distances"]
    
    # Members
    def toggle_signature_distance_sort(self, p_sort_value):
        self.m_sort_signature_distances = p_sort_value

    # Static fields and methods

    @staticmethod
    def dict_to_collection_word_vector(p_dict_to_convert, p_master_dict):

        # 0. Authorial signature contains all words of the collection
        all_words = p_master_dict.keys()

        # 1. Create a vector with all words regardless of whether they are present in the given dictionary
        new_dict = { word: p_dict_to_convert.get(word, 0) for word in all_words }
        word_vector = [ (word, new_dict[word]) for word in new_dict ]
        word_vector = sorted(word_vector, key=lambda item: item[0])

        return word_vector
    
    @staticmethod
    def dict_to_word_vector(p_dict_to_convert):

        word_vector = [ (word, p_dict_to_convert[word]) for word in p_dict_to_convert ]
        return sorted(word_vector, key=lambda item: item[0])

    @staticmethod
    def get_signature(p_source_file):

        # 1. Read in the text file
        with open(p_source_file, "r") as input_file:
            body_text = input_file.read()

        # 2. Create a word vector (in dict form) based off of the vocabulary of the text file
        return AOLMTextUtilities.word_count_from_string(body_text)
    
    @staticmethod
    def get_signature_distances(p_compared_dict, p_text_files, p_sorted=True):
        
        text_distances = []

        compared_vector_as_tuple = DatasetSignature_AuthorialSignature.dict_to_word_vector(p_compared_dict)
        compared_vector = np.array([word_tuple[1] for word_tuple in compared_vector_as_tuple])
        
        for filepath in p_text_files:

            text_signature = DatasetSignature_AuthorialSignature.get_signature(filepath)
            text_signature_vector_as_tuple = DatasetSignature_AuthorialSignature.dict_to_collection_word_vector(text_signature, p_compared_dict)
            text_signature_vector = np.array([word_tuple[1] for word_tuple in text_signature_vector_as_tuple])

            # Cosine similarity between vectors
            text_distances.append([
                os.path.basename(filepath),
                np.dot(compared_vector, text_signature_vector.T) / (np.linalg.norm(compared_vector) * np.linalg.norm(text_signature_vector))
            ])

        # Compute cosine distance for all cosine similarity values
        for index in range(len(text_distances)):
            text_distances[index][1] = 1 - text_distances[index][1]

        return sorted(text_distances, key=lambda item: item[1], reverse=True) if p_sorted else text_distances

    @staticmethod
    def get_superlative_distance(p_compared_dict, p_text_files, p_lowest=False):

        text_distances = {}

        compared_vector_as_tuple = DatasetSignature_AuthorialSignature.dict_to_word_vector(p_compared_dict)
        compared_vector = np.array([word_tuple[1] for word_tuple in compared_vector_as_tuple])
        
        distance = (p_text_files[0], 1000000 if p_lowest else 0)
        
        for filepath in p_text_files:

            text_signature = DatasetSignature_AuthorialSignature.get_signature(filepath)
            text_signature_vector_as_tuple = DatasetSignature_AuthorialSignature.dict_to_collection_word_vector(text_signature, p_compared_dict)
            text_signature_vector = np.array([word_tuple[1] for word_tuple in text_signature_vector_as_tuple])

            # Cosine similarity between vectors
            text_distances[filepath] = np.dot(compared_vector, text_signature_vector.T) / (np.linalg.norm(compared_vector) * np.linalg.norm(text_signature_vector))

            # Calculate cosine distance
            text_distances[filepath] = 1 - text_distances[filepath]
            
            if (p_lowest and text_distances[filepath] < distance[1]) or \
                (not p_lowest and text_distances[filepath] > distance[1]):
                distance = (filepath, text_distances[filepath])

        return distance
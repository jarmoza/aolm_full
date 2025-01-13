# Author: Jonathan Armoza
# Created: January 11, 2025
# Purpose: Data quality metric child class for Dataset completeness - Metadata
#          Sufficiency

# Imports

# Built-ins
from statistics import mean

# Custom
from aolm_textutilities import AOLMTextUtilities
from dq_metric import DataQualityMetric


class DatasetCompleteness_MetadataSufficiency(DataQualityMetric):

    def __init__(self, p_name, p_input):

        super().__init__(p_name, p_input)

    def compute(self):

        # Experiment 1 - Metadata Quality

        # NOTES
        # “Metadata assessment tests first for existence and completeness
        # (percentage of tables defined, percentage of columns defined; percentage
        # of codefields supported by references data, etc.) and next for the
        # clarity and quality of definitions (clear, comprehensible, unambiguous,
        # grammatically correct, etc.) and consistency of representation (the same
        # field content defined in the same way).” (224)

        # 2. Clarity and quality of definitions (clear, comprehensible, unambiguous,
        # grammatically correct, etc.)

        # Maybe here can be a more qualitative score based on the state of the metadata in the original files,
        # the difficulty it took to extract and shape the metadata, etc.
        # For example: A qualitative score based on a standard of qualitative scoring for this category
        # and that reflects the state of the data and the work required, as mnetioned above

        # 3. Consistency of representation (the same field content defined in the same way)

        self.m_results = {

            "existence_and_completeness": {},
            "clarity_and_quality": {},
            "consistency_of_representation": {}
        }

        # 1. Existence and Completeness
        # A. Percentage of tables defined
        # B. Percentage of columns defined
        # C. Percentage of codefields supported by reference data

        self.add_explanation(
            "existence_and_completeness",
            "Existence score:\n" +
            "Editions on Project Gutenberg vs # editions in entire dataset (how many editions are on PG compared to everyone else)\n" +
            "Completeness score: Each edition gets a score that is #edition keys / #total unique keys from the overall dataset\n" +
            "These then get tallied into an overall score for the Project Gutenberg site"
        )

        # A. Percentage of tables defined (All works have header metadata)
        self.m_results["existence_and_completeness"]["percent_tables_defined"] = 100.0

        # B. Percentage of columns defined
        unkeyed_key = "unkeyed_fields"
        self.m_results["existence_and_completeness"]["percent_key_coverage"] = {}

        # I. Get key set for all metadata files
        pg_metadata_keyset = AOLMTextUtilities.get_keyset([self.m_input[filepath] for filepath in self.m_input], [unkeyed_key])
        pg_metadata_keyset.remove(unkeyed_key)

        # II. Calculate percentage coverage each edition has of the total keyset
        for filepath in self.m_input:
            edition_keys = AOLMTextUtilities.get_keyset([self.m_input[filepath]], [unkeyed_key])
            edition_keys.remove(unkeyed_key)
            self.m_results["existence_and_completeness"]["percent_key_coverage"][filepath] = 100 * len(edition_keys) / float(len(pg_metadata_keyset))
        
        # 2. Clarity and quality of definitions
        
        self.add_explanation(
            "clarity_and_quality",
            "Number of unkeyed variables / total key count"
        )

        # A. How many fields are unkeyed?
        total_keyset_len = (len(pg_metadata_keyset))
        unkeyed_count_by_edition = {}
        for filepath in self.m_input:
            edition_unkeyed = self.m_input[filepath][unkeyed_key].keys()
            unkeyed_count_by_edition[filepath] = len(edition_unkeyed) / float(total_keyset_len)
            self.m_results["clarity_and_quality"][filepath] = 100 * len(edition_unkeyed) / float(total_keyset_len)

        # 3. Consistency of representation
        
        self.add_explanation(
            "consistency_of_representation",
            "Tallies number of mismatches across each unique value and then divides that by the total number of values in metadata of all editions"
        )
        
        # A. Get lists of duplicated, unique values
        pg_metadata_valueset = AOLMTextUtilities.get_valueset([self.m_input[filepath] for filepath in self.m_input])
        valuematch_dict = AOLMTextUtilities.levenshtein_listcompare(pg_metadata_valueset)
        
        # B. Determine mismatches as percentage of the total number of values
        # represented in the metadata of all editions
        mismatch_count = 0
        for key in valuematch_dict:
            if len(valuematch_dict[key]) > 0:
                mismatch_count += len(valuematch_dict[key])
        self.m_results["consistency_of_representation"] = 100 * mismatch_count / float(len(pg_metadata_valueset))

        return self.m_results
    
    def evaluate(self):
        
        # self.m_results = {

        #     "existence_and_completeness": {
        #         "percent_tables_defined": 0,
        #         "percent_key_coverage": {}
        #     },
        #     "clarity_and_quality": {},
        #     "consistency_of_representation": {}
        # }

        # 1. Calculate evaluations of subsubmetrics
        subsubmetric_evaluations = {
            "existence_and_completeness": {
                "percent_tables_defined": self.m_results["existence_and_completeness"]["percent_tables_defined"],
                "percent_key_coverage": mean(self.m_results["existence_and_completeness"]["percent_key_coverage"].values())
            },
            "clarity_and_quality": mean(self.m_results["clarity_and_quality"].values()),
            "consistency_of_representation": self.m_results["consistency_of_representation"]
        }

        # 2. Calculate evaluation of submetrics
        submetric_evaluations = {
            "existence_and_completeness": mean(subsubmetric_evaluations["existence_and_completeness"].values()),
            "clarity_and_quality": subsubmetric_evaluations["clarity_and_quality"],
            "consistency_of_representation": subsubmetric_evaluations["consistency_of_representation"]
        }

        # 3. Metric is weighted mean of submetrics
        metric_evaluation = mean(submetric_evaluations.values())

        return metric_evaluation
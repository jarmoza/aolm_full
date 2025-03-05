# Author: Jonathan Armoza
# Created: January 11, 2025
# Purpose: Data quality metric child class for Dataset completeness - Metadata
#          Sufficiency

# Imports

# Built-ins
import os
from statistics import mean

# Custom
from aolm_textutilities import AOLMTextUtilities
from dq_metric import DataQualityMetric


class DatasetCompleteness_MetadataSufficiency(DataQualityMetric):

    def __init__(self, p_name, p_input, p_source_id, p_work_title, p_metadata_directory):

        super().__init__(p_name, p_input,
                         p_source_id=p_source_id,
                         p_work_title=p_work_title,
                         p_path=p_metadata_directory)
        
    def __build_eval_output_line__(self):

        # 1. Base data quality metric evaluation keys
        key_value_map = { key: None for key in DataQualityMetric.s_build_output_line_keys }
        key_value_map["source"] = self.m_source_id
        key_value_map["work_title"] = self.m_work_title
        key_value_map["edition_title"] = os.path.basename(os.path.splitext(self.m_path)[0]) if len(os.path.basename(self.m_path)) else self.m_source_id
        key_value_map["metric"] = DatasetCompleteness_MetadataSufficiency.s_metric_name
        key_value_map["value"] = self.m_evaluations["metric"]
        key_value_map["compared_against"] = self.baseline_source_id
        key_value_map["filepath"] = self.m_path
        
        # 2. Metadata sufficiency-specific evaluation keys
        key_value_map["submetric__existence_and_completeness"] = self.m_evaluations["submetric"]["existence_and_completeness"]
        key_value_map["submetric__clarity_and_quality"] = self.m_evaluations["submetric"]["clarity_and_quality"]
        key_value_map["submetric__consistency_of_representation"] = self.m_evaluations["submetric"]["consistency_of_representation"]
        key_value_map["subsubmetric_existence_and_completeness__percent_tables_defined"] = \
            self.m_evaluations["subsubmetric"]["existence_and_completeness"]["percent_tables_defined"]
        key_value_map["subsubmetric_existence_and_completeness__percent_key_coverage"] = \
            self.m_evaluations["subsubmetric"]["existence_and_completeness"]["percent_key_coverage"]        

        # 3. Build line with key order [build keys, metric-specific evaluation keys]
        keys_in_order = list(DataQualityMetric.s_build_output_line_keys)
        keys_in_order.extend(DatasetCompleteness_MetadataSufficiency.s_eval_output_line_keys)
        line_dict = { key: key_value_map.get(key, None) for key in keys_in_order }
        line_str_array = [line_dict[key] for key in keys_in_order]

        return ",".join(map(str, line_str_array)) + "\n"


    def __build_output_line__(self):

        key_value_map = {
            
            "source": self.m_source_id,
            "work_title": self.m_work_title,
            "edition_title": os.path.basename(os.path.splitext(self.m_path)[0]) if len(os.path.basename(self.m_path)) else self.m_source_id,
            "metric": DatasetCompleteness_MetadataSufficiency.s_metric_name,
            "value": self.m_evaluations["metric"],
            "compared_against": self.baseline_source_id,
            "filename": os.path.basename(self.m_path),
            "filepath": self.m_path
        }

        line_dict = { key: key_value_map.get(key, None) for key in DataQualityMetric.s_build_output_line_keys }
        line_str_array = [line_dict[key] for key in DataQualityMetric.s_build_output_line_keys]

        return ",".join(map(str, line_str_array)) + "\n"


    @property
    def output(self):
        return self.__build_output_line__()
    @property
    def eval_output(self):
        return self.__build_eval_output_line__()

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
        if unkeyed_key in pg_metadata_keyset:
            pg_metadata_keyset.remove(unkeyed_key)

        # II. Calculate percentage coverage each edition has of the total keyset
        for filepath in self.m_input:
            edition_keys = AOLMTextUtilities.get_keyset([self.m_input[filepath]], [unkeyed_key])
            if unkeyed_key in edition_keys:
                edition_keys.remove(unkeyed_key)

            percent_key_coverage = 100 * len(edition_keys) / float(len(pg_metadata_keyset))
            assert 0 <= percent_key_coverage <= 100, f"Percent key coverage out of range: {percent_key_coverage}"
            self.m_results["existence_and_completeness"]["percent_key_coverage"][filepath] = percent_key_coverage
            # self.m_results["existence_and_completeness"]["percent_key_coverage"][filepath] = 100 * len(edition_keys) / float(len(pg_metadata_keyset))
        
        # 2. Clarity and quality of definitions
        
        self.add_explanation(
            "clarity_and_quality",
            "Number of unkeyed variables / total key count"
        )

        # A. How many fields are unkeyed?
        total_keyset_len = (len(pg_metadata_keyset))
        for filepath in self.m_input:
            edition_unkeyed = [] if unkeyed_key not in self.m_input[filepath] else self.m_input[filepath][unkeyed_key].keys()

            clarity_and_quality = 100 - (100 * len(edition_unkeyed) / float(total_keyset_len))
            assert 0 <= clarity_and_quality <= 100, f"Clarity and quality out of range: {clarity_and_quality}"
            self.m_results["clarity_and_quality"][filepath] = clarity_and_quality            
            # self.m_results["clarity_and_quality"][filepath] = 100 - (100 * len(edition_unkeyed) / float(total_keyset_len))

        # 3. Consistency of representation
        
        self.add_explanation(
            "consistency_of_representation",
            "Tallies number of mismatches across each unique value and then divides that by the total number of values in metadata of all editions"
        )
        
        # NOTE: These is a problem with this algorithm overcounting past 100

        # Try #2

        # A. Create a list of all unique keys in the metadata files being examined
        all_metadata_keys = list(set([ key for filepath in self.m_input for key in self.m_input[filepath] if key != unkeyed_key  ]))

        # B. Create a dictionary of lists of unique values for each unique key in the metadata files being examined
        all_metadata_values = { key: [] for key in all_metadata_keys }
        for filepath in self.m_input:
            for key in self.m_input[filepath]:
                if key not in all_metadata_keys:
                    continue
                if isinstance(self.m_input[filepath][key], list):
                    all_metadata_values[key].extend(self.m_input[filepath][key])
                else:
                    all_metadata_values[key].append(self.m_input[filepath][key])
        for key in all_metadata_keys:
            all_metadata_values[key] = list(set(all_metadata_values[key]))

        # C. Create distance lists between all values for each key
        mismatch_dict = { key: None for key in all_metadata_keys }
        for key in all_metadata_keys:
            mismatch_dict[key] = AOLMTextUtilities.levenshtein_listcompare(all_metadata_values[key], p_dedupe=True)

        # # A. Get lists of duplicated, unique values
        pg_metadata_valueset = AOLMTextUtilities.get_valueset([self.m_input[filepath] for filepath in self.m_input])
        pg_metadata_unique_valueset = list(set(pg_metadata_valueset))
        
        # B. Determine mismatches as percentage of the total number of values
        # represented in the metadata of all editions
        mismatch_count = 0
        for key in mismatch_dict:
            for value in mismatch_dict[key]:
                if len(mismatch_dict[key][value]) > 0:
                    mismatch_count += len(mismatch_dict[key][value])

        consistency_of_representation = 100.0 - (100 * mismatch_count / float(len(pg_metadata_unique_valueset)))
        assert 0 <= consistency_of_representation <= 100, f"Consistency of representation out of range: {consistency_of_representation}"
        self.m_results["consistency_of_representation"] = consistency_of_representation

        return self.m_results
    
    def evaluate(self):

        # 0. Clear out any old evaluations
        super()._reset_evaluations()

        # 1. Calculate evaluations of subsubmetrics
        self.m_evaluations["subsubmetric"] = {
            "existence_and_completeness": {
                "percent_tables_defined": self.m_results["existence_and_completeness"]["percent_tables_defined"],
                "percent_key_coverage": mean(self.m_results["existence_and_completeness"]["percent_key_coverage"].values())
            },
            "clarity_and_quality": mean(self.m_results["clarity_and_quality"].values()),
            "consistency_of_representation": self.m_results["consistency_of_representation"]
        }

        # 2. Calculate evaluation of submetrics
        self.m_evaluations["submetric"] = {
            "existence_and_completeness": mean(self.m_evaluations["subsubmetric"]["existence_and_completeness"].values()),
            "clarity_and_quality": self.m_evaluations["subsubmetric"]["clarity_and_quality"],
            "consistency_of_representation": self.m_evaluations["subsubmetric"]["consistency_of_representation"]
        }

        # 3. Metric is weighted mean of submetrics
        self.m_evaluations["metric"] = mean(self.m_evaluations["submetric"].values())

        return self.m_evaluations["metric"]
    
    # Static fields and methods

    s_eval_output_line_keys = [

        "submetric__existence_and_completeness",
        "submetric__clarity_and_quality",
        "submetric__consistency_of_representation",
        "subsubmetric_existence_and_completeness__percent_tables_defined",
        "subsubmetric_existence_and_completeness__percent_key_coverage"
    ]

    s_metric_name = "metadata_sufficiency"

    @staticmethod
    def write_eval_output_header(p_output_file):

        eval_header_keys = list(DataQualityMetric.s_build_output_line_keys)
        eval_header_keys.extend(DatasetCompleteness_MetadataSufficiency.s_eval_output_line_keys)

        p_output_file.write(",".join(eval_header_keys) + "\n")
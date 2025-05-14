# Author: Jonathan Armoza
# Created: May 14, 2025
# Purpose: Contains the script to produce data quality heatmaps of Twain's 'Adventures of Huckleberry Finn'

# Imports

# Built-ins
import glob
import json
import os

# Custom

from dq_metrics.dataset_completeness.metadata_sufficiency import DatasetCompleteness_MetadataSufficiency
from dq_metrics.dataset_completeness.recordcounts_to_controlrecords import DatasetCompleteness_RecordCountsToControlRecords
from dq_metrics.dataset_validity.lexical_validity import DatasetValidity_LexicalValidity


# Globals

# Main script

def main():
    
    # Overall data quality results file
    input_fileprefix = f"{os.getcwd()}{os.sep}experiments{os.sep}outputs{os.sep}huckfinn_dq_experiment_"

    for input_filepath in glob.glob(input_fileprefix + "*.*"):

        if DatasetValidity_LexicalValidity.s_metric_name in input_filepath:
            pass
        elif DatasetCompleteness_MetadataSufficiency.s_metric_name in input_filepath:
            pass
        elif DatasetCompleteness_RecordCountsToControlRecords.s_metric_name in input_filepath:
            pass

    # Read lexical validity json and create heatmaps of lexical validity within a work (by chapter) and within a collection



if "__main__" == __name__:
    main()
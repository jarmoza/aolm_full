# Author: Jonathan Armoza
# Created: February 15, 2022
# Purpose: Contains the abstract base class to be implemented by all 'Art of
#          Literary Modeling' data quality metrics

# Imports

# Built-ins
from abc import ABC, abstractmethod     # Python abstract classes

# Third party
import spacy

# Custom
# from dq_output import DataQualityOutput

# Classes

"""
    'DataQualityMetric' is an abstract base class for all data quality metric
    objects. This abstraction is made for metrics to have a standardized set of
    methods and properties so that they may be collected and acted upon
    uniformly across different sets of analyses (i.e. in a data quality
    assessment framework).
"""
class DataQualityMetric:

    # Constructor

    def __init__(self, p_name, p_text_readers, 
                 p_source_id="", p_work_title="", p_collection_title="", p_path="", p_baseline_source_id="N/A"):

        # 0. Save parameters
        self.m_name = p_name
        self.m_input = p_text_readers

        # A. Optional parameters
        self.m_source_id = p_source_id
        self.m_work_title = p_work_title
        self.m_collection_title = p_collection_title
        self.m_path = p_path
        self.m_baseline_source_id = p_baseline_source_id

        # 1. Other class fields
        self.m_metric_min = 0.0
        self.m_metric_max = 100.0
        self.m_explanation = {}
        self.m_spacymodel = None
        self.m_results = {}
        self.m_spacymodel_name = "en_core_web_sm"
        self.m_urtext_name = ""

        self.m_evaluations = {
            "subsubmetric": {},
            "submetric": {},
            "metric": 0.0
        }

        # This may refer to a single DataQualityOutput or multiple
        self.m_ouput = None

    def _reset_evaluations(self):

        self.m_evaluations = {
            "subsubmetric": {},
            "submetric": {},
            "metric": 0.0
        }        

    # Properties

    @property
    def eval_output(self):
        return ""
    @property
    def input(self):
        return self.m_input
    @input.setter
    def input(self, p_input):
        self.m_input = p_input
    @property
    def output(self):
        return ""
    @property
    def source_id(self):
        return self.m_source_id
    @property
    def work_title(self):
        return self.m_work_title
    @property
    def path(self):
        return self.m_path
    @property
    def baseline_source_id(self):
        return self.m_baseline_source_id
    
    @property
    def results(self):
        return self.m_results
    @property
    def evaluations(self):
        return self.m_evaluations
    
    
    @property
    def metric_evaluation(self):
        return self.m_evaluations["metric"]
    @metric_evaluation.setter
    def metric_evaluation(self, p_metric_evaluation):
        self.m_evaluations["metric"] = p_metric_evaluation
    @property
    def submetric_evaluation(self):
        return self.m_evaluations["submetric"]
    @submetric_evaluation.setter
    def submetric_evaluation(self, p_submetric_evaluation):
        self.m_evaluations["submetric"] = p_submetric_evaluation
    @property
    def subsubmetric_evaluation(self):
        return self.m_evaluations["subsubmetric"]
    @subsubmetric_evaluation.setter
    def subsubmetric_evaluation(self, p_subsubmetric_evaluation):
        self.m_evaluations["subsubmetric"] = p_subsubmetric_evaluation
      
    @property
    def metric_max(self):
        return self.m_metric_max
    @metric_max.setter
    def metric_max(self, p_metric_max):
        self.m_metric_max = p_metric_max
    @property
    def metric_min(self):
        return self.m_metric_min
    @metric_min.setter
    def metric_min(self, p_metric_min):
        self.m_metric_min = p_metric_min
    @property
    def name(self):
        return self.m_name
    @property
    def urtext_name(self):
        return self.m_urtext_name
    @urtext_name.setter
    def urtext_name(self, p_urtext_name):
        self.m_urtext_name = p_urtext_name
    @property
    def spacymodel_name(self):
        return self.m_spacymodel_name
    @spacymodel_name.setter
    def spacymodel_name(self, p_spacymodel_name):
        self.m_spacymodel_name = p_spacymodel_name
    @property
    def result(self):
        return self.m_results
    @result.setter
    def result(self, p_new_results):
        self.m_results = p_new_results

    # Public methods

    def add_explanation(self, p_key, p_text):
        self.m_explanation[p_key] = p_text
    def compute(self):
        self.m_results = {}
    def explanation(self, p_key=""):
        return self.m_explanation[p_key] if len(p_key) else self.m_explanation
    def evaluate(self):
        return self.m_evaluations
    def load_spacymodel(self):
        self.m_spacymodel = spacy.load(self.m_spacymodel_name)
    def run(self, p_show_explanations=False):
        self.compute()
        self.show_results(p_show_explanations=p_show_explanations)
    def set_evalmetric_value(self, p_evalmetric_value):
        self.m_evaluations["metric"] = p_evalmetric_value
    def show_results(self, p_show_explanations=False):
        for key in self.m_results:
            print("=" * 80)
            print(key)
            if p_show_explanations:
                print(self.explanation(key))
            print(self.m_results[key])
    
    # Static fields and methods
    
    s_build_output_line_keys = [
        "source",
        "work_title",
        "edition_title",
        "metric",
        "value",
        "compared_against",
        "filename",
        "filepath"
    ]
    
    s_not_available = "N/A"

    @staticmethod
    def write_output_header(p_output_file):
        p_output_file.write(",".join(DataQualityMetric.s_build_output_line_keys) + "\n")
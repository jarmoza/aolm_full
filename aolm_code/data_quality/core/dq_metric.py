# Author: Jonathan Armoza
# Created: February 15, 2022
# Purpose: Contains the abstract base class to be implemented by all 'Art of
#          Literary Modeling' data quality metrics

# Imports

# Built-ins
from abc import ABC, abstractmethod     # Python abstract classes

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

    def __init__(self, p_name, p_input, p_compute_fn):

        # 0. Save parameters
        self.m_name = p_name
        self.m_input = p_input
        self.m_compute = p_compute_fn

        # 1. Other class fields
        self.m_metric_min = 0.0
        self.m_metric_max = 100.0
        self.m_explanation = {}
        self.m_result = {}
        self.m_urtext_name = ""

    # Properties

    @property
    def input(self):
        return self.m_input
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
    def result(self):
        return self.m_result
    @result.setter
    def result(self, p_new_result):
        self.m_result = p_new_result

    # Public methods

    def add_explanation(self, p_key, p_text):
        self.m_explanation[p_key] = p_text
    def compute(self):
        self.m_result = self.m_compute(self)
    def explanation(self, p_key=""):
        return self.m_explanation[p_key] if len(p_key) else self.m_explanation
    def run(self, p_show_explanations=False):
        self.compute()
        self.show_results(p_show_explanations=p_show_explanations)
    def show_results(self, p_show_explanations=False):
        for key in self.m_result:
            print("=" * 80)
            print(key)
            if p_show_explanations:
                print(self.explanation(key))
            print(self.m_result[key])
    
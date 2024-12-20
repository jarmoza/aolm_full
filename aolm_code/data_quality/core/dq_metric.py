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
        self.m_explanation = {}
        self.m_result = {}

    # Properties

    @property
    def input(self):
        return self.m_input
    @property
    def name(self):
        return self.m_name
    @property
    def result(self):
        return self.m_result
    @result.setter
    def result(self, p_new_result):
        self.m_result = p_new_result

    # Methods

    def add_explanation(self, p_key, p_text):
        self.m_explanation[p_key] = p_text
    def compute(self):
        self.m_result = self.m_compute(self)
    def explanation(self, p_key=""):
        return self.m_explanation[p_key] if len(p_key) else self.m_explanation
    def show_results(self, p_show_explanations=False):
        for key in self.m_result:
            print("=" * 80)
            print(key)
            if p_show_explanations:
                print(self.explanation(key))
            print(self.m_result[key])
    
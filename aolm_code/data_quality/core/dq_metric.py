# Author: Jonathan Armoza
# Created: February 15, 2022
# Purpose: Contains the abstract base class to be implemented by all 'Art of
#          Literary Modeling' data quality metrics


# Imports

# Standard libraries
from abc import ABC, abstractmethod     # Python abstract classes


# Classes

"""
    'DataQualityMetric' is an abstract base class for data quality metric
    classes. This abstraction is made so that metrics may have a standardized
    set of methods and properties so that they may be collected and acted upon
    uniformly across different sets of analyses.
"""
class DataQualityMetric(ABC):

    # Constructor

    def __init__(self, p_name, p_input):

        # 0. Save parameters
        self.m_name = p_name
        self.m_input = p_input

        # 1. Other class fields
        self.m_result = None

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

    # Required methods

    @abstractmethod
    def compute(self):
        pass

    @abstractmethod
    def output(self):
        pass
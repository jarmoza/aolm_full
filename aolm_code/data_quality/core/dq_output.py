# Author: Jonathan Armoza
# Created: June 11, 2024
# Purpose: Basic output module for data quality metrics

# Imports

# Custom
from dq_metric import DataQualityMetric


class DataQualityOutput:

    def __init__(self, p_evaluations):

        self.m_value = p_evaluations
        self.m_data_type = type(self.m_evaluations)        

    def __init__(self, p_parent_metric_id, p_value):
        
        self.m_parent_metric_id = p_parent_metric_id

        # Retrieves from master metric instance list
        self.m_parent_metric_type = DataQualityMetric.get_metric_type(p_parent_metric_id)
        self.m_value = p_value
        self.m_data_type = type(p_value)

    @property
    def data_type(self):
        return self.m_data_type
    @property
    def value(self):
        return self.m_value

class DataQualityOutputComparer:

    def __init__(self, p_outputs_list):

        self.m_outputs = p_outputs_list

    def make_comparisons(self):

        for index in len(self.m_outputs):
            for index2 in len(self.m_outputs):
                # Make comparison ignoring self comparison
                pass

    @property
    def comparisons(self):
        pass



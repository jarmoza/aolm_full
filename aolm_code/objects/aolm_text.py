# Author: Jonathan Armoza
# Created: September 24, 2024
# Purpose: Houses the base class for all Art of Literary Modeling text objects

# Imports

# Globals

# Classes

class AOLMText(object):
    
    def __init__(self, p_filepath, p_filetype):

        # 0. Save parameters
        self.m_filepath = p_filepath
        self.m_filetype = p_filetype

        self.m_body = None
        self.m_metadata = None
        
        self.m_text_lines = []

    @property
    def body(self):
        return self.m_body
    @property
    def filepath(self):
        return self.m_filepath
    @property
    def filetype(self):
        return self.m_filetype
    @property
    def metadata(self):
        return self.m_metadata
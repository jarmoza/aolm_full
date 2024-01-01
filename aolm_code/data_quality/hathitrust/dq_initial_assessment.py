from collections import defaultdict
import glob
import json
import os
import sys

from dq_initial_assessment_nyp import metadata_info
from htrc_ef_metadata_lens_nyp import AOLM_HTRCFeatureReader

class AOLM_DQProfile:
	
	def __init__(self, p_metadata_info):

		# Save fields
		self.m_metadata_filepath = p_metadata_info["path"]
		self.m_metadata_filenames = glob.glob(self.m_metadata_filepath + "*.json.bz2")
		self.m_metadata_datatype_schema = p_metadata_info["data_types"]["schema"]
		self.m_metadata_expectation_schema = p_metadata_info["expectations"]["schema"]
		self.m_dq_profile = {}

		# Initialize profile data
		self.__initialize_profile()

	def __initialize_profile(self):

		for key in self.m_metadata_datatype_schema:

			# Collections will be collections of collections (type of profile tallying occurs in post)
			if "list" in self.m_metadata_datatype_schema[key] or "dict" in self.m_metadata_datatype_schema[key]:
				self.m_dq_profile[key] = []
			# Unary fields can be tallied into a dict
			else:
				self.m_dq_profile[key] = defaultdict(int)

	# Helper function to read in metadata for data quality profiling
	def __read_metadata(self, p_filepath):

		# Create a feature reader
		fr = AOLM_HTRCFeatureReader([p_filepath])

		# Get metadata from the feature reader one volume at a time
		self.m_metadata = fr.get_next_volume_metadata()
		print "======================="
		print "Metadata for {0}".format(os.path.basename(p_filepath))
		print self.m_metadata
		print "======================="


	def output_profile(self, p_output_path, p_indent=4):

		with open(p_output_path, "w") as output_file:
			output_file.write(json.dumps(self.m_dq_profile, indent=p_indent, separators=(',', ': '), sort_keys=True))

	def profile_metadata(self):

		debug_index = 0
		for filename in self.m_metadata_filenames:		

			# Get ready to tally metadata
			self.__read_metadata(filename)

			print "Profiling {0}....".format(filename)

			# Go through the metadata schema and profile the actual metadata
			# (assumes unique metadata keys)
			for key in self.m_metadata_datatype_schema:

				# Profiling collection fields
				if "list" in self.m_metadata_datatype_schema[key]:
					self.profile_list_field(key)
				elif "dict" in self.m_metadata_datatype_schema[key]:
					self.profile_dict_field(key)
				# Profiling unary fields
				else:	
					if "str" in self.m_metadata_datatype_schema[key]:
						self.profile_unary_string_field(key)
					else:
						self.profile_unary_nonstring_field(key)

			print "Done file {0} of {1}".format(debug_index, len(self.m_metadata_filenames))
			debug_index += 1

	# Current implementation assumes single data type for dict values
	def profile_dict_field(self, p_dict_key):

		# Profile is a list of dicts
		self.m_dq_profile[p_dict_key].extend(self.m_metadata[p_dict_key])

	# Current implementation assumes single data type for lists
	def profile_list_field(self, p_list_key):

		# Profile is a list of lists
		self.m_dq_profile[p_list_key].extend(self.m_metadata[p_list_key])

	def profile_unary_nonstring_field(self, p_unary_key):

		# Profile is a dict of string values
		self.m_dq_profile[p_unary_key][str(self.m_metadata[p_unary_key])] += 1

	def profile_unary_string_field(self, p_unary_key):

		# Profile is a dict of string values
		self.m_dq_profile[p_unary_key][self.m_metadata[p_unary_key]] += 1


def main(p_args):

	output_path = "/Users/PeregrinePickle/Documents/Digital_Humanities/htrc_playground/data/ninec_tests/nyp_sandbox/nyp_dq_profile_test_subset.json"

	my_dq_profile = AOLM_DQProfile(metadata_info)

	my_dq_profile.profile_metadata()

	my_dq_profile.output_profile(output_path)


if "__main__" == __name__:
	main(sys.argv)
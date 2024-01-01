import glob
from htrc_features import FeatureReader
import re
import sys

# Paths
nyp_ef_filepath = "/Users/PeregrinePickle/htrc_data_files/nyp_ef_files_compressed/"
extracted_features_filepath = nyp_ef_filepath
output_filepath = "/Users/PeregrinePickle/Documents/Digital_Humanities/htrc_playground/data/ninec_tests/nyp_sandbox/"


class AOLM_HTRCFeatureReader:

	def __init__(self, p_ef_filenames):

		self.m_ef_filenames = p_ef_filenames
		self.m_file_index = 0
		self.m_at_first_file_index = True
		self.m_feature_reader = None

		self.__create_metadata_keys()

	def __create_metadata_keys(self):

		self.m_metadata_key_dict = {}
		for key in self.ef_fr_keys:
			self.m_metadata_key_dict[key] = self.frkey_to_metadatakey(key)

	def is_at_first_file(self):

		return self.m_at_first_file_index

	def get_metadata_values(self):

		# Get feature reader data for next volume
		return self.get_next_volume_metadata()

	def get_next_filename(self):

		next_filename = self.m_ef_filenames[self.m_file_index]
		print "Getting metadata for {0}....".format(next_filename)
		self.m_file_index += 1
		self.m_at_first_file_index = False
		if len(self.m_ef_filenames) == self.m_file_index:
			self.m_file_index = 0
			self.m_at_first_file_index = True
		return next_filename

	def get_next_volume_metadata(self):

		# Create a HTRC feature reader object
		self.m_feature_reader = FeatureReader(self.get_next_filename())

		metadata_values = {}
		for vol in self.m_feature_reader.volumes():
			for key in self.ef_fr_keys:

				# Skip page data
				if "_pages" == key:
					continue

				value = getattr(vol, key)

				# try:
				# 	metadata_values[self.m_metadata_key_dict[key]] = "\"" + str(value).replace("\"", "\'") + "\""
				# except:
				# 	metadata_values[self.m_metadata_key_dict[key]] = "\"" + str(sys.exc_info()[0]) + "\""

				try:
					metadata_values[self.m_metadata_key_dict[key]] = value
				except:
					metadata_values[self.m_metadata_key_dict[key]] = str(sys.exc_info()[0])


		return metadata_values

	def frkey_to_metadatakey(self, p_fr_key):

		# Get all instances of an underscore in the feature reader key
		underscores = [m.start() for m in re.finditer("_", p_fr_key)]

		# Camel case string to be altered and returned
		camel_case_str = list(p_fr_key)

		# Replace each instance of an underscore,lowercase with underscore,uppercase
		for index in underscores:
			camel_case_str[index + 1] = camel_case_str[index + 1].upper()
		camel_case_str = [ch for ch in camel_case_str if "_" != ch]

		return "".join(camel_case_str)
	
	ef_fr_keys = ['isbn', 'classification', 'bibliographic_format', 'source_institution_record_number', 
 		'page_count', 'hathitrust_record_number', '_schema', 'imprint', 'names', 
 		'rights_attributes', 'enumeration_chronology', 'id', 'volume_identifier', 
 		'title', 'schema_version', '_pages', 'type_of_resource', '_has_advanced', 'ht_bib_url',
 		'issuance', 'last_update_date', 'genre', 'pub_date', 'pub_place', 'language', 
 		'default_page_section', 'government_document', 'issn', 'lccn', 'handle_url', 
 		'access_profile', 'date_created', 'source_institution', 'oclc']


def main():

	print "Getting metadata from files in:" + extracted_features_filepath

	# Get all HTRC compressed EF filenames in this filepath
	extracted_features_filenames = glob.glob(extracted_features_filepath + "*.json.bz2")

	# Create a HTRC feature reader object
	fr = FeatureReader(extracted_features_filenames)

	# Output a csv with volume metadata
	index = 0
	with open(output_filepath + "nyp_ef_data_all.csv", "w") as output_file:
		
		# Write the csv header
		output_file.write(",".join(ef_metadata_keys) + "\n")

		for vol in fr.volumes():

			# print "Writing metadata for {0} with isbn {1}".format(vol.id, vol.isbn)

			# if 0 == index % 100:
			# 	debug_print("Written {0} records".format(index))
			# index += 1

			metadata_values = []
			for key in ef_metadata_keys:
				# Skip page data
				if "_pages" == key:
					continue

				value = getattr(vol, key)

				try:
					metadata_values.append("\"" + str(value).replace("\"", "\'") + "\"")
				except:
					metadata_values.append("\"" + str(sys.exc_info()[0]) + "\"")

			output_file.write(",".join(metadata_values) + "\n")

	# for vol in fr.volumes():
	# 	for key in ef_metadata_keys:
	# 		value = getattr(vol, key)
	# 		print "{0}: {1}".format(key, value)
	# 	break


	# # Get all HTRC decompressed EF filenames in this filepath
	# extracted_features_filenames = glob.glob(extracted_features_filepath + "*.bz2")

	# for vol in fr.volumes():
	# 	debug_print(vol.metadata)


if "__main__" == __name__:
	main()
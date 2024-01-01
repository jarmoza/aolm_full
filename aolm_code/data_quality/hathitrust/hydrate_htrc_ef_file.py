# My example: Metta Victoria Fuller Victor: https://en.wikipedia.org/wiki/Metta_Victoria_Fuller_Victor
# miun.adx6300,0001,001.json

# uc2.ark/-13960-t7hq3tv0w
# uc2.ark/-13960-t0zp4497z
# loc.ark/-13960-t6d22dg8q
# uc2.ark/-13960-t6542kn6k

# nyp.33433006830958
# njp.32101067486678
# nyp.33433082138706
# nyp.33433076042393
# nyp.33433082138755
# njp.32101017504109
# nyp.33433076041486
# nyp.33433074799408

import glob
from htrc_features import FeatureReader
import os
import pandas as pd
import sys

# Input and output paths
extracted_features_filepath = "/Users/PeregrinePickle/Desktop/victor_ef_files/bz2/"
output_filepath = "/Users/PeregrinePickle/Desktop/victor_ef_files/mallet_files/"

def main(p_args):

	# if 0 == len(p_args):
	# 	print "Script requires a filepath"
	# 	return

	# # Save filepath and format it
	# extracted_features_filepath = p_args[0]
	# if os.sep != p_args[len(p_args) - 1]:
	# 	extracted_features_filepath += os.sep
	# extracted_features_filepath += "*.json.bz2"

	# Get all HTRC compressed EF filenames in this filepath
	extracted_features_filenames = glob.glob(extracted_features_filepath + "*.json.bz2")

	# Create a HTRC feature reader object
	fr = FeatureReader(extracted_features_filenames)

	# Output a file for each page of each volume
	for vol in fr.volumes():
		
		print "Outputting pages for " + vol.id

		page_index = 0
		for page in vol:
			
			# Turn dataframe into dict of tokens
			page_dict = page.tokenlist(section="body", case=False, pos=False).to_dict()["count"]

			# Write tokens the number of times listed in the page dict (for bag of words output only)
			if len(page_dict.keys()) > 0:
				with open(output_filepath + vol.id + "_" + str(page_index) + ".txt", "w") as output_file:
					for key in page_dict:
						for token_count in range(page_dict[key]):
							try:
								output_file.write(key[2] + " ")
							except:
								continue

			# Increment index for the next page
			page_index += 1
			

if "__main__" == __name__:
	main(sys.argv)
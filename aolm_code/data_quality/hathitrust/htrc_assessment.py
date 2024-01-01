from collections import defaultdict
import glob
import os

from get_htrc_ef_file import id_to_rsync, rsync_ef_file

# Paths
g_htrc_bib_json_path = "/Users/PeregrinePickle/Documents/Digital_Humanities/htrc_playground/data/ninec_tests/bib_api_json/"

g_debug = False

def count_filename_prefixes():

	# Get file prefixes
	filename_prefixes = defaultdict(lambda: 0, {})
	for filename in glob.glob(g_htrc_bib_json_path + "*.json"):
		filename_prefixes[filename[filename.rfind("/") + 1:].split(".")[0]] += 1

	# Count and sort prefixes
	prefixes_sorted = []
	for prefix in filename_prefixes:
		prefixes_sorted.append((prefix, filename_prefixes[prefix]))
	prefixes_sorted = sorted(prefixes_sorted, key=lambda x: x[1], reverse=True)

	if g_debug:
		for prefix_tuple in prefixes_sorted:
			print "{0}: {1}".format(prefix_tuple[0], prefix_tuple[1])

	return prefixes_sorted

def get_filenames_with_prefix(p_prefix):

	# Get file prefixes
	filename_prefixes = defaultdict(lambda: [], {})
	for filename in glob.glob(g_htrc_bib_json_path + "*.json"):
		short_filename = filename[filename.rfind("/") + 1:]
		filename_prefixes[short_filename.split(".")[0]].append(short_filename)

	return None if 0 == len(filename_prefixes[p_prefix]) else filename_prefixes[p_prefix]



def main():

	# Retrieve filenames
	# my_filenames = get_filenames_with_prefix("nyp")
	# with open(os.getcwd() + "/nyp_filenames.csv", "w") as output_file:
	# 	for filename in my_filenames:
	# 		output_file.write(filename + "\n")

	ht_vol_ids = []
	with open(os.getcwd() + "/nyp_filenames.csv", "rU") as input_file:
		data = input_file.readlines()
		for line in data:
			ht_vol_ids.append(line.strip()[0:line.rfind(".")])

	# Find missing files
	# found_vol_ids = []
	# for filename in glob.glob("/Users/PeregrinePickle/Documents/Digital_Humanities/htrc_playground/data/ninec_tests/nyp_ef_files/" + "*.json.bz2"):
	# 	filename = filename[filename.rfind("/") + 1:]
	# 	filename = filename[0:filename.rfind(".")]
	# 	filename = filename[0:filename.rfind(".")]
	# 	found_vol_ids.append(filename)
	# ht_vol_ids = list(set(ht_vol_ids) - set(found_vol_ids))

	# Get filenames for download
	filenames = [id_to_rsync(vol_id) for vol_id in ht_vol_ids]

	# Retrieve EF files
	map(rsync_ef_file, filenames)

if "__main__" == __name__:
	main()
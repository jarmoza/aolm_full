import os
from subprocess import call

local_folder = os.getcwd()
tei_folder = local_folder + "/../tei/"
dc_url_list_filepath = local_folder + "/../" + "dickinson_correspondences_url_list.txt"


def main():

	# Write transformed urls to text file
	tei_urls = []
	with open(dc_url_list_filepath, "r") as output_file:
		data = output_file.readlines()
		for line in data:
			tei_urls.append(line.strip())

	# Get all tei files from the listed urls and store in tei folder
	for url in tei_urls:
		with open(tei_folder + os.path.basename(url), "w") as new_tei_file:
			response = call(["curl", url], stdout=new_tei_file)

if "__main__" == __name__:
	main()

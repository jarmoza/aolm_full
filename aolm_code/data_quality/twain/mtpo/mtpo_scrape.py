# Author: Jonathan Armoza
# Project: Art of Literary Modeling
# Date: September 5, 2019
# Purpose: Downloads known TEI XML files and other (meta)data from Mark Twain
# 		   Project Online (http://www.marktwainproject.org/)
# Credits: Terence Catapano of MTPO (assisted with file location and usage
# 		   rights determination, 2018-2019)
# Initial access date of files: September 5, 2019

# NOTE: Requires Python 3+

import argparse 			  # Terminal arguments
from itertools import chain
import os 					  # File/folder operations
import requests 			  # Download HTML files
from subprocess import call   # Curl files
from bs4 import BeautifulSoup # Parse HTML

from mtpo_commons import mtpo # Data about the Mark Twain Project TEI collection


# Possible choices of work types to download
# mtpo["work_types"] = ["autobio", "fiction"]
mtpo["work_types"] = ["autobio"]
# mtpo["work_types"] = ["autobio", "fiction", "letters", "reviews", "bios"]

# Translates work genre into MTPO site subfolder in 'xtf/tei'
mtpo["url_folder_dict"] = { work_type: None for work_type in mtpo["work_types"] }
mtpo["url_folder_dict"]["autobio"] = "works"
mtpo["url_folder_dict"]["fiction"] = "works"
mtpo["url_folder_dict"]["letters"] = "letters"
mtpo["url_folder_dict"]["reviews"] = "letters"

mtpo["landing_genre_dict"] = {
	"letters": ["letters"],
	# "writings": ["autobiographies", "fiction"]
	"writings": ["autobiographies"]
}

# Means of identifying resource URL
mtpo["resource_search_string"] = "/xtf/view?docId="

# Primary folders of TEI files on MTPO site
mtpo["urls"] = { "base": "http://www.marktwainproject.org/xtf/tei/" }
mtpo["urls"]["landings"] = {

	"letters": "http://www.marktwainproject.org/xtf/search?category=letters;rmode=landing_letters;style=mtp",
	"writings": "http://www.marktwainproject.org/landing_writings.shtml",
}
mtpo["urls"]["works"] = mtpo["urls"]["base"] + "works/"
mtpo["urls"]["letters"] = mtpo["urls"]["base"] + "letters/"


# Utility functions
def format_folder(p_folder):

	# Make sure os.sep is the last character of the given folder
	formatted_folder = p_folder
	if os.sep in formatted_folder:
		if os.sep != formatted_folder[len(formatted_folder) - 1]:
			formatted_folder += os.sep

	return formatted_folder

def work_type(p_filename):

	# Look for worktype of file listed in known files dictionary
	file_work_type = None
	print(mtpo["known_files"])
	for work_type in mtpo["known_files"]:
		if p_filename in mtpo["known_files"][work_type]:
			file_work_type = work_type
			break
			
	return file_work_type

# Primary functions
def make_output_folders(p_root_folder, p_work_types):

	# 1. Define data output folder possibilities
	mtpo["folders"] = { "root": p_root_folder + "mtpo" + os.sep }
	for work_type in p_work_types:
		mtpo["folders"][work_type] = mtpo["folders"]["root"] + work_type + os.sep

	# 2. Create output folders on disk, starting with the root
	if not os.path.exists(mtpo["folders"]["root"]):
		os.mkdir(mtpo["folders"]["root"])
	for folder_name in mtpo["folders"]:
		if "root" != folder_name:
			if not os.path.exists(mtpo["folders"][folder_name]):
				os.mkdir(mtpo["folders"][folder_name])

def scrape_and_build_file_urls(p_work_types, p_landing_pages=None):

	# Determine requested landing pages
	# requested_landing_pages = []
	# for work_type in p_work_types:

	if None == p_landing_pages:
		urls_by_landing = mtpo["urls"]["landings"]

	print(urls_by_landing)

	# Dictionary of urls by work type (or all if no landing pages given)
	# urls_by_worktype = { work_type: [] for work_type in mtpo["work_types"] }
	urls_by_worktype = { work_type: [] for work_type in p_work_types }

	# 1. Scrape given landing pages (or all if none given)
	for page in urls_by_landing:

		# A. Get full page
		page_html = requests.get(mtpo["urls"]["landings"][page])

		# B. Find urls of the form (http://www.marktwainproject.org/xtf/view?docId={folder}/MTDP10001.xml;style=work;brand=mtp)
		page_soup = BeautifulSoup(page_html.text, "html.parser")
		search_string = mtpo["resource_search_string"]
		relevant_anchor_tags = [tag for tag in page_soup.find_all("a") if "href" in tag.attrs and search_string in tag["href"]]

		# C. Transform scraped urls into TEI urls of the form (http://www.marktwainproject.org/xtf/tei/{folder}/MTDP10362.xml)
		for tag in relevant_anchor_tags:

			# i. Get query string from the url
			if "?" not in tag["href"]:
				continue
			query_string = tag["href"].split("?")[1]

			# ii. Form new url
			base_url = mtpo["urls"]["base"]
			folder_name = query_string.split("=")[1]
			folder_name = folder_name[0:folder_name.find("/")]
			filename = query_string.split("=")[1]
			filename = filename[filename.find("/")+1:]
			filename = filename[0:filename.find(";")]
			new_url = base_url + folder_name + os.sep + filename

			# iii. Save new url (sorted by work type)
			my_work_type = work_type(filename)
			if None != my_work_type and my_work_type in urls_by_worktype:
				urls_by_worktype[my_work_type].append(new_url)

	print("Finish scrape\n{0}".format(urls_by_worktype))

	return list(chain.from_iterable(urls_by_worktype.values()))

def curl_urls(p_urls, p_output_folder):

	# Get all tei files from the listed urls and store in tei folder
	for url in p_urls:
		with open(p_output_folder + os.path.basename(url), "w") as new_tei_file:
			response = call(["curl", url], stdout=new_tei_file)

def parse_arguments():

	# 1. Create the argument parser
	parser = argparse.ArgumentParser()

	# 2. Define MTPO Scraping Possibilities
	parser.add_argument("worktype",
						choices=["all"] + mtpo["work_types"],
						help="Type of work to retrieve from Mark Twain Project")
	parser.add_argument("-o", "--output", help="Folder to output requested files. Defaults to current folder.")

	# 3. Parse arguments passed in through the terminal
	arguments = parser.parse_args()

	# 4. Process arguments
	work_types = mtpo["work_types"] if "all" == arguments.worktype else [arguments.worktype]
	output = format_folder(arguments.output) if arguments.output else "." + os.sep

	return work_types, output


def main():

	# 0. Retrieve arguments from terminal
	work_types, output = parse_arguments()

	print("Work type: {0}\nOutput: {1}".format(work_types, output))

	# 1. Create a dict of URLs for resources to download
	urls_to_retrieve = scrape_and_build_file_urls(work_types)
	print(type(urls_to_retrieve))
	print(urls_to_retrieve)
	print(output)

	# 2. Download
	# curl_urls(urls_to_retrieve, mtpo["folders"]["autobiographies"])
	curl_urls(urls_to_retrieve, os.getcwd() + os.sep + "output" + os.sep)


if "__main__" == __name__:
	main()
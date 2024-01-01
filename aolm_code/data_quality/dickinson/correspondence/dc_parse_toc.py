# Author: Jonathan Armoza
# Project: Art of Literary Modeling
# Date: May 23, 2019

import os
from bs4 import BeautifulSoup

local_folder = os.getcwd()
dc_toc_filepath = local_folder + "/../" + "dickinson_correspondences_toc_raw.html"
dc_url_list_filepath = local_folder + "/../" + "dickinson_correspondences_url_list.txt"

root_url = "https://rotunda.upress.virginia.edu"


def main():
 
	# Read table of contents html and transform into beautiful soup
	with open(dc_toc_filepath, "r") as dc_file:
		dc_soup = BeautifulSoup(dc_file.read(), "html.parser")

	# Find all urls and transform them into TEI urls
	tei_urls = []
	table_rows = dc_soup.find_all("tr")
	for row in table_rows:
		cell = row.find("td")
		if cell:
			href = cell.find("a")["href"]
			transformed_url = root_url + href.replace("display.xqy?doc", "showxml.xqy?filename")
			transformed_url = transformed_url[0:transformed_url.find("&")]
			tei_urls.append(transformed_url)
	
	# Write transformed urls to text file
	with open(dc_url_list_filepath, "w") as output_file:
		for url in tei_urls:
			output_file.write(url + "\n")

if "__main__" == __name__:
	main()



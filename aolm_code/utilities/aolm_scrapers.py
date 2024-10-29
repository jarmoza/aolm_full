# Author: Jonathan Armoza
# Created: October 23, 2024
# Purpose: Contains various web scraping functions for the Art of Literary Modeling

def read_mtpo_huckleberry_finn_file(p_file_contents):
    

def get_mtpo_huckleberryfinn():

    # 0. URLs to scrape
    url_list = [

    ]    

    # 1. Download files to scrape
    file_contents = { url_path: download_file(url_path) for url_path in url_list }

    # 2. Perform the reading function on each file, separating out metadata and body text
    separated_file_contents = { url_path: read_mtpo_huckleberryfinn_file(file_contents[url_path]) for url_path in file_contents }



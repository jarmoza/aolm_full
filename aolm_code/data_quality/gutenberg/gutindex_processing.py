import os

# Global variables

'''
Listing format: title (str), ebook_no (str), metadata(dict)
Metadata format: { name: value,... }
'''
listings = []

'''
List of beginnings of known metadata lines in the listings section 
of the GUTINDEX.ALL file 
'''
metadata_linestarts = [
	"GUTINDEX.",
	"Gutenberg collection between",
	"beginning with eBook",
	"****", 
	"~ ~ ~ ~", 
	"TITLE and AUTHOR"
]

# Utility functions
def check_linestart(p_line, p_possible_starts):
	
	for start in p_possible_starts:
		if p_line.strip().startswith(start):
			return True
	
	return False


def contains_ebookno(p_line):

	# Splitting by doublespace (should mostly apply to all listing lines)
	line_parts = p_line.strip().split("  ")

	for index in range(1, len(line_parts)):

		if 0 != len(line_parts[index].strip()) and \
			    str.isdigit(line_parts[index].strip()):
			return True

	return False
			

def get_listingdata(p_line):

	# Splitting by doublespace (should mostly apply to all listing lines)
	line_parts = p_line.strip().split("  ")

	# Determine title, author (if available), and ebook number
	#   - Title should be the first part from the line split
	#   - Author(s) may exist after a ', by' within the title string
	#   - Ebook number will be separated by a varying number of spaces from the 
	#   other two fields

	authors = None
	title = line_parts[0]
	ebook_no = ""

	if ", by" in line_parts[0]:
		by_parts = line_parts[0].split(", by")
		title = by_parts[0].strip()
		authors = [by_parts[index].strip() for index in range(1, len(by_parts))]

	# Looking for the ebook number (not the first part or blank parts from the split)
	for index in range(1, len(line_parts)):
		if 0 == len(line_parts[index]):
			continue
		elif str.isdigit(line_parts[index]): 
			ebook_no = line_parts[index]
			break

	return title, authors, ebook_no


def get_metadata(p_line):

	cleaned_line = p_line.replace("[","").replace("]","")
	colon_index = p_line.find(":")
	
	return p_line[0:colon_index].strip(), p_line[colon_index+1:].strip()

def is_metadataline(p_line):

	return check_linestart(p_line, metadata_linestarts)


def print_line(p_linenumber, p_text):
	
	print "[{0}]: {1}".format(p_linenumber, p_text.strip())


# Primary functions
def gather_metadata():

	for listing in listings:

		for key in listing:
			print "{0}: {1}".format(key, listing[key])
		break


def process_index_file(p_filepath):

	line_counter = 1

	# Debug for metadata lines
	# with open(p_filepath, "rU") as index_file:
	# 	listing_lines = index_file.readlines()
	# 	for line in listing_lines:
	# 		if check_linestart(line, metadata_linestarts):
	# 			print_line(line_counter, line)
	# 		line_counter += 1

	with open(p_filepath, "rU") as index_file:

		listing_lines = index_file.readlines()

		current_listing = None
		
		for line in listing_lines:

			cleaned_line = line.strip()

			# print_line(line_counter, cleaned_line)

			# Skip blank or known metadata lines
			if 0 == len(cleaned_line) or is_metadataline(cleaned_line):
			   	line_counter += 1
			   	continue

			# Look for metadata lines for the current listing
			elif cleaned_line.startswith("["):

				meta_key, meta_value = get_metadata(cleaned_line)
			   	try:
					current_listing["metadata"][meta_key] = meta_value
				except: 
					current_listing["metadata"] = {}
					current_listing["metadata"][meta_key] = meta_value

				current_listing["original_line"].append(cleaned_line)


			# This is a new listing if the line contains an ebook number
			elif contains_ebookno(cleaned_line):

				# Save the previous listing
				if None != current_listing:
					listings.append(current_listing)

				title, author, ebook_no = get_listingdata(cleaned_line)
				current_listing = {
					"title": title,
					"author": author, 
					"ebook_no": ebook_no,
					"original_line": [cleaned_line]
				}

			# Otherwise this is a (more rare) extended author "by" line
			else:
				current_listing["author"] = cleaned_line.replace("by", "").strip()
				current_listing["original_line"].append(cleaned_line)
				

			# Keep track of the file line count
			line_counter += 1


# Main code
def main():

	data_folder = os.getcwd() + os.sep + "data" + os.sep + "indices" + os.sep
	index_filename = "LISTINGS.GUTINDEX.ALL"

	process_index_file(data_folder + index_filename)

	# print "Listings: {0}".format(len(listings))

	metadata_dict = gather_metadata()


if __name__ == "__main__":
	main()
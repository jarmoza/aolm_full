import csv
import glob
import json

# Info
# Stats for pub dates: {'no_pub_dates': 807, 'mt1_pub_dates': 0, 'one_pub_date': 312671}

paths = {}
paths["htrc_data"] = "/Users/PeregrinePickle/Documents/Digital_Humanities/htrc_playground/data/"
paths["bib_api_json"] = paths["htrc_data"] + "ninec_tests/bib_api_json/"
paths["output"] = "/Users/PeregrinePickle/Documents/School/New York University/Dissertation/Scripts/htrc/output/"


# Build table
def build_table():
	
	bib_api_json_files = glob.glob(paths["bib_api_json"] + "*.json")

	# Build out all rows (with null average)
	table_rows = []
	for json_filename in bib_api_json_files:
		with open(json_filename, "rU") as json_file:

			json_data = json.loads(json_file.read())
			first_record = json_data["records"][json_data["records"].keys()[0]]

			# Only look at title lengths for nineteenth century pubdate volumes
			if len(first_record["publishDates"]) and is_ninec_date(first_record["publishDates"][0]):
				table_rows.append([int(first_record["publishDates"][0]), get_titles_length(first_record["titles"]), 0])

	# Calculate year title length averages and insert them into the table
	years = {}
	for row in table_rows:
		y = str(row[0])
		if y not in years:
			years[y] = { "count": 1, "length_total": row[1] }
		else:
			years[y]["count"] += 1
			years[y]["length_total"] += row[1]
	title_length_averages = {}
	for y in years:
		title_length_averages[y] = years[y]["length_total"] / float(years[y]["count"])
	for row in table_rows:
		row[2] = title_length_averages[str(row[0])]

	return table_rows

def get_oldest_year(p_json_years):

	oldest_year = 2200
	for y in p_json_years:
		if int(y) < oldest_year:
			oldest_year = int(y)
	return oldest_year

def get_titles_length(p_json_titles):

	length = 0
	for t in p_json_titles:
		parts = t.split(" ")
		for p in parts:
			length += len(translate_non_alphanumerics(p.strip(), None))
	return length

def is_ninec_date(p_year):

	return int(p_year) >= 1800 and int(p_year) < 1900

# From https://stackoverflow.com/questions/1324067/how-do-i-get-str-translate-to-work-with-unicode-strings
def translate_non_alphanumerics(to_translate, translate_to=u'_'):
    not_letters_or_digits = u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
    translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits)
    return to_translate.translate(translate_table)


# Read in features
feature_names = ["oldest_publishDate", "title_length", "average_title_length"]
table_rows = build_table()
table_rows.insert(0, feature_names)

# Output features to csv
with open(paths["output"] + "bibapi_pubdates_titlelens.csv", "w") as output_file:
	csv.writer(output_file).writerows(table_rows)


		



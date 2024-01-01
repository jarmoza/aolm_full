import glob
import json
import os
import re
import sys
from bs4 import BeautifulSoup
import bs4
from collections import Counter

# Globals

tei_folder = os.getcwd() + "/../tei/"
tei_soups = {}

found_search = False
relationship_str_map = {
	
	"Editing": ["editor:"],
	"Encoding": ["Encoder:", "File encoded by", "encoder:", "encode:"],
	"Header Metadata": ["DTD and header created by", "DTD created by"],
	"Images By": ["Digital image created by the", "Digital imagecreated by the"],
	"Project": ["Project coordinated by"],
	"Proofing": ["File proofed by", "proofreader:"],
	"Transcription": ["Machine-readable text created by"],
	"Unknown": [":"]
}

def get_soup(p_xml_filepath):

	dc_file = open(p_xml_filepath, "r")
	return BeautifulSoup(dc_file.read(), "html.parser")

def read_search_json(p_json_filepath):

	with open(p_json_filepath, "r") as json_file:
		tei_json = json.load(json_file.read())

	print tei_json

def regularize_entity_name(p_name):

	entity = re.sub(r"[\s\n\t]+", " ", p_name)
	if "," in entity:
		entity = entity.split(",")
		entity = entity[1].strip() + " " + entity[0]
	return entity

def entity_responsible(p_tei_soup, p_contents_search=None):

	people = []

	resp_statements = p_tei_soup.find_all("resp")
	global found_search
	found_search = False
	for resp in resp_statements:
		if p_contents_search:
			for c in resp.contents:
				if c.find(p_contents_search) >= 0:
					found_search = True
					names = resp.find_all("name")
					for n in names:
						people.append(regularize_entity_name(n["reg"]))
					# people.append(regularize_entity_name(resp.find("name")["reg"]))
		else:
			names = resp.find_all("name")
			for n in names:
				people.append(regularize_entity_name(n["reg"]))

	return list(set(people))

def resp_statements(p_tei_soup):

	resp_statements = p_tei_soup.find_all("resp")
	for resp in resp_statements:
		print "\tContents: {0}\n\t{1}".format(resp.contents, resp.elements)
	print "\n"

def tally_entities_involved(p_tei_soup, p_entities_involved, p_people_involved, p_institutions_involved):

	names = p_tei_soup.find_all("name")
	for n in names:
		
		# Get name
		regularized_name = n["reg"].strip() if n.has_attr("reg") else n.contents[0].strip()
		regularized_name = regularize_entity_name(regularized_name)

		# Tally entities
		tally_entities_involved_helper(p_entities_involved, n.find_parent("resp"), regularized_name)

		if n.has_attr("type"):

			# Tally people
			if "person" == n["type"]:
				tally_entities_involved_helper(p_people_involved, n.find_parent("resp"), regularized_name)
			# Tally institutionsc
			elif "org" == n["type"]:
				tally_entities_involved_helper(p_institutions_involved, n.find_parent("resp"), regularized_name)

def tally_entities_involved_helper(p_involved_collection, p_tag, p_regularized_name):

	if p_regularized_name not in p_involved_collection:
		p_involved_collection[p_regularized_name] = { "count": 1, "relationships": { } }
	else:
		p_involved_collection[p_regularized_name]["count"] += 1

	if p_tag:
		if len(p_tag.contents) and not isinstance(p_tag.contents[0], bs4.element.Tag):
			regularized_contents = p_tag.contents[0].strip()
			if len(regularized_contents):
				regularized_contents = regularize_entity_name(regularized_contents)
				if regularized_contents not in p_involved_collection[p_regularized_name]["relationships"]:
					p_involved_collection[p_regularized_name]["relationships"][regularized_contents] = 1
				else:
					p_involved_collection[p_regularized_name]["relationships"][regularized_contents] += 1

def print_relationships_of_entities_involved(p_involved_collection, p_print_blank_relationships=True):

	for i in p_involved_collection:
		relationship_list = sorted([(relationship, p_involved_collection[i]["relationships"][relationship]) \
								   for relationship in p_involved_collection[i]["relationships"]],\
							 	   key=lambda x: x[1],\
							 	   reverse=True)
		if len(relationship_list) > 0 or p_print_blank_relationships:
			print "========================\n" + i + "\n"
			for relationship_tuple in relationship_list:
				print "\t{0}: {1}".format(relationship_tuple[0], relationship_tuple[1])

def print_types_of_relationships_by_entity(p_involved_collection):

	relationship_groups = {}
	for key in relationship_str_map:
		relationship_groups[key] = []

	print p_involved_collection

	for entity in p_involved_collection:
		for relationship in p_involved_collection[entity]["relationships"]:
			for r_type in relationship_str_map:
				if relationship in relationship_str_map[r_type]:
					relationship_groups[r_type].extend([entity] * p_involved_collection[entity]["relationships"][relationship])

	for r_type in relationship_groups:
		print "{0} ================\n".format(r_type)
		counted_entities = Counter(relationship_groups[r_type])
		for entity in counted_entities:
			print "\t{0} ({1})".format(entity, counted_entities[entity])


def main(p_args):

	file_responsibility = {}
	entities_involved = {}
	people_involved = {}
	institutions_involved = {}

	# 1. Load soup instances for each tei file
	for tei_filename in glob.glob(tei_folder + "*.xml"):

		base_filename = os.path.basename(tei_filename)
		tei_soups[base_filename] = get_soup(tei_filename)
		
		# Save people responsible for each file
		# file_responsibility[base_filename] = entity_responsible(tei_soups[base_filename], "Machine-readable text created by")
		file_responsibility[base_filename] = entity_responsible(tei_soups[base_filename],\
																"DTD and header created by")
		tally_entities_involved(tei_soups[base_filename], entities_involved, people_involved, institutions_involved)

	# print_relationships_of_entities_involved(entities_involved)
	# print_relationships_of_entities_involved(people_involved, False)
	# print_relationships_of_entities_involved(institutions_involved, False)

	print_types_of_relationships_by_entity(entities_involved)
	# print_types_of_relationships_by_entity(people_involved)
	# print_types_of_relationships_by_entity(institutions_involved)
	
	# 2. Reach search config json file
	
	# people_responsiblity = {}
	# for base_filename in file_responsibility:
	# 	for person in file_responsibility[base_filename]:
	# 		if person not in people_responsiblity:
	# 			people_responsiblity[person] = 1
	# 		else:
	# 			people_responsiblity[person] += 1

	# for entity in people_responsiblity:
	# 	print "{0}: {1}".format(entity, people_responsiblity[entity])

if "__main__" == __name__:

	main(sys.argv[1:])
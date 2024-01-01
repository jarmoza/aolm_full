import json

def main():

	filepath = "/Users/PeregrinePickle/Documents/Digital_Humanities/htrc_playground/data/ninec_tests/nyp_sandbox/"
	input_filename = "nyp_dq_profile.json"
	output_filename = "nyp_dq_profile_fixed.json"
	with open(filepath + input_filename, "w") as input_file:
		my_json = json.loads(input_file.read())
	for key in my_json:
		pass

if "__main__" == __name__:
	main()

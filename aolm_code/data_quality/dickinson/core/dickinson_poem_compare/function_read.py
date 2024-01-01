# Imports

# Built-ins
import glob
import os

def main():

	# 0. All function names
	function_names = []

	# 0. All function names in each script file
	functions_by_file = {}

	# 1. Read all script files in the current working folder
	for filepath in glob.glob(os.getcwd() + os.sep + "*.py"):

		with open(filepath, "r") as script_file:

			# A. New function list for this script file
			functions_by_file[os.path.basename(filepath)] = []
			
			# B. Read all lines from the script
			script_lines = script_file.readlines()
			
			for line in script_lines:
				
				clean_line = line.strip()
				
				# I. Look for function lines
				if "def" == clean_line[0:3]:

					# a. Save function name
					fn_name = clean_line[4:].strip()
					fn_name = fn_name[0:fn_name.find("(")]
					function_names.append(fn_name)
					functions_by_file[os.path.basename(filepath)].append(fn_name)


	# 2. Create a set of all function names in the scripts
	function_names = sorted(list(set(function_names)))

	# 3. Output
	# for fn_name in function_names:
	# 	print(fn_name)
	for filename in functions_by_file:
		print(filename + ":")
		for script_file in functions_by_file[filename]:
			print("\t" + script_file)


if "__main__" == __name__:
	main()
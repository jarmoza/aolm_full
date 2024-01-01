import csv
import glob
import os

from sklearn import svm

# Data folders
input_folder = os.getcwd() + "{0}..{0}data{0}input{0}".format(os.sep)
tei_folder = input_folder + "tei" + os.sep
txt_folder = input_folder + "txt" + os.sep
reference_folder = input_folder + "reference" + os.sep

# Fascicle/Set reference file
reference_file = "dickinson_poem_list.csv"
reference_keys = "First Line (often used as title),F/S[2],1st,1stS.P,Collect,J#[3],Fr#[4]".split(",")


def gather_poems():

	poems = []

	with open(reference_folder + reference_file, "rU") as ref_file:
		
		reader = csv.DictReader(ref_file)
		for row in reader:			

			# Fields from csv reference file
			first_line = row[reference_keys[0]]
			fs_numbers = row[reference_keys[1]]
			first_pub_year = row[reference_keys[2]]
			first_pub_ps_numbers = row[reference_keys[3]]
			bianchi_ps_numbers = row[reference_keys[4]]
			johnson_number = row[reference_keys[5]]
			franklin_number = row[reference_keys[6]]

			# Create a new poem object
			poem = DickinsonPoem(first_line, fs_numbers, first_pub_year, first_pub_ps_numbers, bianchi_ps_numbers, johnson_number, franklin_number)

			# Add poem to collection
			poems.append(poem)

	return poems	


class DickinsonPoem:

	def __init__(
		self, p_first_line, p_fs_numbers, p_first_publication_year, p_firstpub_ps_numbers, 
		p_bianchi_ps_numbers, p_johnson_number, p_franklin_number):

		# First line
		self.m_first_line = p_first_line

		# Fascicle/Set numbers
		self.m_fs_numbers = None
		if len(p_fs_numbers):
			self.m_fs_numbers = { "fs": "", "leaf": "", "order": "" }
			fs_parts = p_fs_numbers.split(".")
			self.m_fs_numbers["fs"] = fs_parts[0]
			self.m_fs_numbers["leaf"] = fs_parts[1]
			self.m_fs_numbers["order"] = fs_parts[2]

		# First year of publication within the Todd & Bianchi volumes of 1890-1945
		self.m_first_publication_year = p_first_publication_year

		# Section and poem number from first publication
		self.m_firstpub_numbers = None
		if len(p_firstpub_ps_numbers):
			self.m_firstpub_numbers = { "section": "", "poem": "" }
			ps_parts = p_firstpub_ps_numbers.split(".")
			self.m_firstpub_numbers["section"] = ps_parts[0]
			if len(ps_parts) > 1:
				self.m_firstpub_numbers["poem"] = ps_parts[1]

		# Section and Poem number in the Bianchi collections of 1924-1937 
		self.m_bianchi_ps_numbers = None
		if len(p_bianchi_ps_numbers):
			self.m_bianchi_ps_numbers = { "section": "", "poem": "" }
			ps_parts = p_bianchi_ps_numbers.split(".")
			self.m_bianchi_ps_numbers["section"] = ps_parts[0]
			if len(ps_parts) > 1:
				self.m_bianchi_ps_numbers["poem"] = ps_parts[1]

		# Number assigned by Thomas H. Johnson in his variorum edition of 1955
		# (Numbering represents Johnson's judgment of chronology.)
		self.m_johnson_number = p_johnson_number

		# Number assigned by R. W. Franklin in his variorum edition of 1998
		# (Numbering represents Franklin's judgment of chronology.)
		self.m_franklin_number = p_franklin_number

	# Getters
	def first_line(self):
		return self.m_first_line
	def fs_number(self):
		return None if not self.m_fs_numbers else self.m_fs_numbers["fs"]
	def fs_leaf(self):
		return None if not self.m_fs_numbers else self.m_fs_numbers["fs"]
	def fs_order(self):
		return None if not self.m_fs_numbers else self.m_fs_numbers["fs"]
	def first_publication_year(self):
		return self.m_first_publication_year	
	def firstpub_section(self):
		return self.m_firstpub_numbers["section"]
	def firstpub_section(self):
		return self.m_firstpub_numbers["poem"]
	def bianchi_section(self):
		return self.m_bianchi_numbers["section"]
	def bianchi_section(self):
		return self.m_bianchi_numbers["poem"]
	def johnson_number(self):
		return self.m_johnson_number
	def franklin_number(self):
		return self.m_franklin_number							


def main():

	# Build a list of poem objects in memory
	dickinson_poems = gather_poems()


if "__main__" == __name__:
	main()
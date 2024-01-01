from collections import Counter
import glob
import os

from dc_edctext import EDCText

def main():

	# broken_filepath = os.getcwd() + "{0}..{0}tei{0}broken_xml{0}".format(os.sep)
	# broken_filename = "DEAmsEDCTWHbpl23.1b_amended.xml"
	# broken_text = EDCText(broken_filepath + broken_filename)

	edc_texts = []
	ea_types = []
	for tei_filepath in glob.glob(EDCText.default_tei_filepath + "*.xml"):
		edc_texts.append(EDCText(tei_filepath))
		ea_types.append(edc_texts[len(edc_texts) - 1].editor_assigned_type)
		# print("==============================================================")
		# edc_texts[len(edc_texts) - 1].stats()
	print(Counter(ea_types))

	# broken_text.stats()

if "__main__" == __name__:
	main()
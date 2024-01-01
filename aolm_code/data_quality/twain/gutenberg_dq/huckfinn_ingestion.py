# Author: Jonathan Armoza
# Creation date: October 9, 2021
# Purpose: Iterative look at how text cleaning processes affect data quality of texts,
# 		   Example case here is The Adventures of Huckleberry Finn by Mark Twain

# Project Gutenberg links
# Folder: https://www.gutenberg.org/files/76/
# Latest text release: https://www.gutenberg.org/files/76/76-0.txt
# Older releases: 
# https://www.gutenberg.org/files/76/old/2016-08-17-76-0.zip
# https://www.gutenberg.org/files/76/old/2011-05-03-76.zip

# Imports

# Built-ins
from collections import OrderedDict
import os

# Custom
from gutenberg_dq import ProjectGutenbergText


# Globals

# Input/output paths
paths = {
	
	"input": "{0}{1}data{1}input{1}".format(os.getcwd(), os.sep),
	"output": "{0}{1}data{1}output{1}".format(os.getcwd(), os.sep)
}
paths["2021-02-21"] = "2021-02-21_HuckFinn.txt"
paths["2016-08-17"] = "2016-08-17_HuckFinn.txt"
paths["2011-05-03"] = "2011-05-03_HuckFinn.txt"

# Text file components
file_components = OrderedDict({

	"GUTENBERG_header": [
		"The Project Gutenberg eBook of Adventures of Huckleberry Finn, by Mark Twain (Samuel Clemens)",
		"*** START OF THE PROJECT GUTENBERG EBOOK HUCKLEBERRY FINN ***"
	],

	"HUCKLEBERRYFINN_FRONTMATTER_titlepage": [
		"ADVENTURES",
		"Complete"
	],

	"HUCKLEBERRYFINN_FRONTMATTER_tableofcontents": [
		"CONTENTS.",
		"Finn."
	],

	"HUCKLEBERRYINN_FRONTMATTER_illustrations": [
		"ILLUSTRATIONS.",
		"Yours Truly"
	],

	"HUCKLEBERRYFINN_FRONTMATTER_explanatory": [
		"EXPLANATORY",
		"THE AUTHOR."
	],

	"HUCKLEBERRYFINN_BODY_titleandsetting": [
		"HUCKLEBERRY FINN",
		"Scene: The Mississippi Valley Time: Forty to fifty years ago"
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER I.": [

		"You don't know about me without you have read a book by the name of The",
		"there was Tom Sawyer waiting for me.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER II.": [

		"We went tiptoeing along a path amongst the trees back towards the end of",
		"dog-tired.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER III.": [

		"Well, I got a good going-over in the morning from old Miss Watson on",
		"the marks of a Sunday-school.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER IV.": [

		"Well, three or four months run along, and it was well into the winter",
		"own self!",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER V.": [

		"I had shut the door to. Then I turned around and there he was. I used",
		"the old man with a shotgun, maybe, but he didn't know no other way.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER VI.": [

		"Well, pretty soon the old man was up and around again, and then he went",
		"drag along.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER VII.": [

		"“Git up! What you 'bout?”",
		"laid down for a nap before breakfast.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER VIII.": [

		"The sun was up so high when I waked that I judged it was after eight",
		"eight hund'd dollars. I wisht I had de money, I wouldn' want no mo'.”",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER IX.": [

		"I wanted to go and look at a place right about the middle of the island",
		"hadn't no accidents and didn't see nobody. We got home all safe.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER X.": [

		"After breakfast I wanted to talk about the dead man and guess out how he",
		"was a girl.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XI.": [

		"“Come in,” says the woman, and I did. She says:  “Take a cheer.”",
		"word.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XII.": [

		"It must a been close on to one o'clock when we got below the island at",
		"loose en gone I--en here we is!”",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XIII.": [

		"Well, I catched my breath and most fainted. Shut up on a wreck with",
		"in and slept like dead people.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XIV.": [

		"By and by, when we got up, we turned over the truck the gang had stole",
		"So I quit.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XV.": [

		"We judged that three nights more would fetch us to Cairo, at the bottom",
		"wouldn't done that one if I'd a knowed it would make him feel that way.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XVI.": [

		"We slept most all day, and started out at night, a little ways behind a",
		"and barking at me, and I knowed better than to move another peg.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XVII.": [

		"In about a minute somebody spoke out of a window without putting his",
		"And warn't the cooking good, and just bushels of it too!",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XVIII.": [

		"Col. Grangerford was a gentleman, you see. He was a gentleman all",
		"raft don't. You feel mighty free and easy and comfortable on a raft.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XIX.": [

		"Two or three days and nights went by; I reckon I might say they swum by,",
		"have their own way.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XX.": [

		"They asked us considerable many questions; wanted to know what we",
		"had so much trouble, he'd forgot it.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXI.": [

		"It was after sun-up now, but we went right on and didn't tie up. The",
		"snatching down every clothes-line they come to to do the hanging with.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXII.": [

		"They swarmed up towards Sherburn's house, a-whooping and raging like",
		"“There,” says he, “if that line don’t fetch them, I dont know Arkansaw!”",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXIII.": [

		"Well, all day him and the king was hard at it, rigging up a stage and",
		"deef en dumb--en I'd ben a-treat'n her so!”",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXIV.": [

		"Next day, towards night, we laid up under a little willow towhead out in",
		"race.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXV.": [

		"The news was all over town in two minutes, and you could see the people",
		"was a prime good hit.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXVI.": [

		"Well, when they was all gone the king he asks Mary Jane how they was off",
		"begun yet; and then I slipped down the ladder.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXVII.": [

		"I crept to their doors and listened; they was snoring. So I tiptoed",
		"done the niggers no harm by it.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXVIII.": [

		"By and by it was getting-up time. So I come down the ladder and started",
		"Peter Wilks--and you pays your money and you takes your choice!”",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXIX.": [

		"They was fetching a very nice-looking old gentleman along, and a",
		"all I could do to keep from crying.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXX.": [

		"When they got aboard the king went for me, and shook me by the collar,",
		"to snoring we had a long gabble, and I told Jim everything.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXXI.": [

		"We dasn't stop again at any town for days and days; kept right along",
		"wanted to of them, and wanted to get entirely shut of them.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXXII.": [

		"When I got there it was all still and Sunday-like, and hot and sunshiny;",
		"I druther he wouldn't take no trouble about me.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXXIII.": [

		"So I started for town in the wagon, and when I was half-way I see a",
		"ain't no good, nohow. Tom Sawyer he says the same.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXXIV.": [

		"We stopped talking, and got to thinking. By and by Tom says:",
		"around then.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXXV.": [

		"It would be most an hour yet till breakfast, so we left and struck down",
		"smouch the knives--three of them.” So I done it.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXXVI.": [

		"As soon as we reckoned everybody was asleep that night we went down the",
		"dollars, I wouldn't.”",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXXVII.": [

		"That was all fixed. So then we went away and went to the rubbage-pile",
		"window-hole.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXXVIII.": [

		"Making them pens was a distressid tough job, and so was the saw; and Jim",
		"behave so no more, and then me and Tom shoved for bed.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XXXIX.": [

		"In the morning we went up to the village and bought a wire rat-trap and",
		"any reward but to know I have done the right thing. _Unknown Friend._",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XL.": [

		"We was feeling pretty good after breakfast, and took my canoe and went",
		"see the doctor coming till he was gone again.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XLI.": [

		"The doctor was an old man; a very nice, kind-looking old man when I got",
		"and her old gray head was resting on her hand, and she was asleep.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER XLII.": [

		"The old man was uptown again before breakfast, but couldn't get no",
		"was just as safe to not to. So I never said nothing.",
	],

	"HUCKLEBERRYFINN_BODY_CHAPTER THE LAST": [

		"The first time I catched Tom private I asked him what was his idea, time",
		"THE END. YOURS TRULY, _HUCK FINN_.",
	],

	"GUTENBERG_footer": [
		"*** END OF THE PROJECT GUTENBERG EBOOK HUCKLEBERRY FINN ***",
		"trademark license, especially commercial redistribution."
	],

	"GUTENBERG_license": [
		"START: FULL LICENSE",
		"subscribe to our email newsletter to hear about new eBooks."
	]

})


# Classes

# Project Gutenberg child class for Huckleberry Finn
class HuckleberryFinn(ProjectGutenbergText):
	
	def __init__(self, p_filepath, p_file_components):

		# 1. Call base constructor to read in file and its components
		super().__init__(p_filepath, p_file_components, self.__read_components)

	def __read_components(self):

		# 1. Save short reference to text file lines
		lines = self.m_raw_text

		# 2. Read in each component based on its start and end line
		index = 0
		start_reading = False
		for key in self.m_components:

			# A. Read in the components' lines
			component_lines = []
			for index in range(index, len(lines) - 1):

				if self.m_components[key][1] == lines[index].strip():
					component_lines.append(lines[index])
					break
				elif self.m_components[key][0] == lines[index].strip():
					start_reading = True
				
				if start_reading:
					component_lines.append(lines[index])

			# B. Add the text body to the component entry
			self.m_components[key].append("".join(component_lines))
	
	@property
	def chapters(self):
		return super().components

def main():

	huckfinn = HuckleberryFinn(paths["input"] + paths["2021-02-21"],
		file_components)

	print(huckfinn.m_components)

if "__main__" == __name__:
	main()
